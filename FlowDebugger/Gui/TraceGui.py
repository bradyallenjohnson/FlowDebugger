'''
Created on Nov 26, 2014

@author: Brady Johnson
'''

from collections import OrderedDict
from Tkinter import Frame, Toplevel
from Tkconstants import BOTH, BOTTOM, LEFT, S, TOP, W, X, YES
from Gui.GuiMisc import Buttons, LabelEntry, LabelOption, Popup, ScrolledList
from Flows.FlowEntryFactory import FlowEntryFactory
from Flows.FlowTracer import FlowTracer

class TraceGui(object):

    def __init__(self, trace_complete_callback=None):
        self._trace_results_callback = trace_complete_callback
        self._flow_entries_container = None

        self._root = Toplevel()
        self._root.title('FlowEntry Trace')
        self._root.minsize(width=300, height=350)
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
        self._dl_src_label    = LabelEntry(label_entry_frame,  'dl_src')
        self._dl_dst_label    = LabelEntry(label_entry_frame,  'dl_dst')
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

        '''
        check_frame = Frame(self._top_frame)
        check_frame.pack(side=TOP, anchor=W, pady=5)
        self._trace_display_label = LabelBase(check_frame, 'Trace display', width=18)
        radio_vals = ['FlowEntry list highlighting', 'seperate window']
        self._radio_trace_display = Radios(check_frame, radio_vals)
        '''

        # the buttons
        button_frame = Frame(self._top_frame, pady=5)
        button_frame.pack(side=BOTTOM, anchor=S)
        buttons_dict = OrderedDict([('trace', self._trace_callback), ('reset', self._reset_callback), ('cancel', self._cancel_callback)])
        Buttons(button_frame, buttons_dict, button_orientation=LEFT)

        # Hide this window until its needed
        self._root.withdraw()

        #
        # The trace results window
        #
        self._trace_result = Toplevel()
        self._trace_result.title('FlowEntry Trace Results')
        self._trace_result.minsize(width=1200, height=700)
        self._trace_result.withdraw()

        # The trace results scrollable list
        list_frame = Frame(self._trace_result)
        list_frame.pack(side=TOP, expand=YES, fill=BOTH)
        self._trace_results_list = ScrolledList(list_frame)

        # The trace results close button
        result_button_frame = Frame(self._trace_result, padx=5)
        result_button_frame.pack(side=BOTTOM, anchor=S)
        Buttons(result_button_frame, {'close' : self._trace_result.withdraw})


    def _trace_callback(self):
        #
        # Get the input specified in the Trace input window
        input_match_obj_list = []
        for label_entry in self._label_entries:
            if len(label_entry.entry_text) > 0 and label_entry.entry_text != 'empty':
                match_object = FlowEntryFactory.get_match_object(label_entry.label_text, label_entry.entry_text)
                #print '\t%s' % match_object
                input_match_obj_list.append(match_object)

        #
        # Do the tracing
        flow_tracer = FlowTracer(self._flow_entries_container, input_match_obj_list)
        # returns a dictionary of MatchedFlowEntry to (next_table, drop, output, next_input_matches)
        matched_flow_entries = flow_tracer.trace()

        #
        # Open the self._trace_result window to display the results
        self._trace_results_list.clear()
        if len(matched_flow_entries) < 1:
            Popup("No tracing matches found")
            return

        for (matched_flow_entry, results) in matched_flow_entries.iteritems():
            if matched_flow_entry.table_ < 0:
                # No match was found
                self._trace_results_list.append_list_entry('')
                self._trace_results_list.append_list_entry('No Match was found in table %s' % results[0])
                next_action = 'Drop'
            else:
                self._trace_results_list.append_list_entry('')
                self._trace_results_list.append_list_entry('Match found in table %s' % matched_flow_entry.table_)
                self._trace_results_list.append_list_entry('        Flow Entry [%s]' % matched_flow_entry)
                self._trace_results_list.append_list_entry('        Resulting Flow Entry Matches [%d]' % len(results[3]))
                for r in results[3]:
                    self._trace_results_list.append_list_entry('                [%s]' % r)
                if results[1]:     next_action = 'Drop'
                elif results[2]:   next_action = 'Output: %s' % results[2]
                else:              next_action = 'Goto Table %s' % results[0]
            self._trace_results_list.append_list_entry('        Resulting Action: [%s]' % next_action);

        # Now display the window
        self._trace_result.update()
        self._trace_result.deiconify()

        #
        # This will call the root gui to display matched flow entries
        if self._trace_results_callback:
            self._trace_results_callback(matched_flow_entries)

    def _reset_callback(self):
        # Reset all of the fields
        for label_entry in self._label_entries:
            label_entry.clear_entry()

    def _cancel_callback(self):
        self._root.withdraw()

    def display(self):
        self._root.update()
        self._root.deiconify()

    def set_flow_entries_container(self, fe_container):
        self._flow_entries_container = fe_container

    flow_entries_conatiner = property(fset=set_flow_entries_container)
