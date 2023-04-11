import unittest
from unittest.mock import patch
from requests.exceptions import Timeout

from apis.proxycurl import Proxycurl
from apis.tests.mock_response import MockResponse


def mocked_requests_get(url, **kwargs):
    """
    Method responsible for simulating request.get method behaviors
    """
    if 'params' in kwargs:

        if 'url' in kwargs["params"]:
            if kwargs["params"]["url"] == 'linkedin.com/in/exception':
                raise Exception('Any Exception')
            if kwargs["params"]["url"] == 'linkedin.com/in/timeout':
                raise Timeout("Timeout request")
            if kwargs["params"]["url"] == 'linkedin.com/in/profile':
                return MockResponse({"key": "data"}, 200)

        if 'work_email' in kwargs["params"]:
            if kwargs["params"]["work_email"] == 'exception@email.com':
                raise Exception('Any Exception')
            if kwargs["params"]["work_email"] == 'timeout@email.com':
                raise Timeout("Timeout request")
            if kwargs["params"]["work_email"] == 'user@email.com':
                return MockResponse({"key": "url"}, 200)

    return MockResponse({"error": "Invalid API Key"}, 401, reason='Invalid API Key')


class TesteProxycurlClass(unittest.TestCase):

    def test_get_linkedin_profile_catch_exceptions(self) -> None:
        """
        Asserts "get_linkedin_profile" method catch raised exceptions.
        """
        problem_api = Proxycurl('invalid_api_key')
        with patch('requests.get', side_effect=mocked_requests_get):
            self.assertRaises(Exception, problem_api.get_linkedin_profile, 'linkedin.com/in/exception')
            self.assertRaises(Timeout, problem_api.get_linkedin_profile, 'linkedin.com/in/timeout')

    def test_get_linkedin_profile_returns(self) -> None:
        """
        Asserts "get_linkedin_profile" returns correct values.
        """
        problem_api = Proxycurl('invalid_api_key')
        with patch('requests.get', side_effect=mocked_requests_get):
            bad_response = problem_api.get_linkedin_profile('linkedin.com/in/nope')
            self.assertEqual({"error": "Invalid API Key"}, bad_response["response"])
            healthy_api = Proxycurl('api_key')
            response = healthy_api.get_linkedin_profile('linkedin.com/in/profile')
            self.assertEqual({"key": "data"}, response["response"])

    def test_get_url_catch_exceptions(self) -> None:
        """
        Asserts "get_url_from_work_email" method catch raised exceptions.
        """
        problem_api = Proxycurl('invalid_api_key')
        with patch('requests.get', side_effect=mocked_requests_get):
            self.assertRaises(Exception, problem_api.get_url_from_work_email, 'exception@email.com')
            self.assertRaises(Timeout, problem_api.get_url_from_work_email, 'timeout@email.com')

    def test_get_url_returns(self) -> None:
        """
        Asserts "get_url_from_work_email" returns correct values.
        """
        problem_api = Proxycurl("invalid_api_key")
        with patch('requests.get', side_effect=mocked_requests_get):
            bad_response = problem_api.get_url_from_work_email('bad@email.com')
            self.assertEqual({"error": "Invalid API Key"}, bad_response["response"])
            healthy_api = Proxycurl('api_key')
            response = healthy_api.get_url_from_work_email('user@email.com')
            self.assertEqual({"key": "url"}, response["response"])
