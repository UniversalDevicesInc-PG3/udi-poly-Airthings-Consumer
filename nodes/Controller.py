
from udi_interface import Node,LOGGER,Custom,LOG_HANDLER
import sys,time,logging,json
from threading import Thread,Lock

from nodes import TagManager
from node_functions import get_server_data,get_valid_node_name,get_profile_info

class Controller(Node):

    def __init__(self, poly, primary, address, name):
        LOGGER.info('WirelessTag Controller: Initializing')
        super(Controller, self).__init__(poly, primary, address, name)
        # These start in threads cause they take a while
        self.ready = False
        self.first_run = True
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
        poly.subscribe(poly.ADDNODEDONE,       self.node_dequeue)
        self.client_id              = None
        self.client_secret          = None
        self.handler_start_st       = None
        self.handler_config_done_st = None
        self.handler_params_st      = None
        self.handler_data_st        = None
        self.handler_nsdata_st      = None
        poly.ready()
        poly.addNode(self, conn_status="ST")

    '''
    node_queue() and wait_for_node_event() create a simple way to wait
    for a node to be created.  The nodeAdd() API call is asynchronous and
    will return before the node is fully created. Using this, we can wait
    until it is fully created before we try to use it.
    '''
    def node_dequeue(self, data):
        LOGGER.debug(f'locking: data={data}')
        self.queue_lock.acquire()
        if self.n_queue.count(data['address']) > 0:
            self.n_queue.remove(data['address'])
        self.queue_lock.release()
        LOGGER.debug('lock released')

    def add_node(self,node):
        LOGGER.debug(f'adding node node={node.address} {node.name}')
        self.queue_lock.acquire()
        ret = False

        # See if it's already being added or exists
        if self.n_queue.count(node.address) > 0:
            LOGGER.error(f"Already waiting for node {node.address} name={node.name} to be added.")
            self.queue_lock.release()
        else:
            ret = self.poly.getNode(node.address)
            if ret is not None:
                LOGGER.error(f"Node {node.address} name={node.name} already exists.")
                self.queue_lock.release()
            else:
                # Queue it up and add it
                self.n_queue.append(node.address)
                self.queue_lock.release()
                ret = self.poly.addNode(node)
                LOGGER.debug(f'got {ret}')
                if ret is None:
                    self.node_dequeue({'address': node.address})
                    LOGGER.error(r'Failed to add {node.address} name={node.name}')
                else:
                    cnt = 0
                    while self.n_queue.count(node.address) > 0:
                        cnt += 1
                       # Warn every 5 seconds, and die after 60?
                        if cnt % 50 == 0:
                            LOGGER.warning(f"Waiting for {node.address} add to complete. Queued for {cnt / 10} seconds...")
                        if cnt > 6000:
                            LOGGER.error(f"TIMEOUT waiting for {node.address} add to complete...")
                            return False
                        time.sleep(0.1)
        LOGGER.debug(f'returning {ret}')
        return ret

    def handler_start(self):
        LOGGER.info('enter')
        self.poly.Notices.clear()
        # Start a heartbeat right away
        self.hb = 0
        self.heartbeat()

        LOGGER.info(f"Started Example JimBo NodeServer {self.poly.serverdata['version']}")
        cnt = 10
        while (self.handler_params_st is None or self.handler_config_done_st is None
            or self.handler_nsdata_st is None or self.handler_data_st is None) and cnt > 0:
            LOGGER.warning(f'Waiting for all to be loaded config={self.handler_config_done_st} params={self.handler_params_st} data={self.handler_data_st} nsdata={self.handler_nsdata_st}... cnt={cnt}')
            time.sleep(1)
            cnt -= 1
        #
        # Always need to start the REST server
        #
        #self.rest_start()
        #
        # All good?
        #
        #if self.wtServer is False:
        #    self.Notices['auth'] = f"REST Server ({self.wtServer}) not running. check Log for ERROR"
        #elif self.client_id is None:
        #    self.Notices['auth'] = "Unable to authorize, no client id returned in Node Server Data.  Check Log for ERROR"
        #elif self.oauth2_code is False:
        #    self.auth_url      = "https://www.mytaglist.com/oauth2/authorize.aspx?client_id={0}".format(self.client_id)
        #    self.Notices['auth'] = 'Click <a target="_blank" href="{0}&redirect_uri={1}/code">Authorize</a> to link your CAO Wireless Sensor Tags account'.format(self.auth_url,self.wtServer.url)
        #else:
        #    self.Notices.delete('auth')

        #self.add_existing_tag_managers()
        self.query()
        self.ready = True
        LOGGER.info('done')

    def handler_config(self,data):
        LOGGER.info(f'enter data={data}')
        self.handler_config_st = True
        LOGGER.info('done')

    def handler_config_done(self):
        LOGGER.info('enter')
        self.handler_config_done_st = True
        LOGGER.info('done')

    def handler_poll(self, polltype):
        if polltype == 'longPoll':
            self.longPoll()
        elif polltype == 'shortPoll':
            self.shortPoll()

    def shortPoll(self):
        if self.discover_thread is not None:
            if self.discover_thread.isAlive():
                LOGGER.debug('discover thread still running...')
            else:
                LOGGER.debug('discover thread is done...')
                self.discover_thread = None
        # Call short poll on the tags managers
        for node in self.poly.nodes():
            if node.id == 'wTagManager':
                node.shortPoll()

    def longPoll(self):
        LOGGER.debug('ready={}'.format(self.ready))
        if not self.ready: return False
        # For now just pinging the server to make sure it's alive
        self.is_signed_in()
        if not self.comm: return self.comm
        # Call long poll on the tags managers
        for node in self.poly.nodes():
            if node.id == 'wTagManager':
                node.longPoll()
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
        if not self.authorized('query') : return False
        self.is_signed_in()
        self.reportDrivers();
        # Don't do this on initial startup!
        for node in self.poly.nodes():
            node.reportDrivers()

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

    def discover(self, *args, **kwargs):
        """
        Example
        Do discovery here. Does not have to be called discovery. Called from example
        controller start method and from DISCOVER command recieved from ISY as an exmaple.
        """
        if not self.authorized('discover') : return False
        self.set_auth(True)
        mgd = self.get_tag_managers()
        if not 'macs' in self.Data:
            self.Data['macs'] = dict()
        if mgd['st']:
            for mgr in mgd['result']:
                LOGGER.debug("TagManager={0}".format(mgr))
                address = mgr['mac'].lower()
                node = self.get_node(address)
                if node is None:
                    self.add_node(TagManager(self, address, mgr['name'], mgr['mac'], do_discover=True))
                else:
                    LOGGER.info('Running discover on {0}'.format(node))
                    node.discover(thread=False)

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def handler_stop(self):
        LOGGER.debug('NodeServer stopped.')


    #def handler_data(self,data):
    #    LOGGER.debug('enter: Loading data')
    #    self.Data.load(data)
    #    LOGGER.debug(f'Data={self.Data}')
    def handler_nsdata(self, key, data):
        LOGGER.debug(f"key={key} data={data}")

        # Temporary, should be fixed in next version of PG3
        if key is None or data is None:
                msg = f"No NSDATA Returned by Polyglot key={key} data={data}"
                LOGGER.error(msg)
                self.Notices['nsdata'] = msg
                self.handler_nsdata_st = False
                return

        if 'nsdata' in key:
            LOGGER.info('Got nsdata update {}'.format(data))

        self.Notices.delete('nsdata')
        try:
            #jdata = json.loads(data)
            self.client_id     = data['client_id']
            self.client_secret = data['client_secret']
        except:
            LOGGER.error(f'failed to parse nsdata={data}',exc_info=True)
            self.handler_nsdata_st = False
            return
        self.handler_nsdata_st = True

    def handler_data(self,data):
        LOGGER.debug(f'enter: Loading data {data}')
        self.Data.load(data)
        self.handler_data_st = True

    def handler_params(self,params):
        LOGGER.debug(f'enter: Loading params {params}')
        self.Params.load(params)
        self.poly.Notices.clear()
        """
        Check all user params are available and valid
        """
        # Assume it's good unless it's not
        st = True
 
        LOGGER.debug(f'oauth2_code={self.oauth2_code}')

        # If it's a config change, then need to restart the REST server
        # because the auth2_code must have changed.
        if not self.first_run:
            self.discover()

        self.first_run = True

        self.handler_params_st = st
        LOGGER.debug(f'exit: st={st}')

    def set_url_config(self):
        # TODO: Should loop over tag managers, and call set_url_config on the tag manager
        for node in self.poly.nodes():
            LOGGER.debug("id={}".format(node.id))
            if not (node.id == 'wtController' or node.id == 'wTagManager'):
                node.set_url_config()

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
    def set_managers(self,val):
        self.setDriver('GV1', val)

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
    id = 'exController'
    commands = {
        'SET_MANAGERS': cmd_set_managers,
        'QUERY': query,
        'DISCOVER': discover,
    }
    drivers = [
        {'driver': 'ST',  'value': 1, 'uom': 56},
        {'driver': 'GV1', 'value': 0, 'uom': 56},  # auth: Managers
    ]
