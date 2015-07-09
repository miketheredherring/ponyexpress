import os
from exceptions import NotImplementedError
from datetime import datetime as dt
from unittest import TestCase

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
		response = self.usps.validate_address('CA', 'Cupertino', '95014', '1 Infinite Loop')

		# Did we get a valid response?
		self.assertTrue(response.validated)

		# Confirm zipcode disection
		self.assertEqual(response.address.simple_zip, '95014')

	# Test address validation for an incorrect address, which resolves to a single correct address.
	def test_invalid_address_validation_complete_correction(self):
		response = self.usps.validate_address('CA', 'Cupertino', '9501', '1 Infinite Circle')

		# Did we get a valid response?
		self.assertTrue(response.validated)

		# Confirm that the two incorrect pieces were fixed
		self.assertEqual(response.address.zip, '95014-2083')
		self.assertEqual(response.address.street, '1 Infinite Loop')

	# Test address validation for an incorrect address, which resolves to no address.
	def test_invalid_address_validation_no_correction(self):
		response = self.usps.validate_address('CA', '', '', '1 Infinite')

		# We didnt get a valid address
		self.assertFalse(response.validated)
		self.assertIsNone(response.address)
