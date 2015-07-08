import os
from datetime import datetime as dt
from unittest import TestCase
from exceptions import NotImplementedError, SyntaxError

from ponyexpress.config import XML_RESPONSE
from ponyexpress.courier import BaseCourier
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
			self.unknown_courier.track('1234567890')
		except NotImplementedError:
			self.assertTrue(True)

	# Test with USPS tracking, won't provide much
	def test_valid_base_tracking(self):
		# Work with USPS for now
		self.unknown_courier.tracking_endpoint = 'http://production.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML=<TrackRequest USERID="{username}"><TrackID ID="{tracking_id}"></TrackID></TrackRequest>'
		self.unknown_courier.response_type = XML_RESPONSE

		response = self.unknown_courier.track('9374889949010711251710')

		self.assertTrue(response is not None)

	# Test with invalid tracking data, non 200 status will throw the exception
	def test_invalid_base_tracking(self):
		# Work with USPS for now
		self.unknown_courier.tracking_endpoint = 'http://www.google.com/hello'
		self.unknown_courier.response_type = XML_RESPONSE

		try:
			response = self.unknown_courier.track('9374889949010711251710')
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
