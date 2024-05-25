
from asyncio import format_helpers
from udi_interface import Node,LOGGER,Custom,LOG_HANDLER
import sys,time,logging,json,os,markdown2
from threading import Thread,Lock
from datetime import datetime, timedelta
from pgSession import pgSession

from nodes import Sensor

class Controller(Node):

    def __init__(self, poly, primary, address, name):
        LOGGER.info('WirelessTag Controller: Initializing')
        super(Controller, self).__init__(poly, primary, address, name)
        # These start in threads cause they take a while
        self.ready = False
        self.first_run = True
        self.authorized = False
        self.token = False
        self.sensors = {}
        self.cfg_longPoll = None
        self.cfg_shortPoll = None
        self.num_sensors = 0
        self.num_sensors_poll = 0
        self.nkey_sp = 'shortPoll'
        self.queue_lock = Lock() # Lock for syncronizing acress threads
        self.n_queue = []
        self.Notices         = Custom(poly, 'notices')
        self.Data            = Custom(poly, 'customdata')
        self.Params          = Custom(poly, 'customparams')
        self.Notices         = Custom(poly, 'notices')
        #self.TypedParameters = Custom(poly, 'customtypedparams')
        #self.TypedData       = Custom(poly, 'customtypeddata')
        poly.subscribe(poly.START,             self.handler_start, address)
        poly.subscribe(poly.POLL,              self.handler_poll)
        poly.subscribe(poly.DISCOVER,          self.discover)
        poly.subscribe(poly.STOP,              self.handler_stop)
        poly.subscribe(poly.CUSTOMPARAMS,      self.handler_params)
        poly.subscribe(poly.CUSTOMDATA,        self.handler_data)
        #poly.subscribe(poly.CUSTOMTYPEDPARAMS, self.handler_typed_params)
        #poly.subscribe(poly.CUSTOMTYPEDDATA,   self.handler_typed_data)
        poly.subscribe(poly.LOGLEVEL,          self.handler_log_level)
        poly.subscribe(poly.CONFIG,            self.handler_config)
        poly.subscribe(poly.CONFIGDONE,        self.handler_config_done)
        poly.subscribe(poly.CUSTOMNS,          self.handler_nsdata)
        poly.subscribe(poly.OAUTH,             self.handler_oauth)
        poly.subscribe(poly.ADDNODEDONE,       self.node_queue)
        self.client_id              = None
        self.client_secret          = None
        self.handler_start_st       = None
        self.handler_config_done_st = None
        self.handler_params_st      = None
        self.handler_data_st        = None
        self.handler_nsdata_st      = None
        self.discover_st            = None
        self.api_get_wait_until     = False
        self.api_get_wait_notified  = False
        self.change_node_names      = False

        poly.ready()
        poly.addNode(self, conn_status="ST")

    '''
    node_queue() and wait_for_node_event() create a simple way to wait
    for a node to be created.  The nodeAdd() API call is asynchronous and
    will return before the node is fully created. Using this, we can wait
    until it is fully created before we try to use it.
    '''
    def node_queue(self, data):
        self.n_queue.append(data['address'])
        # Now that node is done, do what is necessary
        if (data['address'] == self.address):
            self.add_node_done()

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def add_node(self,node):
        # See if we need to check for node name changes where ELK is the source
        address = node.address
        LOGGER.debug(f"Adding: {node.name}")
        self.poly.addNode(node, rename=self.change_node_names)
        self.wait_for_node_done()
        gnode = self.poly.getNode(address)
        if gnode is None:
            LOGGER.error('Failed to add node address')
        return node

    def add_node_done(self):
        LOGGER.debug("start")
        # https://accounts-api.airthings.com/v1/token
        self.start_session()
        self.authorize()
        # if initial discover failed, try again on next poll
        self.discover_st = self.discover()
        self.first_run = False
        LOGGER.debug("done")

    def handler_start(self):
        LOGGER.info('enter')
        self.poly.Notices.clear()
        # Start a heartbeat right away
        self.hb = 0
        self.heartbeat()
        LOGGER.info(f"Started Airthings-Consumer NodeServer {self.poly.serverdata['version']}")
        cnt = 10
        while (self.handler_params_st is None or self.handler_config_done_st is None
            or self.handler_nsdata_st is None or self.handler_data_st is None) and cnt > 0:
            LOGGER.warning(f'Waiting for all to be loaded config={self.handler_config_done_st} params={self.handler_params_st} data={self.handler_data_st} nsdata={self.handler_nsdata_st}... cnt={cnt}')
            time.sleep(1)
            cnt -= 1
        self.set_auth_st(False)
        configurationHelp = './CONFIG.md'
        if os.path.isfile(configurationHelp):
            cfgdoc = markdown2.markdown_path(configurationHelp)
            self.poly.setCustomParamsDoc(cfgdoc)
        self.poly.updateProfile()
        self.ready = True
        LOGGER.info('done')

    def handler_config(self,data):
        LOGGER.info(f'enter data={data}')
        self.cfg_longPoll = int(data['longPoll'])
        self.cfg_shortPoll = int(data['shortPoll'])
        self.check_short_poll()
        self.handler_config_st = True
        LOGGER.info('done')

    def handler_config_done(self):
        LOGGER.info('enter')
        self.handler_config_done_st = True
        LOGGER.info('done')

    def handler_poll(self, polltype):
        if self.token is False:
            LOGGER.warning(f"Not able to poll yet, token={self.token}")
            return False
        if polltype == 'longPoll':
            self.longPoll()
        elif polltype == 'shortPoll':
            self.shortPoll()

    def shortPoll(self):
        LOGGER.info('enter')
        self._query_all()
        LOGGER.info('exit')

    def longPoll(self):
        self.heartbeat()

    def heartbeat(self):
        LOGGER.debug('hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def query(self):
        self.reportDrivers()

    def query_all(self,opt):
        self._query_all()
        self.reportDrivers()

    def _query_all(self):
        LOGGER.info('enter')
        # Make sure we are still authorized
        if self.authorize():
            cnt = 0
            if self.discover_st is not True:
                self.discover_st = self.discover()
            for node in self.poly.nodes():
                if node.address != self.address:
                    node.shortPoll()
                    if node.poll_device():
                        cnt += 1
            self.set_sensors_poll(cnt)
        LOGGER.info('exit')

    # *****************************************************************************
    #
    # Session methods
    #
    def start_session(self):
        LOGGER.debug("start")
        self.session = pgSession(self,LOGGER,'https://accounts-api.airthings.com',debug_level=1)
        LOGGER.debug("done")

    def api_get(self,path,params={}):
        if not self.authorized:
            LOGGER.error("Not Authorized")
        if self.api_get_wait_until is not False:
            if self.api_get_wait_until > datetime.now():
                # Only notify once per wait session
                if not self.api_get_wait_notified:
                    LOGGER.warning(f"API Rate limit exceeded, waiting until {self.api_get_wait_until} to query the Airthings service again.")
                    self.api_get_wait_notified = True
                return None
            LOGGER.warning("API Rate limit pause is over, trying again...")
            self.api_get_wait_until = False
        res = self.session.get(
            path,params,
            auth='{} {}'.format(self.token_type,self.token),
            url="https://ext-api.airthings.com/v1/",
        )
        if res is False:
            return res
        if res['data'] is False:
            return False
        #
        # Profile only supports these specific errors, any others set it to False
        # res={'code': 401, 'data': {'message': 'Unauthorized'}}
        # res={'code': 429, 'data': {'error': 'TOO_MANY_REQUESTS', 'error_description': 'Rate limit on API exceeded', 'error_code': 1070}}
        LOGGER.debug('res={}'.format(res))
        code = res['code']
        if code == 200:
            self.set_server_st(1)
            return res
        if 'error_code' in res['data']:
            if res['data']['error_code'] == 1070:
                self.set_server_st(res['data']['error_code'])
            else:
                LOGGER.error(f"Unknown error code {res['data']['error_code']} in {res['data']}")
                self.set_server_st(0)
        else:
            if code == 401:
                self.set_server_st(code)
            else:
                LOGGER.error(f"Unknown error code {code}")
                self.set_server_st(0)
        # We get thuis, don't try again for 5 minutes?
        if code == 429 and res['data']['error'] == 'TOO_MANY_REQUESTS' and self.api_get_wait_until is False:
            self.api_get_wait_until = datetime. now() + timedelta(seconds=60 * 5)
            self.api_get_wait_notified = False
        return res

    def authorize(self):
        LOGGER.debug("enter")
        if self.authorized:
            # Check if expiring before next longpoll
            LOGGER.debug(f"Token Expires: {self.token_expires_dt} currently: {datetime.now()}")
            if self.token_expires_dt > datetime.now():
                LOGGER.debug("exit")
                return True
            LOGGER.debug(f'Need to re-authorize...')
        st = True
        self.Notices.delete('client_id')
        if self.client_id is None:
            msg = f"Can not authorize, client_id={self.client_id}"
            LOGGER.error(msg)
            self.Notices['client_id'] = msg
            st = False
        self.Notices.delete('client_secret')
        if self.client_secret is None:
            msg = f"Can not authorize, client_secret={self.client_secret}"
            LOGGER.error(msg)
            self.Notices['client_secret'] = msg
            st = False
        if st is False:
            return st
        st = self.session.post('v1/token',
            {
                "grant_type":"client_credentials",
                "client_id":self.client_id,
                "client_secret":self.client_secret,
                "scope": ["read:device:current_values"]
            }
        )
        if 'code' in st and st['code'] == 200:
            LOGGER.info("Authorization Successful")
            self.set_auth_st(True)
            self.token = st['data']['access_token']
            self.token_type = st['data']['token_type']
            self.token_expires = st['data']['expires_in']
            self.token_expires_dt = datetime. now() + timedelta(seconds=self.token_expires)
        LOGGER.debug("done")
        return True

    def devices(self):
        LOGGER.debug("start")
        st = self.api_get('devices',{})
        if st is None:
            # Waiting on timeout...
            return st
        ret = False
        if st is not False and 'code' in st and st['code'] == 200:
            ret = st['data']['devices']
        return ret

    # *****************************************************************************

    def discover(self, *args, **kwargs):
        LOGGER.debug("start")
        st = False
        msg = ''
        nkey = 'discover'
        self.Notices.delete(nkey)
        if self.handler_params_st is not True:
            msg = f"Can not discover until Params are defined. (st={self.handler_params_st})"
        if self.authorize():
            self.set_sensors(0)
            devices = self.devices()
            if devices is None:
                # Waiting for error timeout... Don't say aything
                return False
            if devices is False:
                msg = f"Will try to rediscover on next poll, devices={devices}..."
            else:
                st = True
                for device in devices:
                    self.add_device(device)
                self.check_short_poll()
        else:
            msg = "Can't discover, not authorized, will try again on next poll..."
        if msg != "":
            self.Notices[nkey] = msg
            LOGGER.warning(msg)
        return st

    def check_short_poll(self):
        rval = 30 * self.num_sensors_poll
        if int(self.cfg_shortPoll) < rval:
            # This is a unique message
            tmsg = f"Your shortPoll={self.cfg_shortPoll} is to low for {self.num_sensors_poll} polled sensors, please change to at least {rval}"
            LOGGER.warning(tmsg)
            self.Notices[self.nkey_sp] = tmsg
        else:
            self.Notices.delete(self.nkey_sp)

    def add_device(self,device):
        LOGGER.debug(f"start: {device}")
        if device['deviceType'] != "HUB":
            node = self.add_node(Sensor(self, device['id'], self.poly.getValidName(device['segment']['name']), self.units, device=device))
            if node:
                self.sensors[device['id']] = node
                self.incr_sensors()
                if node.poll_device(): 
                    self.incr_sensors_poll()
        LOGGER.debug(f"done")

    def add_existing_tag_managers(self):
        """
        Called on startup to add the tags from the config
        We can't rely on discover at startup in case the server is down, we need to add the ones we know about.
        """
        for node in self.poly.db_getNodeDrivers(''):
            if 'nodeDefId' in node:
                if node['nodeDefId'] == 'wTagManager':
                    LOGGER.info(f'node={node}')
                    address = node['address']
                    self.add_node(TagManager(self, address, node['name'], address.upper(), node_data=node))
            else:
                LOGGER.error('node has no {0}? node={1}'.format(nodedef,node))

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def handler_stop(self):
        LOGGER.debug('NodeServer stopping...')
        self.set_auth_st(False)
        self.set_server_st(0)

    #def handler_data(self,data):
    #    LOGGER.debug('enter: Loading data')
    #    self.Data.load(data)
    #    LOGGER.debug(f'Data={self.Data}')

    def handler_nsdata(self, key, data):
        LOGGER.debug(f"key={key} data={data}")
        self.handler_nsdata_st = True
        return

        self.Notices.delete(key)

        if key == 'oauth':
            try:
                self.client_id     = data['client_id']
                self.client_secret = data['client_secret']
            except:
                LOGGER.error(f'failed to parse {key} data={data}',exc_info=True)
                self.handler_nsdata_st = False
                return

        self.handler_nsdata_st = True

    def handler_oauth(self, data):
        LOGGER.debug(f"key={key} data={data}")
        return
        self.Notices.delete('oauth')


    def handler_data(self,data):
        LOGGER.debug(f'enter: Loading data {data}')
        self.Data.load(data)
        self.handler_data_st = True

    def handler_params(self,data):
        LOGGER.debug("Enter data={}".format(data))
        #self.Notices.clear()

        # Our defaults, make sure the exist in case user deletes one
        params = {
            'units': 'US',
            'client_id': '',
            'client_secret': "",
            'change_node_names': "false"
        }
        if data is not None:
            # Load what we have
           self.Params.load(data)

        # Assume we are good unless something bad is found
        st = True

        # Make sure all the params exist.
        for param in params:
            if data is None or not param in data:
                LOGGER.error(f'Add back missing param {param}')
                self.Params[param] = params[param]
                # Can't do anything else because we will be called again due to param change
                return

        # Make sure they all have a value that is not the default
        for param in params:
            if data[param] == "" or (data[param] == params[param] and param != 'units' and param != "change_node_names"):
                msg = f'Please define {param}'
                LOGGER.error(msg)
                self.Notices[param] = msg
                st = False
            else:
                self.Notices.delete(param)

        self.client_id     = self.Params['client_id']
        self.client_secret = self.Params['client_secret']
        self.units = self.Params['units'].upper()
        if self.units == "US" or self.units == "METRIC":
            self.Notices.delete('unitsv')
        else:
            msg = f"Units must be 'US' or 'METRIC', assuming 'US'"
            LOGGER.error(msg)
            self.Notices['unitsv'] = msg
        self.change_node_names = self.Params['change_node_names']
        self.handler_params_st = st
        if not self.first_run:
            self.discover()
        LOGGER.debug(f'exit: first_run={self.first_run} st={self.handler_params_st}')

    def handler_log_level(self,level):
        LOGGER.info(f'enter: level={level}')
        if level['level'] < 10:
            LOGGER.info("Setting basic config to DEBUG...")
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
            slevel = logging.DEBUG
        else:
            LOGGER.info("Setting basic config to WARNING...")
            LOG_HANDLER.set_basic_config(True,logging.WARNING)
            slevel = logging.WARNING
        #logging.getLogger('requests').setLevel(slevel)
        #logging.getLogger('urllib3').setLevel(slevel)
        LOGGER.info(f'exit: slevel={slevel}')

    """
    Set Functions
    """
    def set_auth_st(self,val):
        self.authorized = val
        ival = 1 if val else 0
        LOGGER.debug("{}:set_auth_st: {}={}".format(self.address,val,ival))
        self.setDriver('GV1',ival,uom=2)

    def set_sensors(self,val):
        self.num_sensors = val
        self.setDriver('GV2', val)

    def incr_sensors(self):
        self.set_sensors(self.num_sensors + 1)

    def set_sensors_poll(self,val):
        self.num_sensors_poll = val
        self.setDriver('GV4', val)

    def incr_sensors_poll(self):
        self.set_sensors_poll(self.num_sensors_poll + 1)

    def set_server_st(self,val):
        self.setDriver('GV3', val)

    """
    Command Functions
    """

    def cmd_set_managers(self,command):
        val = command.get('value')
        LOGGER.info(val)
        self.set_managers(val)

    """
    Node Definitions
    """
    id = 'Controller'
    commands = {
        'QUERY': query,
        'QUERY_ALL': query_all,
    }
    drivers = [
        {'driver': 'ST',  'value': 1, 'uom': 25, "name": "NodeServer Online"},
        {'driver': 'GV1', 'value': 0, 'uom': 2,  "name": "Authorized"},
        {'driver': 'GV2', 'value': 0, 'uom': 56, "name": "Total Number of Sensors"},
        {'driver': 'GV4', 'value': 0, 'uom': 56, "name": "Number of Polling Sensors"},
        {'driver': 'GV3', 'value': 0, 'uom': 25, "name": "Airthings Server Status"},
    ]
