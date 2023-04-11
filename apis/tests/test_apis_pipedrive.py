import unittest
from unittest.mock import patch

from apis.pipedrive import Pipedrive
from apis.tests.mock_response import MockResponse


def mocked_requests_get(url, **kwargs):
    """
    Method responsible for simulating request.get method behaviors
    """
    if 'params' in kwargs:

        if 'api_token' in kwargs["params"]:

            if kwargs["params"]["api_token"] == 'correct_api_token_domain':
                return MockResponse(
                    {
                        "success": True,
                        "data": {"company_domain": "test_domain"}
                    },
                    200)

            if kwargs["params"]["api_token"] == 'correct_api_token_persons':
                return MockResponse(
                    {
                        "success": True,
                        "data": ['contact_1', 'contact_2', 'contact_3'],
                        "additional_data":
                            {
                                "pagination":
                                    {
                                        "more_items_in_collection": True,
                                        "next_start": 4
                                    }
                            }
                    },
                    200)

            if kwargs["params"]["api_token"] == 'correct_api_token_persons_empty':
                return MockResponse(
                    {
                        "success": True,
                        "data": None,
                        "additional_data":
                            {
                                "pagination":
                                    {
                                        "more_items_in_collection": False
                                    }
                            }
                    },
                    200)

            if kwargs["params"]["api_token"] == 'error_api_token':
                return MockResponse(
                    {
                        "success": False,
                        "error": "Any error",
                        "error_info": "Any Problem"
                    },
                    401,
                    reason="Unauthorized")

            if kwargs["params"]["api_token"] == 'except_api_token':
                raise Exception("Any Exception")

    return MockResponse({"error": "Invalid API Token"}, 401, reason='Invalid API token')


class TestePipedriveClass(unittest.TestCase):

    def test_get_domain(self) -> None:
        """Asserts the get_domain method works correctly."""

        pipe = Pipedrive('correct_api_token_domain')
        except_pipe = Pipedrive('except_api_token')
        error_pipe = Pipedrive('error_api_token')
        with patch('requests.get', side_effect=mocked_requests_get):
            self.assertEqual('test_domain', pipe.get_domain())
            self.assertRaises(Exception, except_pipe.get_domain)
            self.assertRaises(Exception, error_pipe.get_domain)

    @patch('apis.pipedrive.Pipedrive.get_domain')
    def test_get_persons_exceptions(self, mock_getdomain) -> None:
        """Asserts the get_persons method catch the raised exceptions."""

        pipe = Pipedrive('except_api_token')
        mock_getdomain.return_value = 'company'

        self.assertRaises(ValueError, pipe.get_persons, start=-1, limit=0)
        self.assertRaises(ValueError, pipe.get_persons, start=0, limit=0)

        with patch('requests.get', side_effect=mocked_requests_get):
            # get method raises exception
            self.assertRaises(Exception, pipe.get_persons)

            # raises exception to API error responses
            pipe_error = Pipedrive('error_api_token')
            self.assertRaises(Exception, pipe_error.get_persons)
            self.assertRaises(Exception, pipe_error.get_persons, start=0, limit=3)

    @patch('apis.pipedrive.Pipedrive.get_domain')
    def test_get_persons_default(self, mock_getdomain) -> None:
        """Asserts the get_persons method works correctly with default arguments."""

        mock_getdomain.return_value = 'company'
        with patch('requests.get', side_effect=mocked_requests_get):
            pipe = Pipedrive('correct_api_token_persons')
            r_data, r_next_start = pipe.get_persons()
            self.assertEqual(['contact_1', 'contact_2', 'contact_3'], r_data)
            self.assertEqual(None, r_next_start)

            pipe_empty = Pipedrive('correct_api_token_persons_empty')
            r_data, r_next_start = pipe_empty.get_persons()
            self.assertEqual(None, r_data)
            self.assertEqual(None, r_next_start)

    @patch('apis.pipedrive.Pipedrive.get_domain')
    def test_get_persons(self, mock_getdomain) -> None:
        """Asserts the get_persons method works correctly when arguments are provided."""

        mock_getdomain.return_value = 'company'
        with patch('requests.get', side_effect=mocked_requests_get):
            pipe = Pipedrive('correct_api_token_persons')
            r_data, r_next_start = pipe.get_persons(start=0, limit=3)
            self.assertEqual(['contact_1', 'contact_2', 'contact_3'], r_data)
            self.assertEqual(4, r_next_start)

            pipe_empty = Pipedrive('correct_api_token_persons_empty')
            r_data, r_next_start = pipe_empty.get_persons(start=0, limit=3)
            self.assertEqual(None, r_data)
            self.assertEqual(None, r_next_start)

    @patch('apis.api.API.post')
    def test_update_person_exceptions(self, mock_post) -> None:
        """Asserts the update_person method catch the raised exceptions."""

        pipe = Pipedrive('except_api_token')

        mock_post.return_value = {
            "response": {
                "success": False,
                "error": "Any error",
                "error_info": "Any Problem"
            }
        }
        # raises exception when API response indicates an error
        self.assertRaises(Exception, pipe.update_person, id=2, person={"person": "name"})

        mock_post.side_effect = Exception("Any Exception")
        # catch post raised exceptions
        self.assertRaises(Exception, pipe.update_person, id=1, person={"person": "name"})

    @patch('apis.api.API.post')
    def test_update_person(self, mock_post) -> None:
        """Asserts the update_person method works correctly."""

        mock_post.return_value = {
            "response": {
                "success": True,
                "data": "Information",
                "additional_data": False
            }
        }
        expected = mock_post.return_value["response"]

        pipe = Pipedrive('healthy_token')
        self.assertEqual(expected, pipe.update_person(1, {"person": "name"}))
