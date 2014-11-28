'''
Created on Nov 27, 2014

@author: Brady Johnson
'''

from Flows.FlowEntryActions import FlowEntryActionSetField, FlowEntryActionMod, FlowEntryActionSwitchPort, FlowEntryActionSwitch 

class FlowTracer(object):

    # flow_entries is a list as returned by Flows.DumpFlows.dump_flows()
    def __init__(self, flow_entries):
        self._flow_entries = flow_entries

    #
    # Iterate the flow entries in the specified table and returns the 
    # flow_entry from flow_entries that matched input_match_object_list
    # If no match is found, return None
    #
    def get_match(self, table, input_match_object_list):
        # Iterate each Flow Entry in this table, based on priority
        for (__, entry_list) in self._flow_entries.iter_table_priority_entries(table):
            # Iterate each Flow Entry in this table with the same priority
            for entry in entry_list:
                entry_matched = True
                for match_obj in entry.match_object_list_:
                    print 'Looking for a match for: %s' % match_obj
                    item_matched = False
                    for input_match_obj in input_match_object_list:
                        if match_obj.match(input_match_obj):
                            item_matched = True
                            break
                    if item_matched:
                        print 'Match found, match_obj [%s] input [%s]' % (match_obj, input_match_obj)
                    else:
                        # Go on to the next entry in the table
                        entry_matched = False
                        break
                if entry_matched:
                    return entry

    #
    # Given a flow_entry returned by get_match(), return an input_match_object_list
    # which is a result of applying the flow_entry actions
    # Return (next_table, drop, output, next_input_matches)
    #
    def apply_actions(self, flow_entry, input_matches):
        next_table = flow_entry.table_ + 1
        drop = False
        output = None

        # TODO need to merge the input_matches with the actions

        for action in flow_entry.action_object_list_:
            if isinstance(action, FlowEntryActionSwitchPort):
                output = action.output_type
                if action._packet_in:
                    # TODO finish this
                    print 'PktIn'
                elif action.drop:
                    drop = True
            elif isinstance(action, FlowEntryActionSwitch):
                if action.goto_table != None:
                    next_table = int(action.goto_table)
                else:
                    # TODO finish this
                    print 'metadata'
            elif isinstance(action, FlowEntryActionSetField):
                print 'FlowEntryActionSetField: %s' % action
            elif isinstance(action, FlowEntryActionMod):
                print 'FlowEntryActionMod: %s' % action
            else:
                print 'unknown action'

        return (next_table, drop, output, input_matches)
