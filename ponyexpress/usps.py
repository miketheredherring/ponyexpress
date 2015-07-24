import HTMLParser
from exceptions import TypeError

from ponyexpress.address import AddressValidationResponse, Address
from ponyexpress.config import XML_RESPONSE
from ponyexpress.courier import BaseCourier
from ponyexpress.rates import Package, RateCalculation, RateCalculationResponse
from ponyexpress.tracking import TrackingResponse, TrackingEvent


# USPSTracking is a class which is able to interface with the USPS Package Tracking API
# The user will provide a tracking number, and then can query the various aspects
class USPSCourier(BaseCourier):
    def __init__(self, username, password=''):
        # Call super
        super(USPSCourier, self).__init__(username, password)

        # Production URL
        self.tracking_endpoint = 'http://production.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML=' + \
            '<TrackFieldRequest USERID="{username}">' + \
                '<TrackID ID="{tracking_id}"></TrackID>' + \
            '</TrackFieldRequest>'
        self.address_validation_endpoint = 'http://production.shippingapis.com/ShippingAPI.dll?API=Verify&XML=' + \
            '<AddressValidateRequest USERID="{username}">' + \
                '<IncludeOptionalElements>true</IncludeOptionalElements>' + \
                '<ReturnCarrierRoute>true</ReturnCarrierRoute>' + \
                '<Address ID="0">' + \
                    '<FirmName>{name}</FirmName>' + \
                    '<Address1>{address_1}</Address1>' + \
                    '<Address2>{address_2}</Address2>' + \
                    '<City>{city}</City>' + \
                    '<State>{state}</State>' + \
                    '<Zip5>{zip5}</Zip5>' + \
                    '<Zip4>{zip4}</Zip4>' + \
                '</Address>' + \
            '</AddressValidateRequest>'
        self._base_rate_endpoint = 'http://production.shippingapis.com/ShippingAPI.dll?API={api}&XML=' + \
            '<{api}Request USERID="{{username}}">' + \
                '<Revision>2</Revision>' + \
                '{{package}}' + \
            '</{api}Request>'
        self.domestic_rate_endpoint = self._base_rate_endpoint.format(api='RateV4')
        self.international_rate_endpoint = self._base_rate_endpoint.format(api='IntlRateV2')
        # Set the response type to XML
        self.response_type = XML_RESPONSE

    '''
    USPS specific error handler. Parse the error responses and return the appropriate exception.

    ## Parameters
    `error` - The unparsed error message from the server.
    '''
    def process_exception(self, error):
        super(USPSCourier, self).process_exception(error)

    '''
    USPS Address Validation V4 API. Returns one or many `Address` objects depending on the validity of 
    the user provided information, and whether the response was valid.

    ## Parameters
    `State` - The state/providence/region associated with the address. Example: California.
    `City` - The city associated with the address. Example: Cupertino.
    `Zip`- The 5 or 5 + 4 digit zipcode associated with the address. Example: 95014.
    `Street 1` - The secondary identifier of the address. Example: R&D Building.
    `Street 2` - The primary number and road of the address. Example: 1 Infinite Loop Road.
    `Name` - The intended recipient at the address. Example: Steve Jobs.

    ## Returns
    `Addresses` - One or more `Address` objects representing either the correct address or potential corrections.
    `Validity` - Whether the provided address was valid.
    '''
    def validateAddress(self, state, city, postal_code, street_2, street_1='', name=''):
        postal_code = postal_code.split('-')
        # Compose the URL formatting parameters
        params = {
            'state': state.upper(),
            'city': city.upper(),
            'zip5': postal_code[0],
            'zip4': postal_code[1] if len(postal_code) == 2 else '',
            'address_2': street_2.upper(),
            'address_1': street_1.upper(),
            'name': name.upper()
        }

        # Make a request for address information
        raw_response = super(USPSCourier, self).get_server_response(self.address_validation_endpoint, params, method='Address Validation')

        # Extract the XML data for the parsed response
        raw_addresses = raw_response.findall('Address')

        # Check the first address for errors
        error = raw_addresses[0].find('Error')
        if error is not None:
            # Return an empty response
            return AddressValidationResponse()

        # Create the AddressValidationResponse and Addresses
        response = AddressValidationResponse()
        for address in raw_addresses:
            # Used to combine since None might be present
            zip5 = address.find('Zip5').text
            zip4 = address.find('Zip4').text

            # Create the address object
            response.add(
                Address(
                    address.find('State').text,
                    address.find('City').text,
                    '-'.join([zip5, zip4]) if zip4 else zip5,
                    address.find('Address2').text,
                    address.find('DeliveryPoint').text,
                    address.find('CarrierRoute').text,
                )
            )

        return response

    '''
    USPS Tracking Detail V2 API.

    ## Parameters
    `tracking_id` - The USPS tracking id associated with the lett/package of interest. Must be a String type.

    ## Returns
    `TrackingResponse` - Wrapper object for the server response and `TrackingEvents` associated with the provided tracking id.
    '''
    def track(self, tracking_id):
        # Compose the URL formatting parameters
        params = {
            'tracking_id': tracking_id
        }

        # Make a request for the event-level information
        raw_response = super(USPSCourier, self).get_server_response(self.tracking_endpoint, params, method='Tracking')

        # Extract the XML data from the parsed response
        track_info = raw_response.find('TrackInfo')

        # Check to see if we got a valid response
        error = track_info.find('Error')
        if error is not None:
            return self.process_exception(error)

        # Current event/summary
        raw_events = [track_info.find('TrackSummary')]
        # Remaining past events
        raw_events.extend(track_info.findall('TrackDetail'))

        # Create the TrackingResponse and TrackingEvents
        response = TrackingResponse()
        for event in raw_events:
            response.add(
                TrackingEvent(
                    event.find('EventState').text,
                    event.find('EventCity').text,
                    event.find('EventZIPCode').text,
                    event.find('Event').text,
                    event.find('EventDate').text,
                    event.find('EventTime').text,
                    date_format='%B %d, %Y',
                    time_format='%I:%M %p'
                )
            )
        
        return response

    '''
    USPS Rate Calculator V4 and International V2 API.

    NOTE: We currently don't support Non-rectagular packages due to girth calculations. Coming soon.

    ## Parameters
    `Package` - This is the simplist case, the user has already made a `Package` object for their request.
        We just need to extract the attributes.

    ## Returns
    `RateCalculationResponse` - Wrapper object for the server response and `Rates` associated with the provided metrics.
    '''
    def getRate(self, rate_type='domestic', method='ALL', **kwargs):
        # Extract the package item and compose the XML version of it
        package_xml = '<Package ID="{id}">' + \
                        '<Service>{method}</Service>' + \
                        '<ZipOrigination>{origin_zip}</ZipOrigination>' + \
                        '<ZipDestination>{destination_zip}</ZipDestination>' + \
                        '<Pounds>{weight_lb}</Pounds>' + \
                        '<Ounces>{weight_oz}</Ounces>' + \
                        '<Container>{shape}</Container>' + \
                        '<Size>{size}</Size>' + \
                        '<Width>{width}</Width>' + \
                        '<Length>{length}</Length>' + \
                        '<Height>{height}</Height>' + \
                        '<Machinable>true</Machinable>' + \
                    '</Package>'
        package = kwargs.get('package', None)

        # Make sure we got a valid package before continuing
        if package is None:
            raise TypeError('`package` is a required argument (received None)')

        # Compose the URL formatting parameters
        params = {
            'package': package_xml.format(
                id='0',
                method=method, # We only allow a single method type since documentation for multiple is poor :/.
                origin_zip=package.origin,
                destination_zip=package.destination,
                weight_lb=unicode(package.weight[0]),
                weight_oz=unicode(package.weight[1]),
                shape=package.shape,
                size=package.size,
                width=unicode(package.width),
                length=unicode(package.length),
                height=unicode(package.height)
            )
        }

        # Make a request for the event-level information
        raw_response = super(USPSCourier, self).get_server_response(getattr(self, rate_type + '_rate_endpoint'), params, method='Rate')

        # Extract the XML data from the parsed response
        package_info = raw_response.find('Package')

        # Check to see if we got a valid response
        error = package_info.find('Error')
        if error is not None:
            return self.process_exception(error)

        # Gather all of the rates that got returned
        raw_rates = package_info.findall('Postage')
        
        # Create the TrackingResponse and TrackingEvents
        response = RateCalculationResponse()
        for rate in raw_rates:
            response.add(
                RateCalculation(
                    package,
                    rate.find('Rate').text,
                    HTMLParser.HTMLParser().unescape(rate.find('MailService').text)
                )
            )

        return response
