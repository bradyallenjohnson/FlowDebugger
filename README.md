FlowDebugger
============

Tool to simplify and debug Open vSwitch OFS table output, taken from "ovf-ofctl dump-flows"

To be completed:
- Remote execution, for now the Host entry does nothing
	-- The app needs to be run on the same host as the switch
- The flow entry output needs to be cleaned up. Consider Columns and column headings
- Possibly move the checkboxes to a "View" pull-down menu
- Its not possible to copy/paste from the main window
- Need to formalize the installation and complete setup.py
- bin/flow_debugger has the sys.path hard-coded. This will be fixed once the FlowDebugger is officially installed via setup.py
	-- setting the PYTHONPATH env var wont fix the problem since you need to start the app with sudo
- Need to add documentation
