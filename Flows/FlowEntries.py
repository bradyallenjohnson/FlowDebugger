'''
Created on Nov 3, 2014

@author: Brady Johnson
'''

class FlowEntry(object):

    def __init__(self):
        '''
        Constructor
        '''
        self.cookie_ = ''
        self.duration_ = 0.0
        self.table_ = -1
        self.n_packets_ = 0
        self.n_bytes_ = 0
        self.send_flow_rem_ = False
        self.priority_ = 0
        self.raw_match_ = ''
        self.raw_actions_ = ''
        self.match_str_list_ = []
        self.match_object_list_ = []
        self.action_str_list_ = []
        self.action_object_list_ = []

    def __str__(self):
        return 'Match(%d)[%s] Actions(%d)[%s]' % (len(self.match_str_list_), self.raw_match_, len(self.action_str_list_), self.raw_actions_)

    def __lt__(self, other):
        if self.priority_ < other.priority_:
            return False
        elif self.priority_ > other.priority_:
            return True

        return self.raw_match_ < other.raw_match_


class FlowEntryContainer(object):
    def __init__(self):
        self.flow_entries = []
        self.flow_entries_byTable = {}

    def __len__(self):
        return len(self.flow_entries)

    #
    # Return an iterable to iterate all the flow entries. May not be ordered per table
    # Usage:
    #    for flow_entry in flow_entry_container.iter_all():
    #        print flow_entry
    #
    def iter_all(self):
        return iter(sorted(self.flow_entries))

    #
    # Return an iterable to iterate the entries for just one table
    # Usage:
    #    for table_entry in flow_entry_container.iter_table_entries(table=3):
    #        print table_entry
    #
    def iter_table_entries(self, table):
        return iter(sorted(self.flow_entries_byTable[table]))

    #
    # Return an iterable to iterate just the tables
    # Usage:
    #    for table_num in flow_entry_container.iter_tables():
    #        print table_num
    #
    def iter_tables(self):
        return iter(sorted(self.flow_entries_byTable.iterkeys()))

    # TODO need to be able to iterate based on the priority

    #
    # Iterate all entries, ordered by table. Used together with next()
    # Usage:
    #    for table_entry in flow_entry_container:
    #        print table_entry
    #
    def __iter__(self):
        try:
            self.table_iter = iter(sorted(self.flow_entries_byTable.iterkeys()))
            self.flow_entry_iter = iter(sorted(self.flow_entries_byTable[self.table_iter.next()]))
        except StopIteration:
            pass

        return self

    # Used when iterating on the object, see __iter__() for more info.
    def next(self):
        try:
            return self.flow_entry_iter.next()
        except StopIteration:
            self.flow_entry_iter = iter(sorted(self.flow_entries_byTable[self.table_iter.next()]))
            return self.flow_entry_iter.next()

    def num_table_entries(self, table):
        return len(self.flow_entries_byTable[table])

    def add_flow_entry(self, flow_entry):
        # Store all the entries together
        self.flow_entries.append(flow_entry)

        # Store the entries by Table
        flows_list = self.flow_entries_byTable.get(flow_entry.table_)
        if flows_list == None:
            # the first entry for this table number
            self.flow_entries_byTable[flow_entry.table_] = [flow_entry]
        else:
            # append the entry to the existing table list
            flows_list.append(flow_entry)

    def reset(self):
        del self.flow_entries[:]
        self.flow_entries_byTable.clear()


class FlowEntryFormatter(object):
    # For now verbose is the same as show_packets_bytes, for more verbose resolution, use the get/set_show_* functions
    def __init__(self, verbose=False, multiline=False):
        self._multiline = multiline
        self._show_cookie = False
        self._show_packets_bytes = False
        self._show_duration = False
        self._verbose = verbose
        if verbose:
            self._show_packets_bytes = True

    def get_show_cookie(self):        return self._show_cookie
    def get_show_packets_bytes(self): return self._show_packets_bytes
    def get_show_duration(self):      return self._show_duration
    def get_verbose(self):            return self._verbose or self._show_packets_bytes
    def set_show_cookie(self, show):         self._show_cookie = show
    def set_show_packets_bytes(self, show):  self._show_packets_bytes = show
    def set_show_duration(self, show):       self._show_duration = show
    def set_verbose(self, show):             self._verbose = self._show_packets_bytes = show
    show_cookie = property(fset=set_show_cookie, fget=get_show_cookie)
    show_packets_bytes = property(fset=set_show_packets_bytes, fget=get_show_packets_bytes)
    show_duration = property(fset=set_show_duration, fget=get_show_duration)
    show_verbose = property(fset=set_verbose, fget=get_verbose)

    def print_flow_entry(self, flow_entry):
        outstr_list = []
        if self._verbose:
            outstr_list.append('Table=%d, Priority=%s, n_packets=%d, n_bytes=%d ' % (flow_entry.table_, flow_entry.priority_, flow_entry.n_packets_, flow_entry.n_bytes_))
        if self._show_cookie:
            outstr_list.append('Cookie=%s '%flow_entry.cookie_)
        if self._show_duration:
            outstr_list.append('Duration=%s '%flow_entry.duration_)

        if self._multiline:
            outstr_list.append('\nMatches(%d)'%len(flow_entry.match_object_list_))
            for match in flow_entry.match_object_list_:
                outstr_list.append('\n\t%s'%str(match))
            outstr_list.append('\nActions(%d)'%len(flow_entry.action_object_list_))
            for action in flow_entry.action_object_list_:
                outstr_list.append('\n\t%s'%str(action))

            return '\n%s'%''.join(outstr_list)
        else:
            outstr_list.append('Matches(%d)[%s] Actions(%d)[%s]' % (len(flow_entry.match_str_list_), flow_entry.raw_match_, len(flow_entry.action_str_list_), flow_entry.raw_actions_))
            return '%s'%''.join(outstr_list)
