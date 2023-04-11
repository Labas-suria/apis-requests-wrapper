import logging

import requests

logger = logging.getLogger('APIs.API')

SUCCESS_HTTP_CODES = [200, 201, 202, 204]


class API:

    def __init__(self, api_source: dict, enforce_healthcheck: bool = False) -> None:
        """
        :param dict api_source: dict containing API consumption paths and keys.
            The dict has the following keys:
            - endpoints: dictionary with "base_url", "healthcheck", and resource endpoints;
        :param bool enforce_healthcheck: boolean that enables healthcheck validation before API consumption.
        """
        self.api_source = api_source
        try:
            self.base_url = api_source["endpoints"]["base_url"]
            if enforce_healthcheck:
                self.hc_url = self.base_url + api_source["endpoints"]["healthcheck"]
        except KeyError as e:
            logger.error(f"Invalid API source, key {str(e)} not found.")
            raise
        self.enforce_healthcheck = enforce_healthcheck

    def _api_health_check(self, url: str) -> int or dict:
        """
        Method responsible for checking the API integrity.

        :param str url: API healthcheck endpoint url.

        :return: 200 if healthcheck is OK or a dict with the error in healthcheck validation.
        """
        try:
            response = requests.get(url=url)
            logger.info(f'API HealthCheck status code: "{response.status_code}"')
            if response.status_code != 200:
                return {"error": f"API healthcheck not OK -> ({response.status_code}) {response.reason}"}
        except Exception as e:
            logger.error(f'API HealthCheck failed: "{str(e)}"')
            return {"error": f"Failed to validate API HealthCheck, please check the logs for more information."}
        return response.status_code

    def _request(self, request_type: str, url: str, params: dict = None, **kwargs) -> dict:
        """
        Method responsible for making the request in the provided url of the type defined in request_type.

        :param str request_type: string with type of request to be made. Currently supported types: "get", "post".
        :param str url: url to request.
        :param dict params: dictionary with the request parameters.

        :return: dict with response. If response is not a valid JSON, response will be returned in bytes.
        """
        api_healthcheck = None
        if self.enforce_healthcheck:
            api_healthcheck = self._api_health_check(self.hc_url)

        if api_healthcheck == 200 or api_healthcheck is None:
            try:
                if request_type == 'get':
                    response = requests.get(url, params=params, **kwargs)
                    logger.info((f'GET request in "{url}" with params "{params}" returned status code:'
                                 f' "{response.status_code}"'))
                elif request_type == 'post':
                    response = requests.post(url, params=params, **kwargs)
                    logger.info((f'POST request in "{url}" with params "{params}" returned status code:'
                                 f' "{response.status_code}"'))
                else:
                    raise Exception((f'The provided request_type: "{request_type}" is not valid,'
                                     ' please check the method documentation for more information.'))

                if response.status_code in SUCCESS_HTTP_CODES:
                    dict_response = response.json()
                    if not dict_response:
                        logger.warning(f"Empty response with params ({str(params)})")
                else:
                    logger.error(f"API returned an error: ({response.status_code}) {response.reason}")
                    dict_response = response.json()
                return {"response": dict_response}

            except requests.exceptions.JSONDecodeError:
                logger.warning((f"Response is not a valid JSON for params ({str(params)}) and args ({str(kwargs)})."
                                " The response was returned in bytes."))
                return {"response": response.content()}
            except requests.exceptions.Timeout:
                logger.error((f"Failed to get response with params ({str(params)}) and args ({str(kwargs)}),"
                              " timeout request"))
                raise
            except requests.exceptions.TooManyRedirects:
                logger.error((f"Failed to get response with params ({str(params)}) and args ({str(kwargs)}),"
                              " too many redirects"))
                raise
            except requests.exceptions.RequestException as e:
                logger.error((f"Failed to get response with params ({str(params)}) and args ({str(kwargs)}),"
                              f" {str(e)}"))
                raise
        else:
            return api_healthcheck

    def get(self, endpoint_key: str, params: dict = None, **kwargs) -> dict:
        """
        GET request to consume a REST API defined by the api_source.

        :param str endpoint_key: endpoint key to consume from, as defined in the api_source.
        :param dict params: dictionary with the request parameters.

        :return: dict with response. If API response is not a valid JSON, response will be returned in bytes.
        """
        try:
            url = self.base_url + self.api_source["endpoints"][endpoint_key]
        except KeyError as e:
            logger.error(f"Invalid API source, key {str(e)} not found.")
            raise

        return self._request('get', url=url, params=params, **kwargs)

    def post(self, endpoint_key: str, params: dict = None, **kwargs) -> dict:
        """
        POST request to consume a REST API defined by the api_source.

        :param str endpoint_key: endpoint key to consume from, as defined in the api_source.
        :param dict params: dictionary with the request parameters.

        :return: dict with response. If API response is not a valid JSON, response will be returned in bytes.
        """

        try:
            url = self.base_url + self.api_source["endpoints"][endpoint_key]
        except KeyError as e:
            logger.error(f"Invalid API source, key {str(e)} not found.")
            raise

        return self._request('post', url=url, params=params, **kwargs)
