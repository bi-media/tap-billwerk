import requests
import singer
import backoff
import json

LOGGER = singer.get_logger()

    #### Billwerk Sandbox ####
BASE_ID_URL =  'https://sandbox.billwerk.com/'
BASE_API_URL = 'https://sandbox.billwerk.com/api/v1/'

    #### Billwerk ####
# BASE_ID_URL =  'https://app.billwerk.com/'
# BASE_API_URL = 'https://app.billwerk.com/api/v1/'


class BillwerkClient():
    
    
    def __init__(self, config):
        
        self._client_id = config['client_id']
        self._client_secret = config['client_secret']
        self._access_token = config.get('token', None)
        
    def _refresh_access_token(self):
        LOGGER.info('Refreshing access token')
        url=BASE_ID_URL + 'oauth/token/'
        data={'client_id': self._client_id,
              'client_secret': self._client_secret,
              'grant_type': 'client_credentials'}
        resp = requests.request('POST', url, data=data, headers={
                                'Content-Type': 'application/x-www-form-urlencoded'})
        self._access_token=json.loads(resp.text).get('access_token')
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Authorization': 'Bearer {}'.format(self._access_token)}
        LOGGER.info('Refreshed access token')
        
    def make_headers(self):
        
        if self._access_token is not None:
            self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                             'Authorization': 'Bearer {}'.format(self._access_token)}
            
            return self._access_token, self._headers
        
        self._refresh_access_token()
        
        return self._access_token, self._headers

        
    @backoff.on_exception(backoff.constant,(requests.exceptions.HTTPError), max_tries=3, interval=10)
    def _make_request(self, method, endpoint, headers=None, params=None):
        full_url = BASE_API_URL + endpoint      
        LOGGER.info('%s - Making request to %s endpoint %s, with params %s',
            full_url,
            method.upper(),
            endpoint,
            params)

        resp = requests.request(method, full_url, headers=self._headers, params=params)
        resp.raise_for_status()
        
        return resp.json()

    def get(self, url, headers=None, params=None):
        self._access_token, self._headers = self.make_headers()
        
        return self._make_request('GET', url, headers=self._headers, params=params)
