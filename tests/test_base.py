import os
from datetime import datetime as dt
from unittest import TestCase
from exceptions import NotImplementedError, SyntaxError

from ponyexpress.address import Address, AddressValidationResponse
from ponyexpress.config import XML_RESPONSE, JSON_RESPONSE
from ponyexpress.courier import BaseCourier
from ponyexpress.rates import Package, RateCalculation, RateCalculationResponse, RateOption
from ponyexpress.tracking import TrackingResponse, TrackingEvent

class BaseTests(TestCase):
	# Create a base carrier
	def setUp(self):
		self.unknown_courier = BaseCourier(os.getenv('TEST_PONY_USERNAME'))

	# Test the parse JSON works with valid response
	def test_valid_json(self):
		response = self.unknown_courier.parse_json('{"hello": true}')

		self.assertTrue(response['hello'])

	# Test the parse JSON fails invlaid response
	def test_invalid_json(self):
		try:
			response = self.unknown_courier.parse_json('{"hello": tru}')
		except SyntaxError:
			self.assertTrue(True)

	# Test the parse XML works with valid response
	def test_valid_xml(self):
		response = self.unknown_courier.parse_xml('<hello type="world"></hello>')

		self.assertEqual(response.get('type'), 'world')

	# Test the parse XML fails invlaid response
	def test_invalid_xml(self):
		try:
			response = self.unknown_courier.parse_xml('<hello type="world"><hello>')
		except SyntaxError:
			self.assertTrue(True)

class BaseTrackingTests(TestCase):
	# Create a base carrier
	def setUp(self):
		self.unknown_courier = BaseCourier(os.getenv('TEST_PONY_USERNAME'), os.getenv('TEST_PONY_PASSWORD'))

	# Test the BaseCourier
	def test_no_tracking_endpoint(self):
		# Expect an exception to be thrown, no tracking endpoint specified
		try:
			self.unknown_courier.get_server_response(self.unknown_courier.tracking_endpoint, {'tracking_id': '1234567890'}, 'Tracking')
		except NotImplementedError:
			self.assertTrue(True)

	# Test with USPS tracking, won't provide much
	def test_valid_base_tracking(self):
		# Work with USPS for now
		self.unknown_courier.tracking_endpoint = 'http://production.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML=<TrackRequest USERID="{username}"><TrackID ID="{tracking_id}"></TrackID></TrackRequest>'
		self.unknown_courier.response_type = XML_RESPONSE

		response = self.unknown_courier.get_server_response(self.unknown_courier.tracking_endpoint, {'tracking_id': '9374889949010711251710'}, method='Tracking')

		self.assertTrue(response is not None)

	# Test with invalid tracking data, non 200 status will throw the exception
	def test_invalid_base_tracking(self):
		# Work with USPS for now
		self.unknown_courier.tracking_endpoint = 'http://www.google.com/hello'
		self.unknown_courier.response_type = XML_RESPONSE

		try:
			response = self.unknown_courier.get_server_response(self.unknown_courier.tracking_endpoint, {'tracking_id': '9374889949010711251710'}, method='Tracking')
		except NotImplementedError:
			self.assertTrue(True)

	# Test out the TrackingEvent object
	def test_tracking_event(self):
		event = TrackingEvent('NY', 'New York', '12345', 'ACCEPTED', '07-03-2015', '13:21:00')

		# Make sure it parsed okay
		self.assertEqual(dt(2015, 7, 3, 13, 21), event.datetime)

		# Alternate formatting works
		self.assertEqual('July 03, 2015 01:21 PM', event.isoDatetime())

	# Test the TrackingResponse object
	def test_tracking_response_null(self):
		# Make an empty tracking response
		response = TrackingResponse()

		# WE don't know where this item is
		self.assertEqual('UNKNOWN', response.status)

		# Not delivered or accepted
		self.assertIsNone(response.accepted)
		self.assertIsNone(response.delivered)

	# Test the TrackingResponse object
	def test_tracking_response_accepted_delivered(self):
		event1 = TrackingEvent('NY', 'New York', '12345', 'ACCEPTED', '07-03-2015', '13:21:00')
		event2 = TrackingEvent('BC', 'Vancouver', '98765', 'DELIVERED', '07-06-2015', '07:47:00')

		# Events will be added in reverse chronological order in real life
		response = TrackingResponse(event2, event1)

		# Make sure that we have the correct status, acceptance, and delivery info
		self.assertEqual('DELIVERED', response.status)
		self.assertEqual(dt(2015, 7, 3, 13, 21), response.accepted)
		self.assertEqual(dt(2015, 7, 6, 7, 47), response.delivered)

class BaseAddressTests(TestCase):
	# Test out the Address object
	def test_address_5_zip(self):
		address = Address('CA', 'Cupertino', '95014', '1 Infinite Circle')
		# Make sure it parsed okay
		self.assertEqual(address.simple_zip, '95014')

	# Test out the Address object
	def test_address_5_plus_4_zip(self):
		address = Address('CA', 'Cupertino', '95014-1234', '1 Infinite Circle')
		# Make sure it parsed okay
		self.assertEqual(address.simple_zip, '95014')

class BaseRateTests(TestCase):
	# Test out the Package object
	def test_package_large_rectangular(self):
		package = Package((1, 8), 12, 12, 13, True, '11218', '11780')

		# Make sure the weight was taken as (Lbs, Ozs)
		self.assertEqual(package.weight, (1, 8))

		# Make sure sizing is correct
		self.assertEqual(package.size, 'LARGE')
		self.assertEqual(package.shape, 'RECTANGULAR')

	# Test out the Package object
	def test_package_regular_non_rectangular(self):
		package = Package(24, 8, 8, 8, False, '11218', '11780')

		# Make sure the weight was taken as (Lbs, Ozs)
		self.assertEqual(package.weight, (1, 8))

		# Make sure sizing is correct
		self.assertEqual(package.size, 'REGULAR')
		self.assertEqual(package.shape, 'NONRECTANGULAR')

	# Test the RateCalculation object
	def test_rate_calculation(self):
		package = Package(24, 8, 8, 8, False, '11218', '11780')

		rate = RateCalculation(package, 24.50, 'Priority 2-Day')

		# Make sure the price is correct
		self.assertEqual(rate.price, 24.50)

		# Reassign to test string parsing or costs
		rate = RateCalculation(package, '42.50', 'Priority 1-Day')

		# Make sure the price is correct
		self.assertEqual(rate.price, 42.50)

		# Adds an option for the rate
		rate.options.append(RateOption('Tracking', 12.5))

		# Make sure the correct number of objects are the
		self.assertEqual(len(rate.options), 1)

	# Test the RateCalculationResponse object
	def test_rate_calculation_response(self):
		# Setup dummy objects
		package = Package(24, 8, 8, 8, False, '11218', '11780')
		rate_1 = RateCalculation(package, 24.50, 'Priority 2-Day')
		rate_2 = RateCalculation(package, 42.50, 'Priority 1-Day')

		# Rates are added in no particular ordering
		response = RateCalculationResponse(rate_1, rate_2)

		self.assertEqual(response.cheapest().price, 24.50)

	# Test the RateOption object
	def test_rate_option(self):
		# Make a new instance of the rate option
		option = RateOption('Tracking', '2.50', id='123')

		# Verify price was converted and kwargs added
		self.assertEqual(option.price, 2.5)
		self.assertEqual(option.id, '123')
