#!/usr/bin/env python
import hashlib
import json
import sys
import urllib

import requests

class ClientError(Exception):
    pass

class Client(object):
    def __init__(self, endpoint, user_id, api_secret):
        self.endpoint = endpoint
        self.user_id = user_id
        self.api_secret = api_secret

    def order(self, waffle_name, coords, count=1):
        """Order one or more waffles."""
        params = {'waffle': waffle_name, 'count': count,
                  'lat': coords[0], 'long': coords[1]}
        return self.api_call('/orders', params)

    def api_call(self, path, params, debug_response=False):
        """Make an API call with parameters to the specified path."""
        body = self._make_post(params)
        resp = requests.post(self.endpoint + path, data=body)

        # for debugging
        if debug_response:
            return resp

        # try to decode response as json
        data = None
        if resp.headers['content-type'] == 'application/json':
            try:
                data = json.loads(resp.text)
            except ValueError:
                pass
            else:
                # raise error message if any
                error = data.get('error')
                if error:
                    raise ClientError(error)

        # raise error on non-200 status codes
        resp.raise_for_status()

        # return response data decoded from JSON or just response body
        return data or resp.text

    def _make_post(self, params):
        params['user_id'] = self.user_id
        body = urllib.urlencode(params)

        sig = self._signature(body)
        body += '|sig:' + sig

        return body

    def _signature(self, message):
        h = hashlib.sha1()
        h.update(self.api_secret + message)
        return h.hexdigest()

if __name__ == '__main__':
    if len(sys.argv) != 7:
        print 'usage: client.py ENDPOINT USER_ID SECRET WAFFLE LAT LONG'
        sys.exit(1)

    c = Client(*sys.argv[1:4])
    print c.order(sys.argv[4], sys.argv[5:7])
