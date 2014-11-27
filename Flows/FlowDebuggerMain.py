'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

import optparse
from Flows.DumpFlows import DumpFlows
from Flows.FlowEntries import FlowEntryFormatter
from Gui.FlowDebuggerGui import FlowDebuggerGui

class FlowDebuggerMain(object):
    def __init__(self):
        #
        # Command Line Options
        #
        self._parser = optparse.OptionParser(usage='Usage: %prog <option> [component...]')
        self._parser.add_option('-g', '--gui',
                                action='store_true',
                                help='start the application in a GUI as opposed to displaying on stdout, Default')
        self._parser.add_option('-s', '--stdout',
                                action='store_true',
                                help='Dont start the GUI, all output will be displayed on stdout')
        self._parser.add_option('-v', '--verbose',
                                action='store_true',
                                help='verbose output: include packet and byte matches')
        self._parser.add_option('-m', '--multiline',
                                action='store_true',
                                help='multiline output: Display flow entry output on multiple lines, stdout only')
        self._parser.add_option('--matched-only',
                                action='store_true',
                                help='Only display flow entries that have matched')
        self._parser.add_option('-p', '--priority',
                                action='store_true',
                                help='Iterate the flow entries for a table based on priority, as opposed to alphabetically, Default: alphabetically')
        self._parser.add_option('-o', '--of',
                                default='OpenFlow13',
                                type='choice',
                                choices=['OpenFlow11', 'OpenFlow13'],
                                dest='open_flow_version',
                                help='Specify the OpenFlow version [OpenFlow11, OpenFlow13], Default: OpenFlow13')

    def main(self):
        (options, args) = self._parser.parse_args()

        switch = ''
        table = ''
        extra_args = []
        if len(args) > 0:
            switch = args[0]
            table = ''
            extra_args = []
            for arg in args[1:]:
                if arg.starts_with('table='):
                    table = arg.split('=')[1]
                else:
                    extra_args.append(arg)

        #
        # Output the results, either using a GUI or to stdout
        #
        if options.stdout:
            #
            # Output to stdout
            #
            if len(args) < 1:
                print "INVALID Arguments, must at least specify the switch"
                return

            # Returns an instance of FlowEntries.FlowEntryContainer
            flow_entries = DumpFlows.dump_flows(switch=switch, table=table, of_version=options.open_flow_version)
            print 'Displaying %d Flow entries' % (len(flow_entries))

            flow_entry_formatter = FlowEntryFormatter(options.verbose, options.multiline)
            for table in flow_entries.iter_tables():
                print "\nTable[%d] %d entries"%(table, flow_entries.num_table_entries(table))
                if options.priority:
                    for (__, entry_list) in flow_entries.iter_table_priority_entries(table):
                        for entry in entry_list:
                            if options.matched_only and entry.n_packets_ == 0:
                                continue
                            print flow_entry_formatter.print_flow_entry(entry)
                else:
                    for entry in flow_entries.iter_table_entries(table):
                        if options.matched_only and entry.n_packets_ == 0:
                            continue
                        print flow_entry_formatter.print_flow_entry(entry)
        else:
            #
            # GUI
            #
            gui = FlowDebuggerGui(switch, table,
                                  options.open_flow_version,
                                  check_pkts=options.verbose,
                                  check_matched=options.matched_only,
                                  sort_by_priority=options.priority)
            gui.run()
