'''
Created on Dec 11, 2014

@author: Brady Johnson
'''

from collections import OrderedDict
from Tkinter import Frame, Toplevel
from Tkconstants import BOTTOM, LEFT, S, TOP, W, X
from FlowDebugger.Gui.GuiMisc import Buttons, LabelEntry, Popup

class SshUserPw(object):
    '''
    A separate GUI window to enter the SSH username and password
    '''

    def __init__(self, callback):
        self._callback = callback

        self._root = Toplevel()
        self._root.title('FlowEntry Trace')
        self._root.minsize(width=300, height=150)

        self._top_frame = Frame(self._root)
        self._top_frame.pack(side=TOP, fill=X, padx=10, pady=10)

        # The text labels
        label_entry_frame = Frame(self._top_frame)
        label_entry_frame.pack(side=TOP, anchor=W, pady=5)
        self._username_label = LabelEntry(label_entry_frame,  'username')
        self._password_label = LabelEntry(label_entry_frame,  'password')

        # the buttons
        button_frame = Frame(self._top_frame, pady=5)
        button_frame.pack(side=BOTTOM, anchor=S)
        buttons_dict = OrderedDict([('ok', self._ok_callback), ('cancel', self._cancel_callback)])
        Buttons(button_frame, buttons_dict, button_orientation=LEFT)

        # Hide this window until its needed
        self._root.withdraw()

    @property
    def username(self): return self._username_label.entry_text
    @property
    def password(self): return self._password_label.entry_text

    def display(self, show=True):
        if show:
            self._root.update()
            self._root.deiconify()
        else:
            self._root.withdraw()

    def _cancel_callback(self):
        self.display(False)

    def _ok_callback(self):
        if not self.username or not self.password:
            Popup('Both the username and password must be filled in')
            return

        self.display(False)
        self._callback()
