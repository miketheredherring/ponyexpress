from datetime import datetime as dt

# Lookup lists for keywords which specify a type of event. Parsed from response text.
ACCEPTANCE_METHODS = ['ACCEPTED', 'PICKED UP']
DELIVERED_METHODS = ['DELIVERED', ]


class TrackingResponse(object):
    '''
    Response object containing all of the tracking events and helper methods for formating data.

    ## Attributes
    `events` - List of `TrackingEvent` objects in reverse chronological order.
    `status` - Current status of the package/letter, corresponds to the latest `TrackingEvent.type`.
    '''

    # Init for new TrackingResponse
    def __init__(self, *events):
        self.events = []
        self.add(*events)

    # The current status of the tracked package/letter
    @property
    def status(self):
        # Make sure we got events
        if len(self.events):
            return self.events[0].type
        return 'UNKNOWN'

    # If the package/letter has been accepted by the carrier.
    # Returns an datetime object if so
    @property
    def accepted(self):
        # Check all of the events for an ACCEPTANCE one
        for event in reversed(self.events):
            for method in ACCEPTANCE_METHODS:
                if method in event.type:
                    return event.datetime
        return None

    # If the package/letter has been delivered by the carrier.
    # Returns an datetime object if so
    @property
    def delivered(self):
        # Check all of the events for an DELIVERED one
        for event in self.events:
            for method in DELIVERED_METHODS:
                if method in event.type:
                    return event.datetime
        return None

    # Adds tracking events to the response
    def add(self, *events):
        # Extend the list of results with the new ones
        if len(events):
            self.events.extend(events)


class TrackingEvent(object):
        '''
        Contains basic information associated with the status of a package/letter.

        ## Attributes
        `type` - The current status of the item, such as, SHIPPED, DELIVERED, RECEIVED, etc. Will always be in CAPS.
        `date` - The UTC date that this event occured on. Default parse format is `%m-%d-%Y`, 06-29-2015.
        `time` - The UTC time that this event occured at. Default parse format is '%H:%M:%S', 17:35:59.
        `state` - The state/province/region which this event happend in.
        `city` - The city within the above state whic this event happend in.
        `postal_code` - The zip/postal code associated with the particular area within the above city.
        '''

        # Init method for creating a new instance of the TrackingEvent.
        def __init__(self, state, city, postal_code, etype='UNDEFINED',
                     date='01-01-1970', time='00:00:00',
                     date_format='%m-%d-%Y', time_format='%H:%M:%S'):
            self.type = etype.upper()
            self.date = dt.strptime(date, date_format).date()
            self.time = dt.strptime(time, time_format).time()
            self.state = state.title()
            self.city = city.title()
            self.postal_code = postal_code

        @property
        def datetime(self):
            return dt.combine(self.date, self.time)

        # Returns a nice string representation of the date and time
        def isoDatetime(self, date_format='%B %d, %Y', time_format='%I:%M %p'):
            return self.datetime.strftime(' '.join([date_format, time_format]))
