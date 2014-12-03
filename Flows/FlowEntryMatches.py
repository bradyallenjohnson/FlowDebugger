'''
Created on Nov 6, 2014

@author: Brady Johnson
'''

import inspect

#
# The FlowEntryMatches classes are used to parse the "ovs-ofctl dump-flows" match output.
# The parsing is done via the derived class Python Properties. For each output field
# to be parsed, a corresponding Python property should exist: the property name should
# be exactly the same as the field to be parsed.
# Then the property names are stored in the FlowEntryFactory._flow_match_setters
# dictionary and the corresponding value is a list: [class type to instantiate, property setter to call]
# This way, we dont need big if/else checks, all the string checking is done via the 
# Python dictionary.
# To print a particular FlowEntryMatches, the __str__() built-in function has been
# overridden to print all properties using the property fget function. This way, we
# dont need __str__() functions in all the derived classes.
#  

#
# Base class for FlowEntry Matching
#
class FlowEntryMatches(object):
    def __init__(self, match_str='', protocol='EMPTY'):
        self.match_str_ = match_str
        self._protocol = protocol
        match_str_list = match_str.split('=')
        self.match_str_key = match_str_list[0]
        self.match_str_value = None
        if len(match_str_list) == 2:
            self.match_str_value = match_str_list[1]
        #print 'FlowEntryMatches: match_str[%s] _protocol[%s]' % (match_str, _protocol)

    @property
    def protocol(self): return self._protocol

    def __str__(self):
        str_list = []
        attributes = inspect.getmembers(type(self), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
        for attr in attributes:
            if not(attr[0].startswith('__') and attr[0].endswith('__')) and attr[1].fget:
                value = attr[1].fget(self)
                if value:
                    str_list.append('%s = %s' % (attr[0], value))
        return ', '.join(str_list)

    #
    # Compare two FlowEntryMatches objects for equality. They must both be of the same derived 
    # class type, have the same attributes set, and the attributes values must be equal
    #
    def match(self, match_rhs):
        if type(self) != type(match_rhs):
            #print '\tFlowEntryMatches.match() False: %s != %s' % (type(self), type(match_rhs))
            return False

        #print '\tFlowEntryMatches.match() checking self [%s][%s] match [%s][%s]' % (type(self), self, type(match_rhs), match_rhs)
        attributes = inspect.getmembers(type(self), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
        for attr in attributes:
            if not(attr[0].startswith('__') and attr[0].endswith('__')) and attr[1].fget:
                if not hasattr(match_rhs, attr[0]):
                    #print '\tFlowEntryMatches.match() False, %s does not have attr %s' % (type(match_rhs), attr[0])
                    return False
                if attr[1].fget(self) != attr[1].fget(match_rhs):
                    #print '\tFlowEntryMatches.match() False, %s values not equal: self [%s][%s] match [%s][%s]' % (attr[0], type(attr[1].fget(self)), attr[1].fget(self), type(attr[1].fget(match_rhs)), attr[1].fget(match_rhs))
                    return False
        #print '\tFlowEntryMatches.match() True'
        return True

    #
    # Compare if two FlowEntryMatches objects are compareable, meaning they are 
    # both of the same derived class type, they have same attributes, and the
    # attributes are set (not None).
    # For example, 2 FlowEntryMatchLayer2 objects are NOT compareable, if one has
    # dl_src set and the other has dl_dst set.
    #
    def is_compareable(self, match_rhs):
        if type(self) != type(match_rhs):
            #print '\tFlowEntryMatches.is_compareable() False: %s != %s' % (type(self), type(match_rhs))
            return False

        #print '\tFlowEntryMatches.is_compareable() checking self [%s][%s] match [%s][%s]' % (type(self), self, type(match_rhs), match_rhs)
        attributes = inspect.getmembers(type(self), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
        for attr in attributes:
            if not(attr[0].startswith('__') and attr[0].endswith('__')) and attr[1].fget:
                # Check that both have the same attributes
                if not hasattr(match_rhs, attr[0]):
                    #print '\tFlowEntryMatches.is_compareable() False, %s does not have attr %s' % (type(match_rhs), attr[0])
                    return False
                # Check that for each self.attribute that its not None in match_rhs
                if attr[1].fget(self) and not attr[1].fget(match_rhs):
                    #print '\tFlowEntryMatches.is_compareable() False, match doesnt have an attr value: [%s][%s]' % (attr[1].fget(self), attr[1].fget(match_rhs))
                    return False
        #print 'They are compareable'
        return True

    def copy_match(self, match_rhs):
        attributes = inspect.getmembers(type(self), lambda a : not(inspect.isroutine(a)) and inspect.isdatadescriptor(a))
        for attr in attributes:
            if not(attr[0].startswith('__') and attr[0].endswith('__')) and attr[1].fget:
                # Set it, only if match_rhs has the attr, self has the setter, the match_rhs getter isnt None
                if hasattr(match_rhs, attr[0]) and attr[1].fset and attr[1].fget(match_rhs):
                    attr[1].fset(self, attr[1].fget(match_rhs))
                    

#
# OpenFlow Switch matching
# TODO should metadata be included here
#
class FlowEntryMatchSwitch(FlowEntryMatches):
    def __init__(self, match_str=''):
        super(FlowEntryMatchSwitch, self).__init__(match_str, 'OFS')
        self._in_port = None
        self._out_port = None
        self._metadata_value = None
        self._metadata_mask = None

    def set_inport(self, inport):   self._in_port  = inport
    def set_outport(self, outport): self._out_port = outport
    def set_metadata(self, metadata):
        metadata_list = metadata.split('/')
        self._metadata_value = metadata_list[0]
        self._metadata_mask  = metadata_list[1]
    def get_inport(self):   return self._in_port
    def get_outport(self):  return self._out_port
    def get_metadata(self): return '%s/%s' % (self._metadata_value, self._metadata_mask) if self._metadata_value else None
    in_port  = property(fget=get_inport, fset=set_inport)
    out_port = property(fget=get_outport, fset=set_outport)
    metadata = property(fget=get_metadata, fset=set_metadata)

#
# Ethernet
#
class FlowEntryMatchLayer2(FlowEntryMatches):
    _ethertypes = {'0x0800' : 'IP', '0x0806' : 'ARP', '0x8035' : 'RARP'}
    _ethertype_names  = {'IP' : '0x0800', 'ARP' : '0x0806', 'RARP' : '0x8035'}

    def __init__(self, match_str=''):
        super(FlowEntryMatchLayer2, self).__init__(match_str, 'ETHERNET')
        self._dl_src = None
        self._dl_dst = None
        self._protocol_layer3 = ''
        self._dl_type = None
        self._dl_vlan = None     # VLAN tag
        self._dl_vlan_pcp = None # VLAN Priority Code Point

    def set_dl_src(self, dl_src): self._dl_src = dl_src
    def set_dl_dst(self, dl_dst): self._dl_dst = dl_dst
    def set_dl_vlan(self, dl_vlan): self._dl_vlan = int(dl_vlan)
    def set_dl_vlan_pcp(self, dl_vlan_pcp): self._dl_vlan = int(dl_vlan_pcp)
    # The value for this property setter isnt used 
    def set_ip(self, empty): (self._protocol_layer3, self._dl_type) = ('IP', '0x0800')
    def set_dl_type(self, dl_type):
        self._protocol_layer3 = self._ethertypes.get(dl_type, dl_type)
        self._dl_type = self._ethertype_names.get(dl_type, dl_type)
    def get_dl_src(self): return self._dl_src
    def get_dl_dst(self): return self._dl_dst
    def get_dl_vlan(self): return self._dl_vlan
    def get_dl_vlan_pcp(self): return self._dl_vlan
    def get_dl_type(self): return self._dl_type
    def get_l3_protocol(self): return self._protocol_layer3
    dl_src      = property(fget=get_dl_src, fset=set_dl_src)
    dl_dst      = property(fget=get_dl_dst, fset=set_dl_dst)
    dl_vlan     = property(fget=get_dl_vlan, fset=set_dl_vlan)
    dl_vlan_pcp = property(fget=get_dl_vlan_pcp, fset=set_dl_vlan_pcp)
    ip          = property(fset=set_ip)
    dl_type     = property(fget=get_dl_type, fset=set_dl_type)
    l3_protocol = property(fget=get_l3_protocol)

#
# IP, ICMP, IGMP
#
class FlowEntryMatchLayer3(FlowEntryMatches):
    def __init__(self, match_str=''):
        super(FlowEntryMatchLayer3, self).__init__(match_str, 'L3')
        self._nw_src = None
        self._nw_dst = None
        self._nw_tos = None
        self._protocol_layer4 = ''
        #self._nw_proto = 0
        self._nw_proto = None
        self._layer3_protocols = {'TCP' : 'IP', 'UDP' : 'IP', 'SCTP' : 'IP'}
        self._nw_protos        = {'1' : 'ICMP', '6' : 'TCP', '17' : 'UDP', '132' : 'SCTP'}
        self._nw_proto_names   = {'ICMP' : '1', 'TCP' : '6', 'UDP' : '17', 'SCTP' : '132'}
        # TODO need to add icmp_type, icmp_code
        # TODO need to add IP ecn, ttl

    def set_tcp(self, empty): (self._nw_proto, self._protocol_layer4, self._protocol) = ('6', 'TCP', 'IP')
    def set_udp(self, empty): (self._nw_proto, self._protocol_layer4, self._protocol) = ('17', 'UDP', 'IP')
    def set_nw_proto(self, nw_proto):
        self._protocol_layer4 = self._nw_protos.get(nw_proto, nw_proto)
        self._nw_proto = self._nw_proto_names.get(nw_proto, nw_proto)
        self._protocol = self._layer3_protocols.get(self._protocol_layer4, 'L3')
            
    def set_nw_src(self, nw_src): self._nw_src = nw_src
    def set_nw_dst(self, nw_dst): self._nw_dst = nw_dst
    def set_nw_tos(self, tos): self._nw_tos = tos
    def get_nw_proto(self): return self._nw_proto
    def get_nw_src(self): return self._nw_src
    def get_nw_dst(self): return self._nw_dst
    def get_nw_tos(self): return self._nw_tos
    tcp      = property(fset=set_tcp)
    udp      = property(fset=set_udp)
    nw_proto = property(fget=get_nw_proto, fset=set_nw_proto)
    nw_src   = property(fget=get_nw_src, fset=set_nw_src)
    nw_dst   = property(fget=get_nw_dst, fset=set_nw_dst)
    nw_tos   = property(fget=get_nw_tos, fset=set_nw_tos)

#
# TCP, UDP
#
class FlowEntryMatchLayer4(FlowEntryMatches):
    def __init__(self, match_str=''):
        super(FlowEntryMatchLayer4, self).__init__(match_str, 'L4')
        # Should be either TCP or UDP
        self._tp_dst = None
        self._tp_src = None

    def set_tp_src(self, tp_src): self._tp_src = tp_src
    def set_tp_dst(self, tp_dst): self._tp_dst = tp_dst
    def get_tp_src(self): return self._tp_src
    def get_tp_dst(self): return self._tp_dst
    tp_src = property(fget=get_tp_src, fset=set_tp_src)
    tp_dst = property(fget=get_tp_dst, fset=set_tp_dst)


class FlowEntryMatchUnknown(FlowEntryMatches):
    def __init__(self, match_str=''):
        super(FlowEntryMatchUnknown, self).__init__(match_str, 'UNKNOWN')

