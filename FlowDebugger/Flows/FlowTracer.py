'''
Created on Nov 27, 2014

@author: Brady Johnson
'''

import copy
from collections import OrderedDict
from FlowDebugger.Flows.FlowEntries import FlowEntry
from FlowDebugger.Flows.FlowEntryActions import FlowEntryActionSetField, FlowEntryActionMod, FlowEntryActionSwitchPort, FlowEntryActionSwitch 
from FlowDebugger.Flows.FlowEntryMatches import FlowEntryMatchSwitch, FlowEntryMatchLayer2, FlowEntryMatchLayer3, FlowEntryMatchLayer4

class FlowTracer(object):

    # flow_entries is a list as returned by Flows.DumpFlows.dump_flows()
    def __init__(self, flow_entries, input_match_object_list):
        self._flow_entries = flow_entries
        self._input_match_object_list = input_match_object_list
        self._set_fields_actions_to_match = {'eth_src' : [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_src],
                                             'eth_dst' : [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_dst],
                                             'vlan_vid': [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_vlan],
                                             'vlan_pcp': [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_vlan_pcp],
                                             'ip_src'  : [FlowEntryMatchLayer3, FlowEntryMatchLayer3.nw_src], # should we also create a L2.IP?
                                             'ip_dst'  : [FlowEntryMatchLayer3, FlowEntryMatchLayer3.nw_dst],
                                             'tcp_src' : [FlowEntryMatchLayer4, FlowEntryMatchLayer4.tp_src], # should we also create a L3.TCP?
                                             'tcp_dst' : [FlowEntryMatchLayer4, FlowEntryMatchLayer4.tp_dst],
                                             'udp_src' : [FlowEntryMatchLayer4, FlowEntryMatchLayer4.tp_src],
                                             'udp_dst' : [FlowEntryMatchLayer4, FlowEntryMatchLayer4.tp_dst]                                    
                                             }
        self._mod_actions_to_match = {'mod_dl_src'      : [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_src],
                                      'mod_dl_dst'      : [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_dst],
                                      'mod_dl_vlan_vid' : [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_vlan],
                                      'mod_dl_vlan_pcp' : [FlowEntryMatchLayer2, FlowEntryMatchLayer2.dl_vlan_pcp],
                                      'mod_nw_src'      : [FlowEntryMatchLayer3, FlowEntryMatchLayer3.nw_src],
                                      'mod_nw_dst'      : [FlowEntryMatchLayer3, FlowEntryMatchLayer3.nw_dst],
                                      'mod_tp_src'      : [FlowEntryMatchLayer4, FlowEntryMatchLayer4.tp_src],
                                      'mod_tp_dst'      : [FlowEntryMatchLayer4, FlowEntryMatchLayer4.tp_dst]
                                      }

    #
    # Returns an Ordered dictionary:
    #   Key - the FlowEntry object that matched. If the FlowEntry.table_ is < 1, then there was no match
    #   Value - A tuple containing the results: (next_table, drop, output, next_input_matches)
    #      - next_table the next table to evaluate
    #      - drop - True/False indicates if the packet should be dropped
    #      - output - None/str indicates if the packet should be output and where
    #      - next_input_matches - a list of FlowEntryMatches objects after having applied the FlowEntry actions.
    # 
    def trace(self):
        next_input_matches = self._input_match_object_list
        keep_going = True
        next_table = 0
        matched_flow_entries = OrderedDict()

        # Iterate the tables, starting with table 0
        # flow_tracer.apply_actions() will increment the table accordingly
        while keep_going:
            #
            # Try for a match in a particular table
            drop = output = None
            matching_flow_entry = self._get_match(next_table, next_input_matches)
            if not matching_flow_entry:
                drop = True
                keep_going = False
                matching_flow_entry = FlowEntry()
            else:
                # If a match was found, apply the corresponding actions
                (next_table, drop, output, next_input_matches) = self._apply_actions(matching_flow_entry, next_input_matches)

            # Store the results
            matched_flow_entries[matching_flow_entry] = (next_table, drop, output, next_input_matches)

            # If the packet is dropped or output, then stop processing
            if drop or output:
                keep_going = False

        return matched_flow_entries

    #
    # Iterate the flow entries in the specified table and returns the 
    # flow_entry from flow_entries that matched input_match_object_list
    # If no match is found, return None
    #
    def _get_match(self, table, input_match_object_list):
        # Iterate each Flow Entry in this table, based on priority
        for (__, entry_list) in self._flow_entries.iter_table_priority_entries(table):
            # Iterate each Flow Entry in this table with the same priority
            for entry in entry_list:
                entry_matched = True
                for match_obj in entry.match_object_list_:
                    #print 'Looking for a match for in table %s, priority %s: %s' % (table, entry.priority_, match_obj)
                    item_matched = False
                    for input_match_obj in input_match_object_list:
                        if match_obj.match(input_match_obj):
                            item_matched = True
                            break
                    if not item_matched:
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
    def _apply_actions(self, flow_entry, input_matches):
        next_table = flow_entry.table_ + 1
        drop = False
        output = None

        # Perform a deep copy, since we may be modifying it
        next_input_matches = copy.deepcopy(input_matches)

        for action in flow_entry.action_object_list_:
            if isinstance(action, FlowEntryActionSwitchPort):
                #print 'FlowEntryActionSwitchPort: %s' % action
                if action.output:
                    output = '%s %s' % (action.output_type, action.output)
                elif action.drop:
                    drop = True
                else:
                    output = action.output_type
                '''
                elif action._packet_in:
                    # TODO finish this
                    print 'PktIn'
                '''

            elif isinstance(action, FlowEntryActionSwitch):
                #print 'FlowEntryActionSwitch: %s' % action
                if action.goto_table:
                    next_table = int(action.goto_table)
                else:
                    metadata_match = FlowEntryMatchSwitch()
                    metadata_match.metadata = action.write_metadata
                    self._merge_match(next_input_matches, metadata_match)

            elif isinstance(action, FlowEntryActionSetField):
                #print 'FlowEntryActionSetField: %s' % action
                action_list = self._set_fields_actions_to_match.get(action.set_field_key)
                if not action_list:
                    # TODO popup
                    print 'ERROR FlowTracer.apply_actions() cant get match object for %s' % action
                match = action_list[0]() # instantiate
                action_list[1].fset(match, action.set_field_value)
                self._merge_match(next_input_matches, match)
                    
            elif isinstance(action, FlowEntryActionMod):
                #print 'FlowEntryActionMod: %s' % action
                action_list = self._mod_actions_to_match.get(action.action_str_key)
                if not action_list:
                    # TODO popup
                    print 'ERROR FlowTracer.apply_actions() cant get match object for %s' % action
                match = action_list[0]() # instantiate
                action_list[1].fset(match, action.action_str_value)
                self._merge_match(next_input_matches, match)

            else:
                # TODO popup
                print 'ERROR unknown action %s' % action

        return (next_table, drop, output, next_input_matches)

    def _merge_match(self, input_match_list, flow_entry_match):
        flow_entry_match_found = False
        for match in input_match_list:
            if match.is_compareable(flow_entry_match):
                # merge the match
                match.copy_match(flow_entry_match)
                flow_entry_match_found = True
                break

        # if it wasnt already in the input_match_list, then add it
        if not flow_entry_match_found:
            input_match_list.append(flow_entry_match)
