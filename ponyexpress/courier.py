'''
Base carrier class and helper objects.
'''
import requests, json
import xml.etree.ElementTree as et
from xml.etree.ElementTree import ParseError

from ponyexpress.config import JSON_RESPONSE


class BaseCourier(object):
    '''
    Provides base level attributes and methods for new carriers.
    '''
    # Creates a new instance of the postal carrier base object
    def __init__(self, username, password=''):
        # Init instance variables
        self.tracking_endpoint = None
        self.shipping_endpoint = None
        self.address_validation_endpoint = None

        # Default response parse is JSON. See `ponyexpress.config` for preset types.
        self.response_type = JSON_RESPONSE

        # User authentication
        self.username = username
        self.password = password

    '''
    Helper function for parsing a JSON based repsonse. Very naive for now, just loads and returns

    ## Parameters
    `response` - The HTTP response body received from a web server to be parsed.

    ## Returns
    `Object` - JSON parsed response body.
    '''
    def parse_json(self, response):
        try:
            return json.loads(response)
        except ValueError:
            raise SyntaxError('The webserver responded with malformed %s' % self.response_type)

    '''
    Helper function for parsing a XML based response. Little more complex than the JSON.

    ## Parameters
    `response` - The HTTP response body received from a web server to be parsed.\

    ## Returns
    `XMLElementTree` - XML parsed response body.
    '''
    def parse_xml(self, response):
        try:
            return et.fromstring(response)
        except ParseError:
            raise SyntaxError('The webserver responded with malformed %s' % self.response_type)

    '''
    Base error handling method. Throws the appropriate exceptions.
    Simply throw an exception saying something went wrong, but we don't know what to do about it.

    ## Parameters
    `error` - The error data associated with the response.
    '''
    def process_exception(self, *kwargs):
        raise NotImplementedError('An error occured in your request. Unable to parse detailed error message.')

    '''
    Base XMl response. Gets and parses a servers response, with basic error handling.

    ## Parameters
    `tracking_id` - String representing the tracking identifier for your package/letter.

    ## Returns
    `Response` - The parsed response from the server. Can be XMLElementTree or JSON decoded Python object.
    '''
    def get_server_response(self, endpoint='', params={}, method='default'):
        # Checks to make sure that the carrier overrode the endpoint
        if not endpoint:
            raise NotImplementedError('Failed to specify the %s service endpoint.' % method)

        # Add default params
        params.update({'username': self.username, 'password': self.password})

        # Make a request to the specified URL
        self.last_endpoint = endpoint.format(**params)
        response = requests.get(self.last_endpoint)

        # Check if we got a success, parse the results and construct the TrackingResponse object
        if response.status_code == 200:
            # Save the response object for user inspection
            self._server_response = response

            # Parse the content of the response with the specified response_type
            parsed_response = getattr(self, 'parse_' + self.response_type.lower())(response.content)

            # We have no idea what the response looks like for the general case, so pass it up
            return parsed_response
        else:
            self.process_exception()

        # If we got an error, return None, there was probably an exception thrown along the way too
