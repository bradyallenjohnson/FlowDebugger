'''
Created on Nov 17, 2014

@author: Brady Johnson
'''

import inspect

#
# The FlowEntryAction classes are used to parse the "ovs-ofctl dump-flows" action output.
# The parsing is done via the derived class Python Properties. For each output field
# to be parsed, a corresponding Python property should exist: the property name should
# be exactly the same as the field to be parsed.
# Then the property names are stored in the FlowEntryActionFactory._flow_match_setters
# dictionary and the corresponding value is a list: [class type to instantiate, property setter to call]
# This way, we dont need big if/else checks, all the string checking is done via the 
# Python dictionary.
# To print a particular FlowEntryMatches, the __str__() built-in function has been
# overridden to print all properties using the property fget function. This way, we
# dont need __str__() functions in all the derived classes.
#  

# TODO the FlowEntryActionFactory and FlowEntryMatchesFactory classes  
#      basically do the same thing consider combining them into one

class FlowEntryActionFactory(object):
    _flow_action_setters = {} # dictionary {'key' : [class type, property setter func]}
    _initialized = False

    @staticmethod
    def _init_flow_action_dict():
        for flow_entry_action in [FlowEntryActionSwitch(), FlowEntryActionSwitchPort(), FlowEntryActionSetField()]:
            attributes = inspect.getmembers(type(flow_entry_action), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
            for attr in attributes:
                if not(attr[0].startswith('__') and attr[0].endswith('__')):
                    FlowEntryActionFactory._flow_action_setters[attr[0]] = [type(flow_entry_action), attr[1].fset]
        FlowEntryActionFactory._initialized = True

    @staticmethod
    def parse_action(action_str):
        if not FlowEntryActionFactory._initialized:
            FlowEntryActionFactory._init_flow_action_dict()
        parser_obj_list = FlowEntryActionFactory._flow_action_setters.get(action_str.split(':')[0], [FlowEntryActionUnknown.__class__, None])
        obj = parser_obj_list[0](action_str) # instantiate the object
        if parser_obj_list[1] != None:       # call the property setter, if there is one
            parser_obj_list[1](obj, obj.action_str_value)
        else:
            print 'Cant parse: %s' % action_str

        return obj

#
# Base class for FlowEntry Actions
#
class FlowEntryAction(object):
    def __init__(self, action_str=''):
        self.action_str = action_str
        action_str_list = action_str.split(':', 1)
        self.action_str_key = action_str_list[0]
        self.action_str_value = None
        if len(action_str_list) == 2:
            self.action_str_value = action_str_list[1]

    def apply_action(self, packet_metadata):
        ''' '''

    def __str__(self):
        str_list = []
        attributes = inspect.getmembers(type(self), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
        #print 'FlowEntryAction len(attrs)=%d' % (attributes)
        for attr in attributes:
            if not(attr[0].startswith('__') and attr[0].endswith('__')) and attr[1].fget != None:
                value = attr[1].fget(self) 
                #print 'FlowEntryAction property %s=%s' % (attr[0], value)
                if value != None:
                    str_list.append('%s = %s' % (attr[0], value))
        return ', '.join(str_list) if len(str_list) > 0 else None

#
# OFS related actions not related to ports
#   Metadata, goto table, etc
#
class FlowEntryActionSwitch(FlowEntryAction):
    def __init__(self, action_str=''):
        super(FlowEntryActionSwitch, self).__init__(action_str)
        self._goto_table     = None
        self._metadata_value = None
        self._metadata_mask  = None

    def set_goto_table(self, table): self._goto_table = table
    def set_metadata(self, metadata):
        metadata_list = metadata.split('/')
        self._metadata_value = metadata_list[0]
        self._metadata_mask  = metadata_list[1]
    def get_goto_table(self): return self._goto_table
    def get_metadata(self):   return '%s/%s' % (self._metadata_value, self._metadata_mask) if self._metadata_value != None else None
    goto_table = property(fget=get_goto_table, fset=set_goto_table)
    write_metadata = property(fget=get_metadata, fset=set_metadata)

#
# OFS port-related actions
#   output, drop, normal, enqueue, flood, all, local, in_port, etc
#
class FlowEntryActionSwitchPort(FlowEntryAction):
    def __init__(self, action_str=''):
        super(FlowEntryActionSwitchPort, self).__init__(action_str)
        self._drop    = False
        self._normal  = False  # Output the packet to the device's normal L2/L3 processing: to the OS
        self._all     = False  # Output the packet on all switch physical ports, except received port
        self._flood   = False  # Output the packet on all switch physical ports, except received port
        self._in_port = False  # Output the packet to the port it was received on
        self._local   = False  # Output the packet to the "local port"
        self._output_port = None  # Port to output the packet to
        self._packet_in = False
        self._controller_id = 0
        self._packet_in_size = 0
        self._packet_in_reason = 0

    def set_drop(self, empty):    self._drop    = True
    def set_normal(self, empty):  self._normal  = True
    def set_all(self, empty):     self._all     = True
    def set_flood(self, empty):   self._flood   = True
    def set_in_port(self, empty): self._in_port = True
    def set_local(self, empty):   self._loacl   = True
    def set_output(self, output_port): self._output_port = output_port
    def set_controller(self, controller_str):
        self._packet_in = True
        # 2 forms for controller_str:
        #    controller(key=value...)
        #    controller[:nbytes]  same as controller() or controller(max_len=nbytes)
        if controller_str.find(':') > 0:
            self._packet_in_size = int(controller_str[len('controller:'):])
        elif controller_str.find('(') > 0:
            kv_pairs = controller_str.strip('controller(').rstrip(')').split(',')
            for pair in kv_pairs:
                kv = pair.split('=')
                if kv[0] == 'max_len':
                    self._packet_in_size = int(kv[1])
                elif kv[0] == 'reason':
                    self._packet_in_reason = int(kv[1])
                elif kv[0] == 'id':
                    self._controller_id = int(kv[1])
                else:
                    print 'Unknown controller options: %s' % pair
    def get_output(self): return self._output_port
    drop       = property(fset=set_drop)
    normal     = property(fset=set_normal)
    all        = property(fset=set_all)
    flood      = property(fset=set_flood)
    in_port    = property(fset=set_in_port)
    local      = property(fset=set_local)
    output     = property(fget=get_output, fset=set_output)
    controller = property(fset=set_controller)


#
# Set packet fields Actions
#
class FlowEntryActionSetField(FlowEntryAction):
    def __init__(self, action_str=''):
        super(FlowEntryActionSetField, self).__init__(action_str)
        self.set_field_key = ''
        self.set_field_value = ''
    def set_set_field(self, set_field_str):
        field_list = set_field_str.split('->')
        self.set_field_key = field_list[1]
        self.set_field_value = field_list[0]
    def get_set_field(self): return '%s - %s' % (self.set_field_key, self.set_field_value)
    set_field  = property(fget=get_set_field, fset=set_set_field)

#
# Mod actions:
#  mod_vlan_id, mod_vlan_pcp, mod_dl_src/dst, mod_nw_src/dst, mod_tp_src/dst, mod_nw_tos
#  push_vlan, push_mpls

class FlowEntryActionUnknown(FlowEntryAction):
    def __init__(self, action_str=''):
        super(FlowEntryActionUnknown, self).__init__(action_str)
