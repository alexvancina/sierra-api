import json
import time
from base64 import b64encode
from pathlib import Path
import requests

class SierraAPI:

    # Sierra API client

    def __init__(self, apiURL, apiKey, apiSecret, debugMode=False):
        self.apiURL = apiURL
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.debugMode = debugMode

        self.token = None
        self.tokenExpiration = 0
        self.tokenMinLife = 10

        self.cacheFile = "token.json"

        cacheFile = Path(self.cacheFile)
        if cacheFile.is_file():
            with open(str(cacheFile), 'r') as file:
                token = json.load(file)
                self.token = token['access_token']
                self.tokenExpiration = token['expiration_time']

    def getToken(self):

        if (self.tokenExpiration - time.time()) < self.tokenMinLife:
            apiEncodedKey = b64encode(str.encode(self.apiKey + ':' + self.apiSecret))
            response = requests.post(self.apiURL + 'token',
                headers={'Authorization': 'Basic ' + str(apiEncodedKey, 'utf-8')},
                data={'grant_type': 'client_credentials'})

            self.token = response.json()['access_token']
            self.tokenExpiration = time.time() + response.json()['expires_in']

            if self.cacheFile:
                data = response.json()
                data['expiration_time'] = self.tokenExpiration
                cacheFile = Path(self.cacheFile)
                cacheFile.write_text(json.dumps(data, indent=4))

        if self.debugMode:
            print('Token: ' + self.token)
            print('Expires in: ' + str(self.tokenExpiration - time.time()))

    def get(self, path, params={}):
        response = self.request('GET', path, params=params)
        return response

    def delete(self, path, params={}, data={}):
        response = self.request('DELETE', path, params=params, data=data)
        return response

    def post(self, path, params={}, data={}):
        response = self.request('POST', path, params=params, data=data)
        return response

    def put(self, path, params={}, data={}):
        response = self.request('PUT', path, params=params, data=data)
        return response

    def request(self, method, path, params={}, data={}):
        self.getToken()

        headers={'Authorization': 'Bearer ' + self.token}

        # If the path doesn't begin with https://, append it to the API base URL
        if not path.startswith('https://'):
            path = self.apiURL + path

        if method == 'GET':
            response = requests.get(path, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(path, headers=headers, params=params, data=data)
        elif method == 'PUT':
            response = requests.put(path, headers=headers, params=params, data=data)
        elif method == 'DELETE':
            response = requests.delete(path, headers=headers, params=params, data=data)
        else:
            exception = ValueError()
            exception.strerror = 'Error: Invalid HTTP request type ' + method 
            raise exception 

        if self.debugMode:
            try:
                print(json.dumps(response.json(), indent=4))
            except:
                print("Empty response")

        return response