'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

from Tkinter import Tk, Frame
from Tkconstants import *
from Flows.DumpFlows import DumpFlows
from Flows.FlowEntries import FlowEntryFormatter
from Gui.GuiMisc import LabelEntry, Checked, Buttons, ScrolledList

class FlowDebuggerGui(object):

    # flow_entries is an instance of FlowEntries.FlowEntryContainer
    def __init__(self, switch, table, of_version, check_cookie=False, check_pkts=False, check_duration=False, check_matched=False):
        self._root = Tk()
        self._root.title('Flow Debugger')

        self._top_frame = Frame(self._root)
        self._top_frame.pack(side=TOP)

        # The text labels
        label_entry_frame = Frame(self._top_frame)
        label_entry_frame.pack(side=LEFT, anchor=W)
        self._host_label   = LabelEntry(label_entry_frame, 'Host',       'localhost')
        self._ofver_label  = LabelEntry(label_entry_frame, 'OF version', of_version) # Make this a pull-down choice of OpenFlow11 or OpenFlow13
        self._switch_label = LabelEntry(label_entry_frame, 'Switch',     switch)
        self._table_label  = LabelEntry(label_entry_frame, 'Table',      table)

        # The info to display
        # TODO move these to a "View" pull-down menu
        checks_frame = Frame(self._top_frame)
        checks_frame.pack(side=LEFT)
        self._check_pkts         = Checked(checks_frame, 'show Pkts/Bytes',   set_checked=check_pkts)
        self._check_duration     = Checked(checks_frame, 'show duration',     set_checked=check_duration)
        self._check_cookie       = Checked(checks_frame, 'show cookie',       set_checked=check_cookie)
        self._check_matched_only = Checked(checks_frame, 'show matched only', set_checked=check_matched)

        # the buttons
        button_frame = Frame(self._top_frame)
        button_frame.pack(side=RIGHT)
        buttons_dict = {'refresh' : self._refresh_callback, 'quit' : self._root.quit}
        Buttons(button_frame, buttons_dict)

        # The scrollable list
        list_frame = Frame(self._root)
        list_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self._list = ScrolledList(list_frame)

    def run(self):
        self._refresh_callback()
        self._root.mainloop()

    def _refresh_callback(self):
        print 'Refresh was called'

        # TODO if switch is empty, then dont call DumpFlows until its filled in and refresh is called

        flow_entries = DumpFlows.dump_flows(switch=self._switch_label.entry_text,
                                            table=self._table_label.entry_text,
                                            of_version=self._ofver_label.entry_text)
        flow_entry_fomatter = FlowEntryFormatter(True) # TODO need to map check boxes to this option
        for table in flow_entries.iter_tables():
            # TODO add matched-only logic here
            num_table_entries = flow_entries.num_table_entries(table)
            self._list.append_list_entry('')
            self._list.append_list_entry('Table[%d] %d entr%s' % (table, num_table_entries, 'y' if num_table_entries==1 else 'ies'), fg='red')
            for entry in flow_entries.iter_table_entries(table):
                self._list.append_list_entry(flow_entry_fomatter.print_flow_entry(entry))
