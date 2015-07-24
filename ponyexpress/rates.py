class Package(object):
	'''
	Represents a shippable item and contains various metrics about the item.

	## Attributes
	`tracking_id` - The unique idenfier which could be used to track the item via the tracking api.
		Not all `Package` instances are guaranteed to have tracking.
	`origin` - The originating zip code of the `Package`.
	`destination` - The receiving zip code for the `Package`.
	`weight` - The gross mass of the `Package` in US (Lbs, Ozs).
	`length` - The primary dimension of the `Package` in US Inches.
	`width` - The secondary dimension of the `Package` in US Inches.
	`height` - The tertiary dimension of the `Package` in US Inches.
	`rectangular` - Is the `Package` shape rectuangular? Use your best judgement for this one :).
	'''

	# Init method for creating a new Package instance.
	# Weight should be provided in US Ozs and will be converted automatically.
	def __init__(self, weight, length, width, height, rectangular,
				 origin, destination, tracking_id=''):
		# Physical attributes of the `Package`
		self.rectangular = rectangular
		self.weight = weight
		self.length = length
		self.width = width
		self.height = height
		self.origin = origin
		self.destination = destination
		self.tracking_id = tracking_id

	# Simply returns the weight in Lbs to the user
	@property
	def weight(self):
	    return self._weight

	# Allows the user to either specify the weight in Lbs or as a Tuple of Lbs and Ozs.
	@weight.setter
	def weight(self, value):
		# Check for the Tuple, this is a (Lb, Oz) format.
		print type(value)
		if isinstance(value, tuple):
			self._weight = value
		else:
			self._weight = ((value / 16), (value % 16))

	# Returns the 'Size' of the `Package`, which could be LARGE or REGULAR. If any dimention
	# exceeds 12", then the `Package` is considered LARGE.
	@property
	def size(self):
	    if any(dim > 12 for dim in [self.width, self.height, self.length]):
	    	return 'LARGE'
	    return 'REGULAR'

	# Returns the 'Shape' of the `Package`, which could be RECTANGULAR or NONRECTANGULAR.
	@property
	def shape(self):
	    if self.rectangular:
	    	return 'RECTANGULAR'
	    return 'NONRECTANGULAR'

class RateCalculationResponse:
	'''
	Response object containing the results of a rate calculation request.
	This response will contain a list of rate estimates for the requested services.
	If rate is requested for a specific service and is not in the response, this assumes
	the package/letter could not be sent via that service.

	## Attributes
	`rates` - List of `RateCalculation` objects for each requested shipping method.
	'''

	# Init for new RateCalculationResponse instance.
	def __init__(self, *rates):
		self.rates = []
		self.add(*rates)

	# Adds `RateCalculations` to the response
	def add(self, *rates):
		# Extend the list of results with the new ones
		if len(rates):
			self.rates.extend(rates);

	# Returns the `RateCalculation` associated with the lowest price
	# Since multiple rate requests can be made for several packages, we
	# default to using the first package.
	def cheapest(self, package_id='0'):
		return sorted(self.rates, key=lambda x: x.rate)[0]

class RateCalculation:
	'''
	Simple object containing all of the metrics provided for the package/letter,
	as well as, the shipping information.

	## Attributes
	`item` - The `Package` associated with the calculated rate.
	`rate` - The cost, in USD, for the specified shipping method when used with `item`.
	`method` - The specified shipping method for the `Package`.
	'''

	# Init method for creating a new Address instance.
	def __init__(self, package, rate, method):
		self.package = package
		self.rate = float(rate)
		self.method = method
	