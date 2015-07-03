from datetime import datetime as dt

# Lookup lists for keywords which specify a type of event. Parsed from response text.
ACCEPTANCE_METHODS = ['ACCEPTED', 'PICKED UP']
DELIVERED_METHODS = ['DELIVERED', ]

class TrackingResponse:
	'''
	Response object containing all of the tracking events and helper methods for formating data.

	## Attributes
	`events` - List of `TrackingEvent` objects in reverse chronological order.
	`status` - Current status of the package/letter, corresponds to the latest `TrackingEvent.type`.
	'''

	events = []

	class TrackingEvent:
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

		# Default date/time string parsers
		DATE_FORMATER = '%m-%d-%Y'
		TIME_FORMATER = '%H:%M:%S'

		# Init method for creating a new instance of the TrackingEvent.
		def __init__(self, etype='UNDEFINED', date='01-01-1970', time='00:00:00', state, city, postal_code):
			self.type = etype.upper()
			self.date = dt.strptime(date, self.DATE_FORMATER).date()
			self.time = dt.strptime(time, self.TIME_FORMATER).time()
			self.state = state.title()
			self.city = city.title()
			self.postal_code = postal_code

		@property
		def datetime(self):
			return dt.combine(self.date, self.time)

		# Returns a nice string representation of the date and time
		def iso_datetime(self, DATE_FORMAT='%B %d, %Y', TIME_FORMAT='%I:%M %p'):
		    return dt.strptime(' '.join([self.date, self.time]), 
		    				   ' '.join([DATE_FORMAT, TIME_FORMAT]))

	# Init for new TrackingResponse
	def __init__(self):
		pass

	# The current status of the tracked package/letter
	@property
	def status(self):
		# Make sure we got events
		if events:
	    	return self.event[0].type
	    return 'UNKNOWN'

	# If the package/letter has been accepted by the carrier.
	# Returns an datetime object if so
	@property
	def accepted(self):
		# Check all of the events for an ACCEPTANCE one
	    for event in self.events:
	    	if event.type in ACCEPTANCE_METHODS:
	    		return event.datetime
	    return None

	# If the package/letter has been delivered by the carrier.
	# Returns an datetime object if so
	@property
	def delivered(self):
		# Check all of the events for an ACCEPTANCE one
	    for event in self.events:
	    	if event.type in DELIVERED_METHODS:
	    		return event.datetime
	    return None
	
	