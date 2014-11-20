'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

from Tkinter import Tk, Frame, LEFT, RIGHT
import Flows
from MiscGui import LabelEntry, Checked, Buttons

class FlowDebuggerGui(object):

    # flow_entries is an instance of FlowEntries.FlowEntryContainer
    def __init__(self, switch, table, flow_entries):
        self._root = Tk()
        self._root.title('Flow Debugger')

        self._main_frame = Frame(self._root)
        self._main_frame.pack(side=LEFT)

        # The test labels
        label_entry_frame = Frame(self._main_frame)
        label_entry_frame.pack(side=LEFT)
        self._switch_label = LabelEntry(label_entry_frame, 'Switch')
        self._table_label  = LabelEntry(label_entry_frame, 'Table')

        # The info to display
        checks_frame = Frame(self._main_frame)
        checks_frame.pack(side=LEFT)
        self._check_pkts_value = Checked(checks_frame, 'display Pkts/Bytes')
        self._check_duration   = Checked(checks_frame, 'display duration')
        self._check_cookie     = Checked(checks_frame, 'display cookie')

        # the buttons
        button_frame = Frame(self._main_frame)
        button_frame.pack(side=RIGHT)
        buttons_dict = {'refresh' : self.refresh_callback, 'quit' : self._root.quit}
        Buttons(button_frame, buttons_dict)

        self._root.mainloop()

    def refresh_callback(self):
        print 'Refresh was called'
