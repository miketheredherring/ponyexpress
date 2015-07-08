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
		
