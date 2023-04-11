import logging

from apis.api import API

logger = logging.getLogger('APIs.Proxycurl')

BASE_URL = 'https://nubela.co'
DATA_FROM_PROFILE = '/proxycurl/api/v2/linkedin'
URL_FROM_EMAIL = '/proxycurl/api/linkedin/profile/resolve/email'


class Proxycurl(API):
    """
    Class responsible for all interactions with the Proxycurl API for LinkedIn.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

        api_source = {
            "endpoints": {
                "base_url": BASE_URL,
                "data_from_profile": DATA_FROM_PROFILE,
                "url_from_email": URL_FROM_EMAIL
            }
        }

        super(Proxycurl, self).__init__(api_source=api_source)

    def get_linkedin_profile(self, profile_url: str) -> dict:
        """
        Gets data from a LinkedIn profile.

        :param str profile_url: URL that defines the profile where the data will be extracted.
        :return: Dictionary with the data extracted from user profile.
        """
        params = {'url': profile_url}
        header = {'Authorization': 'Bearer ' + self.api_key}

        try:
            response = self.get("data_from_profile", params=params, headers=header)
        except Exception as e:
            logger.error(f"Failed to get data from url with params ({str(params)}) and headers ({str(header)})."
                         f" Error: {str(e)}")
            raise

        return response

    def get_url_from_work_email(self, work_email: str) -> dict:
        """
        Gets user's profile URl searching it by the user work email.

        :param str work_email: User's work email.
        :return: Dictionary with user's LinkedIn profile URL.
        """
        params = {'work_email': work_email}
        header = {'Authorization': 'Bearer ' + self.api_key}

        try:
            response = self.get("data_from_profile", params=params, headers=header)
        except Exception as e:
            logger.error(f"Failed to get data from url with params ({str(params)}) and headers ({str(header)})."
                         f" Error: {str(e)}")
            raise

        return response
