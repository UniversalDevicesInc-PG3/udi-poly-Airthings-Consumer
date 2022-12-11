"""
Work on makeing this a generic session handler for all Polyglot's
"""

import requests,json,warnings
from requests.adapters import HTTPAdapter, Retry

class pgSession():

    def __init__(self,parent,logger,url,debug_level=-1):
        self.parent = parent
        self.logger = logger
        self.url    = url
        self.debug_level = debug_level
        # Create our session
        self.session = requests.Session()
        # Allow for retries on all connections.
        retries = 30
        backoff_factor = .3
        status_force_list = (500, 502, 503, 504, 505, 506)
        adapter = HTTPAdapter(
                    max_retries=Retry(
                        total=retries,
                        read=retries,
                        connect=retries,
                        backoff_factor=backoff_factor,
                        status_forcelist=status_force_list,
                    )
                )
        for prefix in "http://", "https://":
            self.session.mount(prefix, adapter)

    def close(self):
        self.session.close()
        return

    # TODO: auth and api_key should be passed as a header list
    def get(self,path,params={},auth=None,api_key=None,url=None):
        if url is None:
            url = self.url
        url += '/' + path
        # No speical headers?
        headers = {
            "Content-Type": "application/json"
            #"Accept": "application/json"
        }
        if auth is not None:
            headers['Authorization'] = auth
        if api_key is not None:
            headers['x-api-key'] = api_key
        self.logger.debug( "headers={}".format(headers))
        self.session.headers.update(headers)
        self.logger.debug(f"Sending: get: url={url} params={params} headers={headers}")
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=(61,10)
            )
            #self.logger.debug( "url={}".format(response.url))
        # This is supposed to catch all request excpetions.
        except requests.exceptions.RequestException as e:
            self.logger.error("Connection error for %s: %s" % (url, e))
            return False
        return(self.response(response,'get'))

    def response(self,response,name):
        fname = 'reponse:'+name
        self.logger.debug(' Got: code=%s' % (response.status_code))
        if self.debug_level <= 2:
            self.logger.debug('      text=%s' % (response.text))
        json_data = False
        st = False
        # No matter what, return the code and error
        try:
            json_data = json.loads(response.text)
        except (Exception) as err:
            # Only complain about this error if we didn't have an error above
            if st:
                self.logger.error('Failed to convert to json {0}: {1}'.format(response.text,err), exc_info=True)
            json_data = {'message': None}
        if response.status_code == 200:
            self.logger.debug(' All good!')
            st = True
        elif response.status_code == 400:
            self.logger.error("Bad request: %s: text: %s" % (response.url,response.text) )
        elif response.status_code == 403:
            self.logger.error("Forbidden: %s: text: %s" % (response.url,json_data['message']) )
        elif response.status_code == 404:
            self.logger.error("Not Found: %s: text: %s" % (response.url,response.text) )
        elif response.status_code == 401:
            # Authentication error
            self.logger.error("Unauthorized: %s: text: %s" % (response.url,response.text) )
        elif response.status_code == 429:
            # Server specifc error, don't whine about it, let the caller handle it
            pass
        elif response.status_code == 500:
            self.logger.error("Server Error: %s %s: text: %s" % (response.status_code,response.url,response.text) )
        elif response.status_code == 522:
            self.logger.error("Timeout Error: %s %s: text: %s" % (response.status_code,response.url,response.text) )
        else:
            self.logger.error("Unknown response %s: %s %s" % (response.status_code, response.url, response.text) )
            self.logger.error("Check AirThings system status")
        return { 'code': response.status_code, 'data': json_data }

    def post(self,path,payload,api_key=None,content="json"):
        self.logger.debug(f'start: path={path} payload={payload} api_key={api_key} content={content}')
        # No speical headers?
        headers = {
        }
        if api_key is not None:
            headers['x-api-key'] = api_key
        url = "{}/{}".format(self.url,path)
        if content == "json":
            headers['Content-Type'] = 'application/json'
            try:
                payload_out = json.dumps(payload)
            except Exception as e:
                self.logger.error('Error converting to json: {}'.format(payload))
                return False
        elif content == "urlencode":
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            payload_out = urlencode(payload)
        else:
            LOGGER.error("Unknown content={content}, must be json or urlencode")
            return { 'status': False, 'status_code': None, 'code': None }
        self.logger.debug("Sending: url={0} payload={1}".format(url,payload_out))
        self.logger.debug( "headers={}".format(headers))
        self.session.headers.update(headers)
        try:
            response = self.session.post(
                url,
                data=payload_out,
                timeout=(61,10)
            )
        # This is supposed to catch all request excpetions.
        except requests.exceptions.RequestException as e:
            self.logger.error("Connection error for %s: %s" % (url, e))
            return { 'status': False, 'status_code': None, 'code': None }
        return(self.response(response,'post'))

    def delete(self,path,auth=None):
        url = "https://{}{}/{}".format(self.host,self.port_s,path)
        self.logger.debug("Sending: url={0}".format(url))
        # No speical headers?
        headers = {
            "Content-Type": "application/json"
        }
        if auth is not None:
            headers['Authorization'] = auth
        if self.debug_level <= 1:
            self.logger.debug("headers={}".format(headers))
        # Some are getting unclosed socket warnings due to garbage collection?? no idea why, so just ignore them since we dont' care
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<socket.socket.*>")
        #self.session.headers.update(headers)
        try:
            response = self.session.delete(
                url,
                headers=headers,
                timeout=(61,10)
            )
            if self.debug_level <= 1:
                self.logger.debug("url={}".format(response.url))
            self.logger.debug('delete got: {}'.format(response))
        # This is supposed to catch all request excpetions.
        except requests.exceptions.RequestException as e:
            self.logger.error("Connection error for %s: %s" % (url, e))
            return False
        return(self.response(response,'delete'))

