import os
from exceptions import NotImplementedError, TypeError
from datetime import datetime as dt
from unittest import TestCase

from ponyexpress.rates import Package
from ponyexpress.usps import USPSCourier

class USPSTests(TestCase):
	# Create a base carrier
	def setUp(self):
		self.usps = USPSCourier(os.getenv('TEST_PONY_USERNAME'))

	# Test basic tracking functionality with a valid request
	def test_valid_track_response(self):
		# Get the response
		response = self.usps.track('9374889949010711251710')

		# Verify the status, acceptance, and delivery
		self.assertIn('DELIVERED', response.status)
		self.assertEqual(dt(2015, 6, 7, 17, 28), response.accepted)
		self.assertEqual(dt(2015, 6, 9, 12, 33), response.delivered)

	# Test basic tracking functionality with an invalid tracking number
	def test_invalid_track_response(self):
		# Get the response
		try:
			response = self.usps.track('93748899490101251710')
		except NotImplementedError:
			self.assertTrue(True)

	# Test address validation for a correct address
	def test_valid_address_validation(self):
		response = self.usps.validateAddress('CA', 'Cupertino', '95014', '1 Infinite Loop')

		# Did we get a valid response?
		self.assertTrue(response.validated)

		# Confirm zipcode disection
		self.assertEqual(response.address.simple_zip, '95014')

	# Test address validation for an incorrect address, which resolves to a single correct address.
	def test_invalid_address_validation_complete_correction(self):
		response = self.usps.validateAddress('CA', 'Cupertino', '9501', '1 Infinite Circle')

		# Did we get a valid response?
		self.assertTrue(response.validated)

		# Confirm that the two incorrect pieces were fixed
		self.assertEqual(response.address.zip, '95014-2083')
		self.assertEqual(response.address.street, '1 Infinite Loop')

	# Test address validation for an incorrect address, which resolves to no address.
	def test_invalid_address_validation_no_correction(self):
		response = self.usps.validateAddress('CA', '', '', '1 Infinite')

		# We didnt get a valid address
		self.assertFalse(response.validated)
		self.assertIsNone(response.address)

	# Test rate calculation for a standard large box
	def test_valid_rate_calculation(self):
		package = Package((1, 8), 12, 12, 13, True, '11218', '11780')

		response = self.usps.getRate(package=package)

		# Did we get the correct number of responses
		self.assertEqual(len(response.rates), 5)

	# Test what happends when we don't provide the right arguments
	def test_invalid_rate_calculation_arguments(self):
		try:
			response = self.usps.getRate()
		except TypeError:
			self.assertTrue(True)

	# Test what happens when a poor quality package is added
	def test_invalid_rate_calculation(self):
		package = Package(24, 12, 12, 13, False, '11218', '11218')

		try:
			response = self.usps.getRate(package=package)
		except NotImplementedError:
			self.assertTrue(True)

	# Test rate detail fetching for a domestic rate
	def test_valid_rate_detail_calculation(self):
		package = Package((1, 8), 12, 12, 13, True, '11218', '11780')

		response = self.usps.getRate(package=package)

		# Get the detailed options for all of the shipping methods available for USPS
		for rate in response.rates:
			detailed_rate = self.usps.getDetailedRate(rate)

			self.assertEqual(rate.price, detailed_rate.price)
