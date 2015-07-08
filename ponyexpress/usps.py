from ponyexpress.config import XML_RESPONSE
from ponyexpress.courier import BaseCourier
from ponyexpress.tracking import TrackingResponse, TrackingEvent

# USPSTracking is a class which is able to interface with the USPS Package Tracking API
# The user will provide a tracking number, and then can query the various aspects
class USPSCourier(BaseCourier):
    # Production URL
    tracking_endpoint = 'http://production.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML=<TrackFieldRequest USERID="{username}"><TrackID ID="{tracking_id}"></TrackID></TrackFieldRequest>'

    # Set the response type to XML
    response_type = XML_RESPONSE

    # Extracts error data and throws the proper exception, if needed
    def process_exception(self, error):
        super(USPSCourier, self).process_exception(error)

    # Retrieves the RAW tracking information from USPS
    def track(self, tracking_id):
        # Make a request for the event-level information
        raw_response = super(USPSCourier, self).track(tracking_id)

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

        # Create the TrackingResponse
        response = TrackingResponse()

        # Create an event object for each detail
        for event in raw_events:
            response.addEvents(
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
