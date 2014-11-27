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
            if not(attr[0].startswith('__') and attr[0].endswith('__')) and attr[1].fget != None:
                value = attr[1].fget(self)
                if value != None:
                    str_list.append('%s = %s' % (attr[0], value))
        return ', '.join(str_list)

    # abstract base class
    def match(self, packet_str):
        raise NotImplementedError

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
    def get_metadata(self): return '%s/%s' % (self._metadata_value, self._metadata_mask) if self._metadata_value != None else None
    in_port  = property(fget=get_inport, fset=set_inport)
    out_port = property(fget=get_outport, fset=set_outport)
    metadata = property(fget=get_metadata, fset=set_metadata)

    def match(self, packet_str):
        raise NotImplementedError

#
# Ethernet
#
class FlowEntryMatchLayer2(FlowEntryMatches):
    def __init__(self, match_str=''):
        super(FlowEntryMatchLayer2, self).__init__(match_str, 'ETHERNET')
        self._mac_src = None
        self._mac_dst = None
        self._protocol_layer3 = ''
        self._dl_type = None
        self._ethertypes = {'0x0800' : 'IP', '0x0806' : 'ARP', '0x8035' : 'RARP'}
        self._dl_vlan = None     # VLAN tag
        self._dl_vlan_pcp = None # VLAN Priority Code Point

    def set_mac_src(self, mac_src): self._mac_src = mac_src
    def set_mac_dst(self, mac_dst): self._mac_dst = mac_dst
    def set_dl_vlan(self, dl_vlan): self._dl_vlan = int(dl_vlan)
    def set_dl_vlan_pcp(self, dl_vlan_pcp): self._dl_vlan = int(dl_vlan_pcp)
    def set_ip(self, empty): # The value for this property setter isnt used 
        self._protocol_layer3 = 'IP'
        self._dl_type = '0x0800'
    def set_dl_type(self, dl_type):
        self._dl_type = dl_type
        self._protocol_layer3 = self._ethertypes.get(dl_type, 'UNKNOWN')
    def get_mac_src(self): return self._mac_src
    def get_mac_dst(self): return self._mac_dst
    def get_dl_vlan(self): return self._dl_vlan
    def get_dl_vlan_pcp(self): return self._dl_vlan
    def get_dl_type(self): return self._dl_type
    mac_src     = property(fget=get_mac_src, fset=set_mac_src)
    mac_dst     = property(fget=get_mac_dst, fset=set_mac_dst)
    dl_vlan     = property(fget=get_dl_vlan, fset=set_dl_vlan)
    dl_vlan_pcp = property(fget=get_dl_vlan_pcp, fset=set_dl_vlan_pcp)
    ip          = property(fset=set_ip)
    dl_type     = property(fget=get_dl_type, fset=set_dl_type)

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
        self._nw_proto = 0
        self._nw_protos = {'1' : 'ICMP', '6' : 'TCP', '17' : 'UDP', '132' : 'SCTP'}
        # TODO need to add icmp_type, icmp_code
        # TODO need to add IP tos, ecn, ttl

    def set_tcp(self, empty): (self._nw_proto, self._protocol_layer4, self._protocol) = (6, 'TCP', 'IP')
    def set_udp(self, empty): (self._nw_proto, self._protocol_layer4, self._protocol) = (17, 'UDP', 'IP')
    def set_nw_proto(self, nw_proto): (self._nw_proto, self._protocol_layer4) = (nw_proto, self._nw_protos.get(nw_proto, 'UNKNOWN'))
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

