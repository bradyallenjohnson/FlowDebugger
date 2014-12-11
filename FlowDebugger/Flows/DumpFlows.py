'''
Created on Nov 20, 2014

@author: Brady Johnson
'''

import subprocess
import tempfile
import paramiko
from FlowDebugger.Flows.FlowEntries import FlowEntryContainer
from FlowDebugger.Flows.FlowEntryFactory import FlowEntryFactory

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

def _ssh_connect(host, username, password, port=22):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(host, username=username, password=password, port=port)
    return client

def _execute_remote_command(host, user, pw, command, read_buf_size=256):
    ssh_client = _ssh_connect(host, user, pw)
    (__, ssh_stdout, ssh_stderr) = ssh_client.exec_command(command)
    str_list = []
    channel = ssh_stdout.channel
    buf = channel.recv(read_buf_size)
    while buf:
        str_list.append(buf)
        buf = channel.recv(read_buf_size)

    # TODO need to handle the case that the user doesnt have sudo access to ovs-ofctl and they are asked to enter a password

    stderr_str = ssh_stderr.read().strip()
    if stderr_str:
        print 'SSH command error:\n%s' % stderr_str

    # Use the following lines for simple commands, but
    # for longer running commands, use the channel
    #ssh_stdout.flush()
    #strout = ssh_stdout.read().strip()
    #strerr = ssh_stderr.read().strip()
    #print 'SSH command:\n%s\n%s\n%s\nrc=%d' % (command, strout, strerr, rc)

    return (channel.recv_exit_status(), ''.join(str_list).split('\n'))

# Given the input parameters, pass the dump-flows output to the Flows.FlowEntryFactory, 
# and return the results in an instance of Flows.FlowEntries.FlowEntryContainer
def dump_flows(of_version, switch, host='localhost', table='', extra_args='', user='', pw=''):
    #
    # Call ovs-ofctl, the resulting output is stored in flow_entry_strs
    #
    command_str = 'ovs-ofctl -O %s dump-flows %s %s %s' % (of_version, switch, 'table=%s'%(table) if len(table) > 0 else '', extra_args)
    print 'Executing command: %s' % command_str
    if host == 'localhost':
        (rc, flow_entry_strs) = _execute_command([command_str])
    else:
        (rc, flow_entry_strs) = _execute_remote_command(host, user, pw, 'sudo %s'%command_str)

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
