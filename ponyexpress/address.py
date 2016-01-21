class AddressValidationResponse(object):
    '''
    Response object containing the results of a address validation request.
    The number of results returned will vary based on whether the valiation was a success.
    One result is indicative of success. Multiple shows there was a correction or conflict between multiple addresses.

    ## Attributes
    `addresses` - List of `Address` objects matching the validation request
    '''

    # Init for new AddressValidationResponse
    def __init__(self, *addresses):
        self.addresses = []

    # Since we only allow single address validation, here is a simple hook for getting the validated address.
    # Though we do store it as a list, this is for the future when you can validate multiple addresses simultaneously.
    @property
    def address(self):
        if len(self.addresses):
            return self.addresses[0]
        return None

    # Simple access for correct address, if valid. Returns None if no validation found.
    # Raises MultipleAddressesFoundException if correct address could not be resolved pragmatically.
    @property
    def validated(self):
        if len(self.addresses):
            return True
        return False

    # Adds `Addresses` to the response
    def add(self, *addresses):
        # Extend the list of results with the new ones
        if len(addresses):
            self.addresses.extend(addresses)


class Address(object):
    '''
    Simple object containing all of the identifiers associated with a given US Postal address.

    ## Attributes
    `State` - The state/providence/region associated with the address. Example: California.
    `City` - The city associated with the address. Example: Cupertino.
    `Zip`- The 5 + 4 digit zipcode associated with the address. Example: 95014-2083.
    `Street` - The primary number and road of the address. Example: 1 Infinite Loop.
    `Delivery Point` - The physical location representing where the letter/package will be delivered.
    `Carrier Route` - The route the letter/package will travel when out for delivery. Can be used to gain information
        about the surrounding area like income and total delivery points.
    '''

    # Init method for creating a new Address instance.
    def __init__(self, state, city, postal_code, street,
                 delivery_point='', carrier_route=''):
        self.state = state.title()
        self.city = city.title()
        self.zip = postal_code
        self.street = street.title()
        self.delivery_point = delivery_point
        self.carrier_route = carrier_route

    @property
    def simple_zip(self):
        return self.zip.split('-')[0]
