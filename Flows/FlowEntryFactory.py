'''
Created on Nov 24, 2014

@author: Brady Johnson
'''

import inspect

from Flows.FlowEntries import FlowEntry
from Flows.FlowEntryActions import FlowEntryActionSwitch, FlowEntryActionSwitchPort, FlowEntryActionSetField, FlowEntryActionUnknown, FlowEntryActionMod
from Flows.FlowEntryMatches import FlowEntryMatchSwitch, FlowEntryMatchLayer2, FlowEntryMatchLayer3, FlowEntryMatchLayer4, FlowEntryMatchUnknown

class FlowEntryFactory(object):

    # Static variables
    _flow_match_setters = {} # dictionary {'key' : [class type, property setter func]}
    _flow_action_setters = {} # dictionary {'key' : [class type, property setter func]}
    _flow_action_initialized = False
    _flow_match_initialized = False
    COOKIE_STR         =  'cookie='
    DURATION_STR       =  'duration='
    TABLE_STR          =  'table='
    NPACKETS_STR       =  'n_packets='
    NBYTES_STR         =  'n_bytes='
    SEND_FLOW_REM_STR  =  'senf_flow_rem'
    ACTIONS_STR        =  'actions='

    # TODO _init_flow_match_dict() and _init_flow_action_dict() do exactly the same thing, but with different classes
    #      either those from FlowEntryMatches.py or FlowEntryActions.py, consider simplifying and removing duplicate code
    # TODO same goes for _parse_match() and _parse_action()

    @staticmethod
    def _init_flow_match_dict():
        # The Python properties of each of these FlowEntryMatch* classes is considered a parseable match entry
        for flow_entry_match in [FlowEntryMatchSwitch(), FlowEntryMatchLayer2(), FlowEntryMatchLayer3(), FlowEntryMatchLayer4()]:
            attributes = inspect.getmembers(type(flow_entry_match), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
            for attr in attributes:
                if not(attr[0].startswith('__') and attr[0].endswith('__')):
                    FlowEntryFactory._flow_match_setters[attr[0]] = [type(flow_entry_match), attr[1].fset]
        FlowEntryFactory._flow_match_initialized = True

    @staticmethod
    def _init_flow_action_dict():
        # The Python properties of each of these FlowEntryAction* classes is considered a parseable action entry
        for flow_entry_action in [FlowEntryActionSwitch(), FlowEntryActionSwitchPort(), FlowEntryActionSetField(), FlowEntryActionMod()]:
            attributes = inspect.getmembers(type(flow_entry_action), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
            for attr in attributes:
                if not(attr[0].startswith('__') and attr[0].endswith('__')):
                    FlowEntryFactory._flow_action_setters[attr[0]] = [type(flow_entry_action), attr[1].fset]
        FlowEntryFactory._flow_action_initialized = True

    @staticmethod
    def _parse_match(match_str):
        if not FlowEntryFactory._flow_match_initialized:
            FlowEntryFactory._init_flow_match_dict()
        parser_obj_list = FlowEntryFactory._flow_match_setters.get(match_str.split('=')[0], [FlowEntryMatchUnknown.__class__, None])
        obj = parser_obj_list[0](match_str) # instantiate the object
        if parser_obj_list[1]:              # call the property setter, if there is one
            parser_obj_list[1](obj, obj.match_str_value)
        else:
            print 'Cant parse: %s' % match_str

        return obj

    @staticmethod
    def _parse_action(action_str):
        if not FlowEntryFactory._flow_action_initialized:
            FlowEntryFactory._init_flow_action_dict()
        parser_obj_list = FlowEntryFactory._flow_action_setters.get(action_str.split(':')[0], [FlowEntryActionUnknown.__class__, None])
        obj = parser_obj_list[0](action_str) # instantiate the object
        if parser_obj_list[1]:               # call the property setter, if there is one
            parser_obj_list[1](obj, obj.action_str_value)
        else:
            print 'Cant parse: %s' % action_str

        return obj

    @staticmethod
    def _parse_item(item_key, item_str):
        value = item_str
        if len(item_key) > 0:
            value = item_str.partition(item_key)[2]

        return value.rstrip(',')

    @staticmethod
    def parse_entry(line):
        '''
        Expecting one of the following formats:
          cookie=0x0, duration=1573.875s, table=0, n_packets=2, n_bytes=152, send_flow_rem priority=10 actions=goto_table:1
          cookie=0xa, duration=1573.091s, table=1, n_packets=0, n_bytes=0, priority=256,ip,nw_src=172.16.150.134 actions=write_metadata:0x3e/0xfff,goto_table:2
          cookie=0x0, duration=243628.614s, table=0, n_packets=251762, n_bytes=18340623, priority=0 actions=NORMAL
          cookie=0x0, duration=218.554s, table=0, n_packets=0, n_bytes=0, ip,in_port=2 actions=output:1
        '''

        str_list = line.split(' ')

        flow_entry = FlowEntry()
        flow_entry.cookie_    =  FlowEntryFactory._parse_item(FlowEntryFactory.COOKIE_STR,        str_list[0])
        flow_entry.duration_  =  FlowEntryFactory._parse_item(FlowEntryFactory.DURATION_STR,      str_list[1])
        flow_entry.table_     =  int(FlowEntryFactory._parse_item(FlowEntryFactory.TABLE_STR,     str_list[2]))
        flow_entry.n_packets_ =  int(FlowEntryFactory._parse_item(FlowEntryFactory.NPACKETS_STR,  str_list[3]))
        flow_entry.n_bytes_   =  int(FlowEntryFactory._parse_item(FlowEntryFactory.NBYTES_STR,    str_list[4]))

        # Parse the send_flow_rem, if present
        next_index = 5
        if len(str_list) == 8:
            flow_entry.send_flow_rem_ = True
            next_index = 6

        flow_entry.raw_match_   =  FlowEntryFactory._parse_item('', str_list[next_index])
        flow_entry.raw_actions_ =  FlowEntryFactory._parse_item(FlowEntryFactory.ACTIONS_STR, str_list[next_index+1])

        flow_entry.action_str_list_ =  flow_entry.raw_actions_.split(',')
        flow_entry.match_str_list_  =  flow_entry.raw_match_.split(',')
        if flow_entry.match_str_list_[0].startswith('priority='):
            flow_entry.priority_  =  int(flow_entry.match_str_list_[0].split('=')[1])
            flow_entry.match_str_list_.pop(0) # Remove the priority from the match list

        # Parse each match string into a match object
        for match_str in flow_entry.match_str_list_:
            flow_entry.match_object_list_.append(FlowEntryFactory._parse_match(match_str))

        # Parse each action string into an action object
        for action_str in flow_entry.action_str_list_:
            flow_entry.action_object_list_.append(FlowEntryFactory._parse_action(action_str))

        return flow_entry

    @staticmethod
    def get_match_object(key, value):
        if not FlowEntryFactory._flow_match_initialized:
            FlowEntryFactory._init_flow_match_dict()

        parser_obj_list = FlowEntryFactory._flow_match_setters.get(key, None)
        if not parser_obj_list:
            print 'Cant get match Object'
            return None

        obj = parser_obj_list[0]()      # instantiate the object
        if parser_obj_list[1]:          # call the property setter, if there is one
            parser_obj_list[1](obj, value)

        return obj
