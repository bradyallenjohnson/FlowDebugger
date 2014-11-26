'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

from collections import OrderedDict
from Tkinter import Tk, Frame
from Tkconstants import BOTH, BOTTOM, E, LEFT, RIGHT, TOP, W, X, YES
from Flows.DumpFlows import DumpFlows
from Flows.FlowEntries import FlowEntryFormatter
from Gui.GuiMisc import Buttons, Checked, LabelEntry, Popup, ScrolledList
from Gui.TraceGui import TraceGui

class FlowDebuggerGui(object):

    # flow_entries is an instance of FlowEntries.FlowEntryContainer
    def __init__(self, switch, table, of_version, check_cookie=False, check_pkts=False, check_duration=False, check_matched=False):
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
        self._host_label   = LabelEntry(label_entry_frame, 'Host',       'localhost')
        self._ofver_label  = LabelEntry(label_entry_frame, 'OF version', of_version) # TODO Make this a pull-down choice of OpenFlow11 or OpenFlow13
        self._switch_label = LabelEntry(label_entry_frame, 'Switch',     switch)
        self._table_label  = LabelEntry(label_entry_frame, 'Table',      table)

        # The info to display
        # TODO move these to a "View" pull-down menu
        # TODO order by either priority or alphabetical
        checks_frame = Frame(self._top_frame)
        checks_frame.pack(side=LEFT, anchor=W, padx=5)
        self._check_pkts         = Checked(checks_frame, 'show Pkts/Bytes',   set_checked=check_pkts)
        self._check_duration     = Checked(checks_frame, 'show duration',     set_checked=check_duration)
        self._check_cookie       = Checked(checks_frame, 'show cookie',       set_checked=check_cookie)
        self._check_matched_only = Checked(checks_frame, 'show matched only', set_checked=check_matched)

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

        flow_entries = DumpFlows.dump_flows(switch=self._switch_label.entry_text,
                                            table=self._table_label.entry_text,
                                            of_version=self._ofver_label.entry_text)
        flow_entry_formatter = FlowEntryFormatter(verbose=self._check_pkts.checked)
        flow_entry_formatter.show_cookie = self._check_cookie.checked
        flow_entry_formatter.show_duration = self._check_duration.checked
        flow_entry_formatter.show_packets_bytes = self._check_pkts

        for table in flow_entries.iter_tables():
            num_table_entries = flow_entries.num_table_entries(table)
            self._list.append_list_entry('')
            self._list.append_list_entry('Table[%d] %d entr%s' % (table, num_table_entries, 'y' if num_table_entries==1 else 'ies'), fg='red')
            for entry in flow_entries.iter_table_entries(table):
                if self._check_matched_only.checked and entry.n_packets_ == 0:
                    continue
                self._list.append_list_entry(flow_entry_formatter.print_flow_entry(entry))

    def _trace_callback(self):
        Popup('Tracing is not implemented yet')
