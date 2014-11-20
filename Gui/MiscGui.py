'''
Created on Nov 20, 2014

@author: Brady Johnson

Miscellaneous GUI classes used by the FlowDebuggerGui

'''

from Tkinter import *

class LabelEntry(object):
    def __init__(self, parent_frame, label_text, on_input_callable=None):
        self._on_input_callback = on_input_callable

        self._label_entry_frame = Frame(parent_frame)
        self._label_entry_frame.pack(side=TOP)

        self._label_var = StringVar(value=label_text)
        self._label = Label(self._label_entry_frame, textvariable=self._label_var)
        self._label.config(text=label_text)
        self._label.pack(side=LEFT)

        self._entry_var = StringVar()
        self._entry = Entry(self._label_entry_frame, bd=5, textvariable=self._entry_var)
        self._entry.bind('<Return>', self._entry_input)
        self._entry.pack(side=RIGHT)

    def _entry_input(self, event):
        print 'Text Entered: %s' % self.entry_text
        print 'Label Text: %s' % self.label_text
        #self.clear_entry()
        #self.label_text = self.entry_text
        if self._on_input_callback != None:
            self._on_input_callback()

    def clear_entry(self):
        self.entry_text = ''

    def set_label_text(self, text):
        self._label_var.set(text)

    def get_label_text(self):
        return self._label_var.get()

    def set_entry_text(self, text):
        self._entry_var.set(text)

    def get_entry_text(self):
        return self._entry_var.get()

    entry_text = property(fget=get_entry_text, fset=set_entry_text)
    label_text = property(fget=get_label_text, fset=set_label_text)

class Checked(object):
    def __init__(self, parent_frame, check_text, set_checked=False, on_check_callback=None, on_uncheck_callback=None):
        self._checked_value = IntVar(value=1 if set_checked else 0)
        self._check = Checkbutton(parent_frame, text=check_text, variable=self._checked_value, command=self._on_check)
        self._check.pack(side=TOP)
        self._on_check_callback = on_check_callback
        self._on_uncheck_callback = on_uncheck_callback
        self._check_text = check_text

    def _on_check(self):
        if self._checked_value.get() == 1:
            print '%s Checked' % self._check_text
            if self._on_check_callback != None:
                self._on_check_callback()
        else:
            print '%s Un-hecked' % self._check_text
            if self._on_uncheck_callback != None:
                self._on_uncheck_callback()

    def get_checked(self):
        return True if self._checked_value.get() == 1 else False
    def set_checked(self, is_checked):
        if is_checked:
            self._checked_value.set(1)
        else:
            self._checked_value.set(0)
    checked = property(fget=get_checked, fset=set_checked)

class Buttons(object):
    # The buttons_dict should be a dictionary of the form: {'button text' : button_callback}
    def __init__(self, parent_frame, buttons_dict):
        self._buttons = []
        for (name, callback) in buttons_dict.iteritems():
            button = Button(parent_frame, text=name, command=callback)
            button.pack(side=TOP, fill=X)
            self._buttons.append(button)
