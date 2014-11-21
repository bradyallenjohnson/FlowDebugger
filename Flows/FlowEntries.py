'''
Created on Nov 3, 2014

@author: Brady Johnson
'''

import FlowEntryMatches
import FlowEntryActions

class FlowEntry(object):
    COOKIE_STR         =  'cookie='
    DURATION_STR       =  'duration='
    TABLE_STR          =  'table='
    NPACKETS_STR       =  'n_packets='
    NBYTES_STR         =  'n_bytes='
    SEND_FLOW_REM_STR  =  'senf_flow_rem'
    ACTIONS_STR        =  'actions='


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

    @staticmethod
    def parse_item(item_key, item_str):
        value = item_str
        if len(item_key) > 0:
            value = item_str.partition(item_key)[2]

        return value.rstrip(',')

    @staticmethod
    def parse_entry(line):
        '''
        Expecting one of the following formats:
          cookie=0x0, duration=1573.875s, table=0, n_packets=2, n_bytes=152, send_flow_rem priority=10 actions=goto_table:1
          cookie=0xa, duration=1573.091s, table=1, n_packets=0, n_bytes=0, priority=256,ip,nw_src=172.16.150.134 actions=write_metadata:0x3e/0xfff,goto_table:2
          cookie=0x0, duration=243628.614s, table=0, n_packets=251762, n_bytes=18340623, priority=0 actions=NORMAL
        '''

        str_list = line.split(' ')

        flow_entry = FlowEntry()
        flow_entry.cookie_    =  FlowEntry.parse_item(FlowEntry.COOKIE_STR,        str_list[0])
        flow_entry.duration_  =  FlowEntry.parse_item(FlowEntry.DURATION_STR,      str_list[1])
        flow_entry.table_     =  int(FlowEntry.parse_item(FlowEntry.TABLE_STR,     str_list[2]))
        flow_entry.n_packets_ =  int(FlowEntry.parse_item(FlowEntry.NPACKETS_STR,  str_list[3]))
        flow_entry.n_bytes_   =  int(FlowEntry.parse_item(FlowEntry.NBYTES_STR,    str_list[4]))

        # Parse the send_flow_rem, if present
        next_index = 5
        if len(str_list) == 8:
            flow_entry.send_flow_rem_ = True
            next_index = 6

        flow_entry.raw_match_   =  FlowEntry.parse_item('', str_list[next_index])
        flow_entry.raw_actions_ =  FlowEntry.parse_item(FlowEntry.ACTIONS_STR, str_list[next_index+1])

        flow_entry.action_str_list_ =  flow_entry.raw_actions_.split(',')
        flow_entry.match_str_list_  =  flow_entry.raw_match_.split(',')
        flow_entry.priority_        =  int(flow_entry.match_str_list_[0].split('=')[1])

        # Parse each match string into a match object, skip the first element which is priority
        for match_str in flow_entry.match_str_list_[1:]:
            flow_entry.match_object_list_.append(FlowEntryMatches.FlowEntryMatchFactory.parse_match(match_str))

        for action_str in flow_entry.action_str_list_:
            flow_entry.action_object_list_.append(FlowEntryActions.FlowEntryActionFactory.parse_action(action_str))

        return flow_entry


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
