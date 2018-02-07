# --------------------------------
# Name: TemporalMeanCenter.py
# Purpose: Runs multiple mean center(s) (analysis)  on a feature class based on either a single time
#  or a start or end time based on a set datetime. The result is a merged feature class.
# Current Owner: David Wasserman
# Last Modified: 2/7/2018
# Copyright:   (c) Co-Adaptive- David Wasserman
# ArcGIS Version:   10.4.1
# Python Version:   2.7
# License
# Copyright 2015 David J. Wasserman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------

# Import Modules
import arcpy, os, datetime, dateutil, re
import SharedArcNumericalLib as san


# Function Definitions

# Main Function Definition

def temporal_mean_center(inFeatureClass, outFeatureClass, start_time, end_time, time_interval, bin_start,
                         weight_field, case_field, dimension_field):
    """ This tool will split a feature class into multiple kernel densities based on a datetime field and a
    a set time interval. The result will be a time enabled moasic with Footprint. """
    try:
        outWorkSpace = os.path.dirname(outFeatureClass)
        if arcpy.Exists(outWorkSpace):
            arcpy.env.workspace = outWorkSpace
            arcpy.env.overwriteOutput = True
            san.arc_print("The current work space is: {0}.".format(outWorkSpace), True)
            # Set up Work Space Environments
            out_workspace_path_split = os.path.split(outWorkSpace)
            workSpaceTail = out_workspace_path_split[1]
            inFeatureClassTail = os.path.split(inFeatureClass)[1]
            san.arc_print("Gathering describe object information from workspace and input feature class.")
            ws_desc = arcpy.Describe(outWorkSpace)
            workspace_is_geodatabase = ws_desc.dataType == "Workspace" or ws_desc.dataType == "FeatureDataset"
            fin_output_workspace = outWorkSpace

            # Set up Time Deltas and Parse Time String
            san.arc_print("Constructing Time Delta from input time period string.", True)
            time_magnitude, time_unit = san.alphanumeric_split(str(time_interval))
            time_delta = san.parse_time_units_to_dt(time_magnitude, time_unit)
            san.arc_print(
                "Using datetime fields to generate new feature classes in {0}.".format(
                    str(workSpaceTail)))
            san.arc_print("Getting start and final times in start time field {0}.".format(start_time))
            start_time_min, start_time_max = san.get_min_max_from_field(inFeatureClass, start_time)
            # Establish whether to use end time field or only a start time (Single Date Field)
            if san.field_exist(inFeatureClass, end_time) and end_time:
                san.arc_print("Using start and end time to grab feature classes whose bins occur within an events "
                              "start or end time.")
                end_time_min, end_time_max = san.get_min_max_from_field(inFeatureClass, end_time)
                start_time_field = start_time
                end_time_field = end_time
                start_time_range = start_time_min
                end_time_range = end_time_max
            else:
                san.arc_print("Using only first datetime start field to construct time bin ranges.")
                start_time_field = start_time
                end_time_field = start_time
                start_time_range = start_time_min
                end_time_range = start_time_max
            if isinstance(bin_start, datetime.datetime) or isinstance(bin_start, datetime.date):
                start_time_range = bin_start
                san.arc_print("Bin Start Time was selected, using {0} as bin starting time period."
                              .format(str(bin_start_time)))
            time_bins = san.construct_time_bin_ranges(start_time_range, end_time_range, time_delta)
            san.arc_print("Constructing queries based on datetime ranges.")
            temporal_queries = san.construct_sql_queries_from_time_bin(time_bins, inFeatureClass, start_time_field,
                                                                       end_time_field)
            # Declare New Temporal Field Names
            join_id_field = arcpy.ValidateFieldName("TemporalJoinID", fin_output_workspace)
            bin_number = arcpy.ValidateFieldName("Bin_Number", fin_output_workspace)
            dt_starttime = arcpy.ValidateFieldName("DT_Start_Bin", fin_output_workspace)
            dt_endtime = arcpy.ValidateFieldName("DT_End_Bin", fin_output_workspace)
            txt_starttime = arcpy.ValidateFieldName("TXT_Start_Bin", fin_output_workspace)
            txt_endtime = arcpy.ValidateFieldName("TXT_End_Bin", fin_output_workspace)
            extract_query_field = arcpy.ValidateFieldName("Extract_Query", fin_output_workspace)
            # Transition to temporal iteration
            time_counter = 0
            temporal_record_dict = {}
            san.arc_print("Generating Mean Centers based on {0} queries.".format(len(temporal_queries)), True)
            for query in temporal_queries:
                try:
                    time_counter += 1
                    newFCName = "TempFCBin_{0}".format(str(time_counter))
                    if not workspace_is_geodatabase:
                        newFCName = newFCName[0:13]  # Truncate Name if not workspace.
                    san.arc_print("Creating Mean Center with query '{0}'.".format(str(query)), True)
                    temporary_layer = arcpy.MakeFeatureLayer_management(inFeatureClass, newFCName, query)
                    # Break up general density to have pop field set to none if no actually field exists.
                    temporal_mean_center = "in_memory/MCTemporalTemp"
                    arcpy.MeanCenter_stats(temporary_layer, temporal_mean_center, weight_field, case_field,
                                           dimension_field)
                    start_date_time = time_bins[time_counter - 1][0]
                    end_date_time = time_bins[time_counter - 1][1]
                    start_bin_time_string = str(start_date_time)
                    end_bin_time_string = str(end_date_time)
                    if not workspace_is_geodatabase:
                        arcpy.AddWarning("DBF tables can only accept date fields, not datetimes."
                                         " Please check string field.")
                        start_date_time = start_date_time.date()
                        end_date_time = end_date_time.date()
                    # Create Unique ID
                    san.add_new_field(temporal_mean_center, join_id_field, "TEXT", field_alias="TEMPORAL_JOIN_ID")
                    join_fields = [join_id_field]
                    case_present = False
                    if san.field_exist(temporal_mean_center, case_field):
                        join_fields = [join_id_field, case_field]
                        case_present = True
                    with arcpy.da.UpdateCursor(temporal_mean_center, join_fields) as join_cursor:
                        for row in join_cursor:
                            unique_id = san.constructUniqueStringID([str("1"), str(time_counter)])
                            if case_present:
                                unique_id = san.constructUniqueStringID([str(row[1]), str(time_counter)])
                            row[0] = unique_id
                            join_cursor.updateRow(row)
                            temporal_record_dict[unique_id] = [time_counter, start_date_time, end_date_time,
                                                               start_bin_time_string, end_bin_time_string, query]

                    if time_counter == 1:
                        san.arc_print("Copying First Mean Center to Output Feature Class.")
                        arcpy.CopyFeatures_management(temporal_mean_center, outFeatureClass)
                    else:
                        san.arc_print("Appending Mean Center to Output Feature Class.")
                        arcpy.Append_management(temporal_mean_center, outFeatureClass)
                    arcpy.Delete_management(temporal_mean_center)  # memory management
                except:
                    arcpy.AddWarning("Could not process query {0}.".format(str(query)))
            san.arc_print("Adding time fields to output temporal feature class.", True)
            san.add_new_field(outFeatureClass, bin_number, "LONG")
            san.add_new_field(outFeatureClass, dt_starttime, "DATE", field_alias="Start Bin Datetime")
            san.add_new_field(outFeatureClass, dt_endtime, "DATE", field_alias="End Bin Datetime")
            san.add_new_field(outFeatureClass, txt_starttime, "TEXT", field_alias="Start Bin String")
            san.add_new_field(outFeatureClass, txt_endtime, "TEXT", field_alias="End Bin String")
            san.add_new_field(outFeatureClass, extract_query_field, "TEXT")

            san.arc_print("Joining Temporal values by joining a dictionary to the unique ID.", True)
            table_fields = [bin_number, dt_starttime, dt_endtime, txt_starttime, txt_endtime,
                            extract_query_field]
            san.join_record_dictionary(outFeatureClass, temporal_record_dict, join_id_field, table_fields)
            san.arc_print("Tool execution complete.", True)
            pass
        else:
            san.arc_print("The desired workspace does not exist. Tool execution terminated.", True)
            arcpy.AddWarning("The desired workspace does not exist.")

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        san.arc_print(str(e.args[0]))


# Main Script
if __name__ == "__main__":
    # Define Inputs
    # Temporal Params
    inFeatureClass = arcpy.GetParameterAsText(0)
    outFeatureClass = arcpy.GetParameterAsText(1)
    start_time_field = arcpy.GetParameterAsText(2)
    end_time_field = arcpy.GetParameterAsText(3)
    time_interval = arcpy.GetParameter(4)
    bin_start_time = arcpy.GetParameter(5)
    # Mean Center Params
    case_field = arcpy.GetParameterAsText(6)
    weight_field = arcpy.GetParameterAsText(7)
    dimension_field = arcpy.GetParameterAsText(8)
    temporal_mean_center(inFeatureClass, outFeatureClass, start_time_field, end_time_field,
                         time_interval, bin_start_time, weight_field, case_field, dimension_field)
