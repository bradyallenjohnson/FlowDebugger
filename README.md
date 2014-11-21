FlowDebugger
============

Tool to simplify and debug Open vSwitch OFS table output, taken from "ovf-ofctl dump-flows"

To be completed:
- Remote execution, for now the Host entry does nothing
	-- The app needs to be run on the same host as the switch
- The Label/Entry fields, checkboxes and buttons need to be stuck down, now they move (stupidly) when the window is resized
- The flow entry output needs to be cleaned up. Consider Columns and column headings
- Add tracing feature: allow an input pkt to be specified, then pressing a trace button, you can see the flow through the OFS tables
	This is similar to the "ovs-appctl trace" feature
- Possibly move the checkboxes to a "View" pull-down menu
