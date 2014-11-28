'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

from collections import OrderedDict
from Tkinter import Tk, Frame
from Tkconstants import BOTH, BOTTOM, E, LEFT, N, RIGHT, TOP, W, X, YES
from Flows.DumpFlows import DumpFlows
from Flows.FlowEntries import FlowEntryFormatter
from Flows.FlowTracer import FlowTracer
from Gui.GuiMisc import Buttons, Checked, LabelBase, LabelEntry, LabelOption, Popup, Radios, ScrolledList
from Gui.TraceGui import TraceGui

class FlowDebuggerGui(object):

    # flow_entries is an instance of FlowEntries.FlowEntryContainer
    def __init__(self, switch, table, of_version, check_cookie=False, check_pkts=False, check_duration=False, check_priority=False, check_matched=False, sort_by_priority=False):
        self._first_refresh = True
        self._root = Tk()
        self._root.title('Flow Debugger')
        self._root.minsize(width=700, height=500)
        self._root.geometry('%dx%d+%d+%d'%(1200, 700, 100, 100)) # widthxheight+x+y

        self._top_frame = Frame(self._root)
        self._top_frame.pack(side=TOP, fill=X, padx=10, pady=10)

        # The text labels
        label_entry_frame = Frame(self._top_frame)
        label_entry_frame.pack(side=LEFT, anchor=W, padx=5)
        self._host_label   = LabelEntry(label_entry_frame,  'Host',       'localhost')
        self._switch_label = LabelEntry(label_entry_frame,  'Switch',     switch)
        self._table_label  = LabelEntry(label_entry_frame,  'Table',      table)
        self._ofver_label  = LabelOption(label_entry_frame, 'OF version', of_version, 'OpenFlow11', 'OpenFlow13')

        # The info to display
        # TODO move these to a "View" pull-down menu
        checks_frame = Frame(self._top_frame)
        checks_frame.pack(side=LEFT, anchor=W, padx=5)
        self._check_pkts         = Checked(checks_frame, 'show Pkts/Bytes',   set_checked=check_pkts)
        self._check_duration     = Checked(checks_frame, 'show duration',     set_checked=check_duration)
        self._check_priority     = Checked(checks_frame, 'show priority',     set_checked=check_priority)
        self._check_cookie       = Checked(checks_frame, 'show cookie',       set_checked=check_cookie)
        self._check_matched_only = Checked(checks_frame, 'show matched only', set_checked=check_matched)
        #self._radio_sort         = LabelRadio(checks_frame, 'sort by', ['priority', 'match string'])
        
        # Sorting
        sort_frame = Frame(self._top_frame)
        sort_frame.pack(side=LEFT, anchor=N, padx=5)
        self._sort_label = LabelBase(sort_frame, 'Sort FlowEntries', width=18)
        radio_vals = ['priority', 'match string']
        self._radio_sort = Radios(sort_frame, radio_vals, text_prefix='by ')
        if not sort_by_priority:
            self._radio_sort.radio_value = radio_vals[1]

        # Create the Trace GUI window, but only show it when the trace button is pressed
        self._trace_gui = TraceGui(self._trace_callback)

        # the buttons
        button_frame = Frame(self._top_frame, padx=5)
        button_frame.pack(side=RIGHT, anchor=E)
        buttons_dict = OrderedDict([('refresh', self._refresh_callback), ('trace', self._trace_gui.display), ('quit', self._root.quit)])
        Buttons(button_frame, buttons_dict)

        # The scrollable list
        list_frame = Frame(self._root)
        list_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self._list = ScrolledList(list_frame)

    def run(self):
        self._refresh_callback()
        self._root.mainloop()

    def _refresh_callback(self):

        self._list.clear()

        if len(self._switch_label.entry_text) == 0:
            # TODO consider adding functionality to list all availale switches
            if self._first_refresh:
                self._first_refresh = False
            else:
                Popup('Nothing to refresh\n\'Switch\' is empty')
            return

        if self._host_label.entry_text != 'localhost':
            Popup('Remote hosts arent supported yet\nOnly \'localhost\' is supported')
            return
            
        self._flow_entries = DumpFlows.dump_flows(switch=self._switch_label.entry_text,
                                                  table=self._table_label.entry_text,
                                                  of_version=self._ofver_label.entry_text)

        flow_entry_formatter = FlowEntryFormatter()
        flow_entry_formatter.show_cookie        =  self._check_cookie.checked
        flow_entry_formatter.show_duration      =  self._check_duration.checked
        flow_entry_formatter.show_priority      =  self._check_priority.checked
        flow_entry_formatter.show_packets_bytes =  self._check_pkts.checked

        # First display the total number of entries
        self._list.append_list_entry('Total Flow entries: %d' % (len(self._flow_entries)), fg='red')

        for table in self._flow_entries.iter_tables():
            num_table_entries = self._flow_entries.num_table_entries(table)
            self._list.append_list_entry('')
            self._list.append_list_entry('Table[%d] %d entr%s' % (table, num_table_entries, 'y' if num_table_entries==1 else 'ies'), fg='red')
            if self._radio_sort.radio_value == 'priority':
                for (__, entry_list) in self._flow_entries.iter_table_priority_entries(table):
                    for entry in entry_list:
                        if self._check_matched_only.checked and entry.n_packets_ == 0:
                            continue
                        self._list.append_list_entry(flow_entry_formatter.print_flow_entry(entry))
            else:
                for entry in self._flow_entries.iter_table_entries(table):
                    if self._check_matched_only.checked and entry.n_packets_ == 0:
                        continue
                    self._list.append_list_entry(flow_entry_formatter.print_flow_entry(entry))

    def _trace_callback(self, input_match_obj_list):
        for obj in input_match_obj_list:
            print obj
        #Popup('Tracing is not implemented yet')

        # TODO should we do it with a new set of flow entries, or with the ones already displayed???
        '''
        flow_entries = DumpFlows.dump_flows(switch=self._switch_label.entry_text,
                                            table=self._table_label.entry_text,
                                            of_version=self._ofver_label.entry_text)
        '''

        flow_tracer = FlowTracer(self._flow_entries)
        next_input_matches = input_match_obj_list
        keep_going = True
        next_table = 0

        # Iterate the tables, starting with table 0
        # flow_tracer.apply_actions() will increment the table accordingly
        while keep_going:
            # This will try for a match in a particular table
            matching_flow_entry = flow_tracer.get_match(next_table, next_input_matches)
            if matching_flow_entry == None:
                print 'No match found in table %d, DROP' % next_table
                keep_going = False
                break
            print 'Applying actions %s' % (', '.join(matching_flow_entry.action_str_list_))
            (next_table, drop, output, next_input_matches) = flow_tracer.apply_actions(matching_flow_entry, next_input_matches)
            
            if drop:
                print 'Drop packet'
                break
            if output != None:
                print 'output packet to port %s' % output
                break

            print 'Jumping to table %d' % next_table
            #print 'Resulting packet: %s' % ', '.join(next_input_matches)


