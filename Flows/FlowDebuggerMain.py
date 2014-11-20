'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

import optparse
from Flows.DumpFlows import DumpFlows
from Flows.FlowEntries import FlowEntryFormatter

class FlowDebuggerMain(object):
    def __init__(self):
        #
        # Command Line Options
        #
        self._parser = optparse.OptionParser(usage='Usage: %prog <option> [component...]')
        self._parser.add_option('-g', '--gui',
                                action='store_true',
                                help='start the application in a GUI as opposed to displaying on stdout')
        self._parser.add_option('-v', '--verbose',
                                action='store_true',
                                help='verbose output: include packet and byte matches')
        self._parser.add_option('-m', '--multiline',
                                action='store_true',
                                help='multiline output: Display flow entry output on multiple lines')
        self._parser.add_option('-o', '--of',
                                default='OpenFlow13',
                                type=str,
                                dest='open_flow_version',
                                help='Specify the OpenFlow version [OpenFlow11 | OpenFlow13], default: OpenFlow13')

    def main(self):
        (options, args) = self._parser.parse_args()

        if len(args) < 1:
            print "INVALID Arguments, must at least specify the switch"
            return

        switch = args[0]
        table = ''
        extra_args = []
        for arg in args[1:]:
            if arg.starts_with('table='):
                table = arg.split('=')[1]
            else:
                extra_args.append(arg)

        # Returns an instance of FlowEntries.FlowEntryContainer
        flow_entries = DumpFlows.dump_flows(switch=switch, table=table, of_version=options.open_flow_version)

        # Output the results
        if options.gui:
            print 'The GUI is not supported yet'
        else:
            # Output to stdout
            print 'Displaying %d Flow entries' % (len(flow_entries))
            flow_entry_fomatter = FlowEntryFormatter(options.verbose, options.multiline)
            for table in flow_entries.iter_tables():
                print "\nTable[%d] %d entries"%(table, flow_entries.num_table_entries(table))
                for entry in flow_entries.iter_table_entries(table):
                    flow_entry_fomatter.print_flow_entry(entry)
    
        '''
        for flow_entry in flow_entries:
            flow_entry_fomatter.print_flow_entry(flow_entry)
        '''
