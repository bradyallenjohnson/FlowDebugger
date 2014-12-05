'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

import subprocess
import tempfile
from Flows.FlowEntries import FlowEntryContainer
from Flows.FlowEntryFactory import FlowEntryFactory

#
# Internal method to execute a system command and return the return_code and stdout as a str
#
def _execute_command(arg_list_str):
    return_code = 0
    stdout_str = ''

    with tempfile.TemporaryFile(mode='w+b') as f:
        try:
            return_code=subprocess.call(arg_list_str, stdout=f, shell=True)
        except OSError as e:
            print 'OS Error [%d] \"%s\", with command \"%s\"' % (e.errno, e.strerror, ' '.join(arg_list_str))
            return (-1, stdout_str)
        except:
            print 'Unexpected error with command: \"%s\"' % (' '.join(arg_list_str))
            return (-1, stdout_str)

        #print '\"%s\", rc=%d' % (' '.join(arg_list_str), return_code)

        if return_code != 0:
            print 'Non-zero return code [%d] for command: \"%s\"' % (return_code, ' '.join(arg_list_str))
            return (return_code, stdout_str)

        # Flush the tempfile and go to the beginning of it
        f.flush()
        f.seek(0, 0)

        stdout_str = f.read()

    return (return_code, stdout_str.split('\n'))

# Given the input parameters, pass the dump-flows output to the Flows.FlowEntryFactory, 
# and return the results in an instance of Flows.FlowEntries.FlowEntryContainer
def dump_flows(of_version, switch, table='', extra_args=''):
    #
    # Call ovs-ofctl, the resulting output is stored in flow_entry_strs
    #
    command_str = 'ovs-ofctl -O %s dump-flows %s %s %s' % (of_version, switch, 'table=%s'%(table) if len(table) > 0 else '', extra_args)
    print 'Executing command: %s' % command_str
    (rc, flow_entry_strs) = _execute_command([command_str])

    flow_entries = FlowEntryContainer()

    if rc != 0:
        return flow_entries

    #
    # Parse each input line and store the resulting FlowEntries objects
    #
    for line in flow_entry_strs:
        if line.startswith('OFPST_FLOW') or len(line) == 0:
            continue
        flow_entries.add_flow_entry(FlowEntryFactory.parse_entry(line.strip()))

    return flow_entries
