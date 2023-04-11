import logging

from apis.api import API

logger = logging.getLogger('APIs.Pipedrive')

BASE_URL = 'https://api.pipedrive.com'
USERS_ME = '/v1/users/me/'
PERSONS = '/api/v1/persons/'
UPDATE_KEY = 'contact_update'


class Pipedrive(API):
    """
    Class responsible for all interactions with the Pipedrive API.
    """

    def __init__(self, token: str) -> None:
        """
        :param token:  Pipedrive personal token for request authentication.
        """

        self.token = token

        api_source = {
            "endpoints": {
                "base_url": BASE_URL,
                "users_me": USERS_ME,
                "persons": PERSONS
            }
        }

        super(Pipedrive, self).__init__(api_source=api_source)

    def get_domain(self) -> str:
        """
        Gets the company domain the user's token is linked to.

        :return: Company domain.
        """

        try:
            params = {
                'api_token': self.token
            }
            content = self.get(endpoint_key='users_me', params=params)["response"]

            if content["success"] is False:
                msg = content["error"] + '! ' + content["error_info"]
                raise Exception(msg)
            else:
                return content["data"]["company_domain"]

        except Exception as e:
            logger.error(f'Failed to get company domain with provided api token. Error: {str(e)}.')
            raise

    def get_persons(self, start: int = None, limit: int = None) -> list or None:
        """
        Gets the contacts a company has in Pipedrive using the 'people' Pipedrive API endpoint.

        :param start: Pagination start, the default value is 0. Check Pipedrive API pagination documentation
        for more information.
        :param limit: The number of contacts per page, if not provided, 100 items will be returned.

        :return: List of Pipedrive contacts formatted as dictionaries and next page number,
         if there are no more contacts None will be returned as next page.
        """
        params = {
            'api_token': self.token
        }

        if start is not None and limit is not None:
            if not start >= 0:
                raise ValueError(f"start must be a integer equal or greater than 0.")
            if not limit > 0:
                raise ValueError(f"limit must be a integer greater than 0.")
            params['start'] = start
            params['limit'] = limit

        company_domain = self.get_domain()

        try:
            content = self.get(endpoint_key='persons', params=params)["response"]

            if content["success"] is False:
                msg = f'{content["error"]}! {content["error_info"]}'
                raise Exception(msg)

        except Exception as e:
            logger.error(f'Failed to get company contacts with the params {params}. Error: {str(e)}.')
            raise

        next_start = None

        if start is not None:
            more_items = content['additional_data']['pagination']['more_items_in_collection']
            if more_items:
                next_start = content['additional_data']['pagination']['next_start']

        data = content['data']

        if isinstance(data, type(None)):
            logger.warning(f'List of contacts for company domain {company_domain} is empty.')
        else:
            logger.info((f'Retrieving list of contacts for company domain {company_domain} was successful.'
                         f' {len(data)} contacts retrieved.'))

        return data, next_start

    def update_person(self, id: int, person: dict) -> dict:
        """
        Class that updates some contact by id.

        :param id: ID of contact that will be updated.
        :param person: Dictionary with updated contact information.
        :type id: int
        :type person: dict

        :return: The content of the POST response as dictionary.
        """
        put_url = f'{PERSONS}{id}'
        self.api_source["endpoints"][UPDATE_KEY] = put_url

        params = {'api_token': self.token}
        headers = {'content-type': 'application/json'}

        try:
            content = self.post(endpoint_key=UPDATE_KEY, params=params, headers=headers, data=person)["response"]

            if content["success"] is False:
                msg = f'{content["error"]}! {content["error_info"]}'
                raise Exception(msg)

        except Exception as e:
            logger.error(f'Failed update contact with id:{id}, params:{params} and headers:{headers}. Error: {str(e)}.')
            raise

        return content
