FlowDebugger
============

Tool to simplify and debug Open vSwitch OFS table output, taken from "ovf-ofctl dump-flows"

INSTALLATION:
-------------

Prerequisites:

To be able to connect to switches remotely, SSH is used, which is implemented by the paramiko Python library.
Here are the steps to install paramiko:

	$ sudo pip install paramiko

If your not interested in connecting to remote machines, and dont want to install paramiko, just use 
flow_debugger version 1.0.


There are several options to download and install the flow_debugger, as follows:

1) Clone the git repository

	$ git clone https://github.com/bradyallenjohnson/FlowDebugger.git
	$ cd FlowDebugger
	$ sudo python ./setup.py install

2) Download the source distribution

	A source distribution is available here:

		https://github.com/bradyallenjohnson/FlowDebugger/tree/master/dist/FlowDebugger-1.0.tar.gz

	Download it and install as follows:
	$ wget https://github.com/bradyallenjohnson/FlowDebugger/tree/master/dist/FlowDebugger-1.0.tar.gz
	$ tar xvzf FlowDebugger-1.0.tar.gz
	$ cd FlowDebugger-1.0
	$ sudo python ./setup.py install

3) Download a Linux binary distribution

	A binary distribution is available in two different formats here:

		https://github.com/bradyallenjohnson/FlowDebugger/tree/master/dist/FlowDebugger-1.0.linux-x86_64.tar.gz
		https://github.com/bradyallenjohnson/FlowDebugger/tree/master/dist/FlowDebugger-1.0.linux-x86_64.zip

	Download the appropriate format and install as follows:
	$ cd /
	$ wget https://github.com/bradyallenjohnson/FlowDebugger/tree/master/dist/FlowDebugger-1.0.linux-x86_64.tar.gz
	$ sudo tar xvzf FlowDebugger-1.0.linux-x86_64.tar.gz
		-- OR --
	$ wget https://github.com/bradyallenjohnson/FlowDebugger/tree/master/dist/FlowDebugger-1.0.linux-x86_64.zip
	$ sudo unzip FlowDebugger-1.0.linux-x86_64.zip

4) Windows users
	I dont know if 'ovs-ofctl' is available for windows, so the flow_debugger may only be usable on windows
	by connecting to a remote machine, using the "Host" field on the main window.

	I havent prepared a windows version, but you can still install it on windows following these pseudo-steps:
	(I dont know the exact windows syntax, sorry)

	- Clone the Git repository mentioned in step 1) above
	- Install: 'setup.py install'

	- Download the source distribution mentioned in step 2) above
	- Install: 'setup.py install'

USAGE:
------
To see the flow_debugger usage, execute the following:
$ flow_debugger --help

NOTICE: 'flow_debugger' must be run as root, using 'sudo'. If the password is requested when executing
sudo ovs-ofctl, then the applicationt wont work correctly. To get around this, do the following command:

	$ sudo visudo
	$ <Add this line, replacing mininet with your user> mininet ALL=NOPASSWD: ALL

Revision History:
-----------------

1.0 Initial release
1.1 Added remote connection functionality and paramiko dependency


TODO:
-----

- remote connections is only supported in the gui
- Not all FlowEntry match types and actions are supported.
- Ive only ever tested with OpenFlow 1.3
- The flow entry GUI output could be cleaned up. Consider Columns and column headings
- Possibly move the main GUI window checkboxes to a "View" pull-down menu
- Its not possible to copy/paste from the main window
- Need to add documentation
- It would be nice to have a "List Switches" feature that would execute
  "sudo ovs-vsctl list-br" to list the ofs switches available
