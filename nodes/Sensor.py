"""
This is a NodeServer for CAO Gadgets Wireless Sensor Tags for Polyglot v2 written in Python3
by JimBoCA jimboca3@gmail.com
"""

from udi_interface import Node,LOGGER
import sys
import time
import re
from node_functions import myfloat,CtoF

DLEV = 0

class Sensor(Node):

    def __init__(self, controller, serial, name, units, device=None):
        #
        # start: {'id': '2930024814', 'deviceType': 'WAVE_PLUS', 
        # 'sensors': ['radonShortTermAvg', 'temp', 'humidity', 'pressure', 'co2', 'voc'], 
        # 'segment': {'id': 'd480acc5-ab3b-4ee3-9595-0207ec1c5741', 'name': 'Family Room', 'started': '2020-02-09T02:06:00', 'active': True}, 
        # 'location': {'id': '74d065d0-694f-45d0-9f3b-50453198b2f8', 'name': 'Home'}}
        #
        LOGGER.debug(f'serial={serial} name={name} units={units} device={device}')
        self.serial = serial
        address = f"s_{serial}"
        self.id = 'Sensor' # Until we figure out the uom?
        self.name = name
        self.units = units
        self.controller = controller
        self.device = device
        if device is None:
            # TODO: This section not being used yet, need to an add_existing_sensors in Controller...
            # Existing device, get the list of drivers...
            #
            # An existing node,
            LOGGER.debug('Existing node...')
            # We need to pull info from existing tags to know what they are.
            node_data = self.controller.poly.db_getNodeDrivers(address)
            LOGGER.debug(f"node_data={node_data}")
            dv = dict()
            for driver in node_data:
                dv[driver['driver']] = driver['value']
            if 'UOM' in dv:
                self.tag_uom = dv['UOM']
            else:
                LOGGER.error('No tag_uom (UOM)')
                self.tag_uom = -1
            # tag_id = GPV
            if 'GPV' in dv:
                tag_id = dv['GPV']
            else:
                LOGGER.error('No tag_id (GPV) in node_data={0}'.format(node_data))
                return False
            # tag_type = GV1
            if 'GV1' in dv:
                tag_type = dv['GV1']
            else:
                LOGGER.error('No tag_type (GV1) in node_data={0}'.format(node_data))
                return False
        else:
            LOGGER.debug('New node')
        self.name = name
        #
        # C or F?
        # Fix our temp_uom in drivers
        # This won't change an existing tag, only new ones.
        #
        # TODO:  test changing it by forcing update?
        # temp:   Curent temperature (17=F 4=C)
        temp_uom = 4 if self.units == "METRIC" else 17
        dv = [
            {'driver': 'ST',      'value': 0, 'uom': 2},
            {'driver': 'CLITEMP', 'value': 0, 'uom': temp_uom},
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},
            {'driver': 'CO2LVL', 'value': 0, 'uom': 54},
            {'driver': 'BARPRES', 'value': 0, 'uom': 56},
            {'driver': 'GV1', 'value': 0, 'uom': 56}, # radon
            {'driver': 'GV2', 'value': 0, 'uom': 56}, # time
            {'driver': 'GV3', 'value': 0, 'uom': 56}, # rssi
            {'driver': 'GV4', 'value': 0, 'uom': 56}, # voc
            {'driver': 'VOCLVL', 'value': 0, 'uom': 96}, # voc level name
        ]
        dv.append({'driver': 'BATLVL',  'value': 0, 'uom': 51})
        #dv.append({'driver': 'CLIHUM',  'value': 0, 'uom': 22})
        self.drivers = dv
        controller.poly.subscribe(controller.poly.START,             self.handler_start, address) 
        super(Sensor, self).__init__(controller.poly, controller.address, address, name)
        LOGGER.debug('done')

    def handler_start(self):
        LOGGER.debug('enter')
#        if self.controller.update_profile:
#            # Drivers were updated, need to query
#            self.query()
#        else:
#            # Otherwise just report previous values
#            self.reportDrivers()
        self.set_st(self.device['segment']['active'])
        self.query()
        LOGGER.debug('exit')

    def shortPoll(self):
        LOGGER.info('enter')
        self.query(force=False,authorize=False)
        LOGGER.info('exit')

    def query(self,force=True,authorize=True):
        LOGGER.info('enter')
        if authorize:
            # Check that we are authorized
            self.controller.authorize()
        # res={'code': 200, 'data': {'data': {'battery': 100, 'co2': 570.0, 'humidity': 43.0, 'pressure': 996.3, 'radonShortTermAvg': 10.0, 'rssi': -63, 'temp': 25.6, 'time': 1656884420, 'voc': 138.0, 'relayDeviceType': 'hub'}}}
        st = self.controller.api_get(f"devices/{self.serial}/latest-samples")
        if st is False:
            return False
        if st['code'] == 200:
            data = st['data']['data']
            for param in data:
                if param == 'battery':
                    self.set_battery(data[param])
                elif param == 'co2':
                    self.set_co2(data[param])
                elif param == 'humidity':
                    self.set_hum(data[param])
                elif param == 'pressure':
                    self.set_pressure(data[param])
                elif param == 'radonShortTermAvg':
                    self.set_radon(data[param])
                elif param == 'relayDeviceType':
                    pass
                elif param == 'rssi':
                    self.set_rssi(data[param])
                elif param == 'temp':
                    self.set_temp(data[param])
                elif param == 'time':
                    self.set_time(data[param])
                elif param == 'voc':
                    self.set_voc(data[param])
                else:
                    LOGGER.warning(f"Unknown param {param}={data[param]}")
        LOGGER.info('exit')

    """
    Set Functions
    """
    def set_st(self,val):
        self.authorized = val
        ival = 1 if val else 0
        LOGGER.debug("{}:set_st: {}={}".format(self.address,val,ival))
        self.setDriver('ST',ival,uom=2)

    def set_battery(self,value,force=False):
        LOGGER.debug('{0}'.format(value))
        self.setDriver('BATLVL', int(value))

    def set_co2(self,value):
        LOGGER.debug('{0}'.format(value))
        self.setDriver('CO2LVL', myfloat(value,1))

    def set_hum(self,value):
        LOGGER.debug('{0}'.format(value))
        self.setDriver('CLIHUM', myfloat(value,1))

    def set_pressure(self,value):
        LOGGER.debug('{0}'.format(value))
        self.setDriver('BARPRES', myfloat(value,1))

    # One pCi/L is equivalent to 37 Bq/m3.
    def set_radon(self,value):
        LOGGER.debug('{0}'.format(value))
        if self.units == "US":
            self.setDriver('GV1', myfloat(value/37,1))
        else:
            self.setDriver('GV1', myfloat(value,1))

    def set_rssi(self,value):
        LOGGER.debug('{0}'.format(value))
        self.setDriver('GV3', int(value))

    # (17=F 4=C)
    def set_temp(self,value):
        LOGGER.debug('{0}'.format(value))
        if self.units == "US":
            self.setDriver('CLITEMP', myfloat(CtoF(value),1), uom=17)
        else:
            self.setDriver('CLITEMP', myfloat(value,1), uom=4)

    def set_time(self,value):
        LOGGER.debug('{0}'.format(value))
        self.setDriver('GV2', int(value))

    def set_voc(self,value):
        LOGGER.debug('{0}'.format(value))
        self.setDriver('GV4', myfloat(value,1))
        self.set_voc_level(value)
    
    #96 = VOC Level
    #  1 - Clean
    #  2 - Slightly Polluted
    #  3 - Moderately Polluted
    #  4 - Highly Polluted
    def set_voc_level(self,value):
        LOGGER.debug('{0}'.format(value))
        if value < 250:
            lvl = 1
        elif value < 500:
            lvl = 2
        elif value < 2000:
            lvl = 3
        else:
            lvl = 4
        self.setDriver('VOCLVL',lvl)

    """
    """

    commands = {
        'QUERY': query,
    }
