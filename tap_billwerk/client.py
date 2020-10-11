import requests

import singer
import backoff
import json

LOGGER = singer.get_logger()

BASE_ID_URL =  'https://sandbox.billwerk.com/'
BASE_API_URL = 'https://sandbox.billwerk.com/api/v1/'

class BillwerkClient():
    
    
    def __init__(self, config):
        self._client_id = config['client_id']
        self._client_secret = config['client_secret']
        self._access_token = config.get('token', None)
        
    def _refresh_access_token(self):
        LOGGER.info("Refreshing access token")
        url=BASE_ID_URL + 'oauth/token/'
        data={'client_id': self._client_id,
              'client_secret': self._client_secret,
              'grant_type': 'client_credentials'}

        resp = requests.request('POST', url, data=data,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self._access_token=json.loads(resp.text).get('access_token')
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                                 'Authorization': 'Bearer {}'.format(self._access_token)}
        LOGGER.info("Refreshed access token")
        
    def make_headers(self):
        if self._access_token is not None:
            self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                                  'Authorization': 'Bearer {}'.format(self._access_token)}
            return self._access_token, self._headers
        self._refresh_access_token()
        return self._access_token, self._headers

        
    @backoff.on_exception(backoff.constant,
                          (requests.exceptions.HTTPError),
                          max_tries=3,
                          interval=10)
    def _make_request(self, method, endpoint, headers = None, params=None):
        full_url = BASE_API_URL + endpoint      
        LOGGER.info(
            "%s - Making request to %s endpoint %s, with params %s",
            full_url,
            method.upper(),
            endpoint,
            params,
        )

        resp = requests.request(method, full_url, headers=self._headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, url, headers=None, params=None):
        self._access_token, self._headers = self.make_headers()
        return self._make_request("GET", url, headers=self._headers, params=params)
    
# #### test
# config = {
#   "client_id" : "5f4f8d5d2aaa162b1c662169",
#   "client_secret" : "201490ada937007febef1140732f3161",
# "start_date" : "2020-09-01T00:00:00Z",
# "token" : "Lf5DZNvlFavJoPr09ocju9__aTtokY3gzI__nB0jN8x6M0m07Sx9cOXbDVUg4GxHWrRC9MX0Qv7vSVDRMwoQUQ=="
# }
# test_client = BillwerkClient(config)
# ####  

# full_url = 'https://sandbox.billwerk.com/api/v1/orders'
# headers = {'Content-Type': 'application/x-www-form-urlencoded',
#             'Authorization': 'Bearer Lf5DZNvlFavJoPr09ocju9__aTtokY3gzI__nB0jN8x6M0m07Sx9cOXbDVUg4GxHWrRC9MX0Qv7vSVDRMwoQUQ=='}

# resp = requests.request('GET', full_url, headers=headers, params='take=100')
# resp.raise_for_status()
# json_data = resp.json()
# data = json_data

# if len(json_data) == 100:
    
#     last_entry = json_data[len(json_data)-1].get('Id', json_data[len(json_data)-1].get('Timestamp'))
#     data.remove(data[len(data)-1])
#     resp = requests.request('GET', full_url, headers=headers, params='take=100&from={}'.format(last_entry))
#     json_data = resp.json()
#     data = data + json_data
    

# def more_pages(data, ):
#     pass