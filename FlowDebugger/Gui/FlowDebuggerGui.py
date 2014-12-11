'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

from collections import OrderedDict
from Tkinter import Tk, Frame
from Tkconstants import BOTH, BOTTOM, E, LEFT, N, RIGHT, TOP, W, X, YES
import FlowDebugger.Flows.DumpFlows as DumpFlows
from FlowDebugger.Flows.FlowEntries import FlowEntryFormatter
from FlowDebugger.Gui.GuiMisc import Buttons, Checked, LabelBase, LabelEntry, LabelOption, Popup, Radios, ScrolledList
from FlowDebugger.Gui.TraceGui import TraceGui
from FlowDebugger.Gui.SshUserPw import SshUserPw

class FlowDebuggerGui(object):

    # flow_entries is an instance of FlowEntries.FlowEntryContainer
    def __init__(self, switch, table, of_version, check_cookie=False, check_pkts=False, check_duration=False, check_priority=False, check_matched=False, sort_by_priority=False):
        self._first_refresh = True
        self._flow_entries = None

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
        self._filter_label = LabelEntry(label_entry_frame,  'Filter string')
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
        self._reset_login        = Checked(checks_frame, 'reset login',       set_checked=False)
        self._reset_login.display(False)

        # Sorting
        sort_frame = Frame(self._top_frame)
        sort_frame.pack(side=LEFT, anchor=N, padx=5)
        self._sort_label = LabelBase(sort_frame, 'Sort FlowEntries', width=18)
        radio_vals = ['priority', 'match string']
        self._radio_sort = Radios(sort_frame, radio_vals, text_prefix='by ')
        if not sort_by_priority:
            self._radio_sort.radio_value = radio_vals[1]

        # the buttons
        button_frame = Frame(self._top_frame, padx=5)
        button_frame.pack(side=RIGHT, anchor=E)
        buttons_dict = OrderedDict([('refresh', self._refresh_callback), ('trace', self._trace_callback), ('quit', self._root.quit)])
        Buttons(button_frame, buttons_dict)

        # The scrollable list
        list_frame = Frame(self._root)
        list_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self._list = ScrolledList(list_frame)
        # keep the index of each FlowEntry to be able to highlight the tracing later
        self._list_entry_indices = {}

        # Create the Trace GUI window, but only show it when the trace button is pressed
        self._trace_gui = TraceGui(self._trace_results_callback)

        # Create the User/Pw GUI window
        self._user_gui = SshUserPw(self._refresh_callback_user_pw)
        self._user_pass_stored = False


    # This is a blocking call
    def run(self):
        self._refresh_callback()
        self._root.mainloop() # blocking call

    # This function is called when the "refresh" button is pressed on the main GUI window
    def _refresh_callback(self):
        # We cant do anything if the switch name is empty
        if not self._switch_label.entry_text:
            # TODO consider adding functionality to list all availale switches
            if self._first_refresh:
                self._first_refresh = False
            else:
                Popup('Nothing to refresh\n\'Switch\' is empty')
            return

        # Check if we need to get the username/password
        if self._host_label.entry_text != 'localhost':
            if not self._user_pass_stored or self._reset_login.checked:
                self._user_gui.display(True)
                return
        else:
            self._user_pass_stored = False
            self._reset_login.checked = False
            self._reset_login.display(False) # Hide it if it was previously being displayed
        self._refresh_callback_dump()

    # This function is called when the self._user_gui is displayed and its "ok" button is pressed
    def _refresh_callback_user_pw(self):
        self._user_pass_stored = True
        self._reset_login.display(True)
        self._refresh_callback_dump()

    # This function is only called by either _refresh_callback() or _refresh_callback_user_pw()
    def _refresh_callback_dump(self):
        self._list.clear()
        self._list_entry_indices.clear()

        
        try:
            self._flow_entries = DumpFlows.dump_flows(switch=self._switch_label.entry_text,
                                                      table=self._table_label.entry_text,
                                                      host=self._host_label.entry_text,
                                                      user=self._user_gui.username,
                                                      pw=self._user_gui.password,
                                                      of_version=self._ofver_label.entry_text)
        except Exception as e:
            Popup('Caught an exception trying to dump flows:\n[%s]'%e)
            return

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
                        self._append_entry(flow_entry_formatter, entry)
            else:
                for entry in self._flow_entries.iter_table_entries(table):
                    self._append_entry(flow_entry_formatter, entry)

    def _append_entry(self, formatter, entry):
        if self._check_matched_only.checked and entry.n_packets_ == 0:
            return

        flow_str = formatter.print_flow_entry(entry)
        if self._filter_label.entry_text:
            if self._filter_label.entry_text not in flow_str:
                return

        self._list_entry_indices[entry] = self._list.append_list_entry(flow_str)

    def _trace_callback(self):
        if not self._flow_entries or not self._flow_entries:
            Popup('No FlowEntries to Trace')
            return

        if self._filter_label.entry_text:
            Popup('Cant trace when a filter string is specified')
            return

        self._trace_gui.flow_entries_conatiner = self._flow_entries
        self._trace_gui.display()


    # matched_flow_entries will be a dictionary of matched flow_entry to (next_table, drop, output, next_input_matches) 
    # The tuple indicates the results: next_input_matches will be a list of FlowEntryMatch objects which will
    # show which flow entries were matched and how the packet was changed by the corresponding actions
    def _trace_results_callback(self, matched_flow_entries):
        # TODO need to iterate all entries and un-highlight them in case trace was called multiple times without haveing done a refresh 
        for (matched_flow_entry, __) in matched_flow_entries.iteritems():
            index = self._list_entry_indices.get(matched_flow_entry)
            if index is not None:
                self._list.highlight_entry(index, bg='grey')
