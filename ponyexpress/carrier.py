'''
Base carrier class and helper objects.
'''
import os, requests, json
import xml.etree.ElementTree as et
from xml.etree.ElementTree import ParseError
from datetime import datetime as dt

from exceptions import NotImplementedError, SyntaxError, ValueError

from ponyexpress.config import JSON_RESPONSE

class BaseCarrier:
	'''
	Provides base level attributes and methods for new carriers.
	'''
	tracking_endpoint = None
	shipping_endpoint = None
	address_validation_endpoint = None

	# Default response parse is JSON. See `ponyexpress.config` for preset types.
	response_type = JSON_RESPONSE

	# Creates a new instance of the postal carrier base object
	def __init__(self, username, password=''):
		self.username = username
		self.password = password

	'''
	Helper function for parsing a JSON based repsonse. Very naive for now, just loads and returns

	## Parameters
	`response` - The HTTP response body received from a web server to be parsed.

	## Returns 
	Object - JSON parsed response body.
	'''
	def parse_json(self, response):
		try:
			return json.loads(response.content)
		except ValueError:
			raise SyntaxError('The webserver responded with malformed %s' % self.response_type)

	'''
	Helper function for parsing a XML based response. Little more complex than the JSON.

	## Parameters
	`response` - The HTTP response body received from a web server to be parsed.\

	## Returns 
	ElementTree - XML parsed response body.
	'''
	def parse_xml(self, response):
		try:
			return et.fromstring(response.content)
		except ParseError:
			raise SyntaxError('The webserver responded with malformed %s' % self.response_type)

	'''
	Base tracking method.

	## Parameters
	`tracking_id` - String representing the tracking identifier for your package/letter.
	'''
	def track(self, tracking_id):
		# Checks to make sure that the carrier overrode the endpoint
		if not tracking_endpoint:
			raise NotImplementedError('Failed to specify the tracking service endpoint.')

		# Make a request to the specified URL
		endpoint = self.tracking_endpoint.format(username=self.username, tracking_id=tracking_id)
		response = requests.get(endpoint)

		# Check if we got a success, parse the results and construct the TrackingResponse object
		if response.status_code == 200:
			parsed_response = getattr(self, 'parse_' + self.response_type.lower())(response)

			# We have no idea what the response looks like for the general case, so pass it up
			return parsed_response

		# If we got an error, return None, there was probably an exception thrown along the way too
		return None
	