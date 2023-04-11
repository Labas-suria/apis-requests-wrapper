import unittest
from unittest.mock import patch, Mock

import requests.exceptions

from apis.api import API
from apis.tests.mock_response import MockResponse

HEALTHY_API_SOURCE = {
    "endpoints": {
        "base_url": "http://path",
        "healthcheck": "//healthcheck",
        "data_key": "//data"
    }
}


def mocked_requests_get(url, **kwargs):
    """
    Method responsible for simulating request.get method behaviors
    """

    if url == 'http://path//healthcheck':
        return MockResponse({"key1": "value1"}, 200)
    elif url == 'http://path//data':
        return MockResponse({"key2": "value2"}, 200)
    elif url == '':
        raise Exception('Any Exception')

    if 'headers' in kwargs:
        if kwargs['headers']['header_1'] == 'exception_Timeout':
            raise requests.exceptions.Timeout
        if kwargs['headers']['header_1'] == 'request_error':
            return MockResponse({}, 401, reason='unauthorized')
        if kwargs['headers']['header_1'] == 'non_json':
            return MockResponse("Non JSON response", 200)

    return MockResponse({}, 404, reason='error')


class TestAPIClass(unittest.TestCase):

    def test_constructor(self) -> None:
        """
        Asserts that api_source has the correct attributes.
        """
        self.assertRaises(KeyError, API, api_source={})
        self.assertRaises(KeyError, API, api_source={"endpoints": {"healthcheck": "foo"}})
        self.assertRaises(KeyError, API, api_source={"endpoints": {"base_url": "foo"}}, enforce_healthcheck=True)

    def test_api_healthcheck(self) -> None:
        """
        Asserts the API health check works correctly
        """
        api = API(api_source=HEALTHY_API_SOURCE, enforce_healthcheck=True)
        with patch('requests.get', side_effect=mocked_requests_get):
            # mocked_requests_get method will return a different responses for different urls and headers
            self.assertEqual(200, api._api_health_check("http://path//healthcheck"))
            self.assertEqual(
                {"error": "API healthcheck not OK -> (404) error"},
                api._api_health_check("http://path//bad//healthcheck"))
            self.assertEqual(
                {"error": f"Failed to validate API HealthCheck, please check the logs for more information."},
                api._api_health_check(""))

    def test_request_raise_exceptions(self) -> None:
        """
        Asserts the API _request raise exceptions correctly
        """
        api = API(api_source=HEALTHY_API_SOURCE)
        self.assertRaises(Exception, api._request, request_type='put', url='')
        # test get requests cases
        with patch('requests.get', side_effect=mocked_requests_get):
            self.assertRaises(Exception, api._request, request_type='get', url='')
            self.assertRaises(requests.exceptions.Timeout, api._request,
                              request_type='get',
                              url='http://path',
                              headers={"header_1": "exception_Timeout"})

        # test post requests cases
        with patch('requests.post', side_effect=mocked_requests_get):
            self.assertRaises(Exception, api._request, request_type='post', url='')
            self.assertRaises(requests.exceptions.Timeout, api._request,
                              request_type='post',
                              url='http://path',
                              headers={"header_1": "exception_Timeout"})

    def test_request(self) -> None:
        """
        Asserts the API _request works correctly.
        """
        api_hc = API(api_source=HEALTHY_API_SOURCE, enforce_healthcheck=True)
        api_hc._api_health_check = Mock()
        hc_return_error = {"error": f"API healthcheck not OK -> (400) error"}
        api_hc._api_health_check.return_value = hc_return_error

        api = API(api_source=HEALTHY_API_SOURCE)

        with patch('requests.get', side_effect=mocked_requests_get):
            self.assertEqual({"response": {"key2": "value2"}},
                             api._request(request_type='get', url='http://path//data'))
            self.assertEqual({"response": {}},
                             api._request(request_type='get', url='http://path//error'))
            self.assertIsInstance(api._request(request_type='get',
                                               url='http://path//test',
                                               headers={"header_1": "non_json"}
                                               )["response"]
                                  , bytes)

            # healthcheck failed
            self.assertEqual(hc_return_error,
                             api_hc._request(request_type='get', url='http://path//data'))

        with patch('requests.post', side_effect=mocked_requests_get):
            self.assertEqual({"response": {"key2": "value2"}},
                             api._request(request_type='post', url='http://path//data'))
            self.assertEqual({"response": {}},
                             api._request(request_type='post', url='http://path//error'))
            self.assertIsInstance(api._request(request_type='post',
                                               url='http://path//test',
                                               headers={"header_1": "non_json"}
                                               )["response"]
                                  , bytes)

            # healthcheck failed
            self.assertEqual(hc_return_error,
                             api_hc._request(request_type='post', url='http://path//data'))

    def test_get(self) -> None:
        """
        Asserts the GET request API works correctly
        """
        healthy_api = API(api_source=HEALTHY_API_SOURCE)
        self.assertRaises(KeyError, healthy_api.get, "")

        healthy_api._request = Mock()
        ok_response = {"response": {"data": "value"}}
        healthy_api._request.return_value = ok_response

        self.assertEqual(ok_response, healthy_api.get('data_key'))

    def test_post(self) -> None:
        """
        Asserts the POST request API works correctly
        """
        healthy_api = API(api_source=HEALTHY_API_SOURCE)
        self.assertRaises(KeyError, healthy_api.post, "")

        healthy_api._request = Mock()
        ok_response = {"response": {"data": "value"}}
        healthy_api._request.return_value = ok_response

        self.assertEqual(ok_response, healthy_api.post('data_key'))
