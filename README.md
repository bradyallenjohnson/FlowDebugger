FlowDebugger
============

Tool to simplify and debug Open vSwitch OFS table output, taken from "ovf-ofctl dump-flows"

To be completed:
- Remote execution, for now the Host entry does nothing
	-- The app needs to be run on the same host as the switch
- The Label/Entry fields, checkboxes and buttons need to be stuck down, now they move (stupidly) when the window is resized
	DONE
- The flow entry output needs to be cleaned up. Consider Columns and column headings
- Add tracing feature: allow an input pkt to be specified, then pressing a trace button, you can see the flow through the OFS tables
  (This is similar to the "ovs-appctl trace" feature)
        In Progress: partially complete, the output goes to stdout, need to highlight matched entries in the main window, and upon 
                     selecting matched entries, show the changes and actions to be taken (next table, drop, etc)
- Possibly move the checkboxes to a "View" pull-down menu
- Its not possible to copy/paste from the main window
- Need to formalize the installation and complete setup.py
- bin/flow_debugger has the sys.path hard-coded. This will be fixed once the FlowDebugger is officially installed via setup.py
	-- setting the PYTHONPATH env var wont fix the problem since you need to start the app with sudo
