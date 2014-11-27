'''
Created on Nov 26, 2014

@author: Brady Johnson
'''

from collections import OrderedDict
from Tkinter import Frame, Toplevel
from Tkconstants import BOTTOM, LEFT, S, TOP, W, X
from Gui.GuiMisc import Buttons, LabelEntry, LabelOption
from Flows.FlowEntryFactory import FlowEntryFactory

class TraceGui(object):

    def __init__(self, trace_callback):
        self._root_trace_callback = trace_callback

        self._root = Toplevel()
        self._root.title('FlowEntry Trace')
        #self._root.minsize(width=350, height=350)
        #self._root.geometry('%dx%d+%d+%d'%(900, 700, 120, 120)) # widthxheight+x+y

        self._top_frame = Frame(self._root)
        self._top_frame.pack(side=TOP, fill=X, padx=10, pady=10)

        # TODO for now these label names have to be exactly the same as the FlowEntryMatch object properties
        #      consider either using the property values, or setting the FlowEntryMatch objects in _trace_callback()
        #      differently. This way is kind-of a hack

        # The text labels
        label_entry_frame = Frame(self._top_frame)
        label_entry_frame.pack(side=TOP, anchor=W, pady=5)
        self._in_port_label   = LabelEntry(label_entry_frame,  'in_port')
        self._dl_src_label    = LabelEntry(label_entry_frame,  'mac_src')
        self._dl_dst_label    = LabelEntry(label_entry_frame,  'mac_dst')
        self._dl_type_label   = LabelOption(label_entry_frame, 'dl_type', 'empty', 'empty', 'ARP', 'IP', 'RARP')
        self._vlan_vid_label  = LabelEntry(label_entry_frame,  'dl_vlan')
        self._vlan_pcp_label  = LabelEntry(label_entry_frame,  'dl_vlan_pcp')
        self._nw_src_label    = LabelEntry(label_entry_frame,  'nw_src')
        self._nw_dst_label    = LabelEntry(label_entry_frame,  'nw_dst')
        self._nw_tos_label    = LabelEntry(label_entry_frame,  'nw_tos')
        self._nw_proto_label  = LabelOption(label_entry_frame, 'nw_proto', 'empty', 'empty', 'ICMP', 'SCTP', 'TCP', 'UDP')
        self._tp_src_label    = LabelEntry(label_entry_frame,  'tp_src')
        self._tp_dst_label    = LabelEntry(label_entry_frame,  'tp_dst')
        # This list is used when clearing the label entries
        self._label_entries = [self._in_port_label,
                               self._dl_src_label, self._dl_dst_label, self._dl_type_label,
                               self._vlan_vid_label, self._vlan_pcp_label,
                               self._nw_src_label, self._nw_dst_label, self._nw_tos_label, self._nw_proto_label,
                               self._tp_src_label, self._tp_dst_label]

        # the buttons
        button_frame = Frame(self._top_frame, pady=5)
        button_frame.pack(side=BOTTOM, anchor=S)
        buttons_dict = OrderedDict([('trace', self._trace_callback), ('reset', self._reset_callback), ('cancel', self._cancel_callback)])
        Buttons(button_frame, buttons_dict, button_orientation=LEFT)

        # Hide this window until its needed
        self._root.withdraw()

    def _trace_callback(self):
        # TODO populate a FlowEntry with a list of fields 
        match_obj_list = []
        for label_entry in self._label_entries:
            if len(label_entry.entry_text) > 0 and label_entry.entry_text != 'empty':
                match_obj_list.append(FlowEntryFactory.get_match_object(label_entry.label_text, label_entry.entry_text))
        self._root_trace_callback(match_obj_list)

    def _reset_callback(self):
        # Reset all of the fields
        for label_entry in self._label_entries:
            label_entry.clear_entry()

    def _cancel_callback(self):
        self._root.withdraw()

    def display(self):
        self._root.update()
        self._root.deiconify()
