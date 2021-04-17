# --------------------------------
# Name: TemporalSplit.py
# Purpose: Split a feature class based on either a single time or a start or end time based one a set date time.
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
import arcpy, os, datetime
import SharedArcNumericalLib as san


# Function Definitions

# Main Function Definition

def temporal_split(in_fc, out_ws, start_time, end_time, time_interval, compactBool=True):
    """ This tool will split a feature class into multiple feature classes based on a datetime field based on
    a set time interval.
     Parameters
    -----------------
     in_fc - input feature class with datetime field
     out_ws- out workspace
     start_time - start date time
     end_time - end date time
     time_interval - temporal spacing
     compactBool - compact db after run."""
    try:
        if arcpy.Exists(out_ws):
            arcpy.env.workspace = out_ws
            arcpy.env.overwriteOutput = True
            san.arc_print("The current work space is: {0}.".format(out_ws), True)
            workSpaceTail = os.path.split(out_ws)[1]
            san.arc_print("Constructing Time Delta from input time period string.", True)
            time_magnitude, time_unit = san.alphanumeric_split(time_interval)
            time_delta = san.parse_time_units_to_dt(time_magnitude, time_unit)
            inFeatureClassTail = os.path.split(in_fc)[1]
            san.arc_print(
                "Using datetime fields to generate new feature classes in {0}.".format(
                    str(workSpaceTail)))
            san.arc_print("Getting start and final times in start time field {0}.".format(start_time))
            start_time_min, start_time_max = san.get_min_max_from_field(in_fc, start_time)

            if san.field_exist(in_fc, end_time) and end_time:
                san.arc_print("Using start and end time to grab feature classes whose bins occur within an events "
                              "start or end time.")
                end_time_min, end_time_max = san.get_min_max_from_field(in_fc, end_time)
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
            if isinstance(bin_start_time, datetime.datetime) or isinstance(bin_start_time, datetime.date):
                start_time_range = bin_start_time
                san.arc_print("Bin Start Time was selected, using {0} as bin starting time period."
                              .format(str(bin_start_time)))
            time_bins = san.construct_time_bin_ranges(start_time_range, end_time_range, time_delta)
            san.arc_print("Constructing queries based on datetime ranges.")
            temporal_queries = san.construct_sql_queries_from_time_bin(time_bins, in_fc, start_time_field,
                                                                       end_time_field)
            time_counter = 0
            san.arc_print("Splitting feature classes based on {0} queries.".format(len(temporal_queries)), True)
            for query in temporal_queries:
                try:
                    time_counter += 1
                    san.arc_print("Determining name and constructing query for new feature class.", True)
                    newFCName = "Bin_{0}_{1}".format(time_counter,
                                                     arcpy.ValidateTableName(inFeatureClassTail, out_ws))
                    expression = str(query)
                    arcpy.Select_analysis(in_fc, newFCName, expression)
                    san.arc_print(
                        "Selected out unique ID: {0} with query [{1}] and created a new feature class in {2}".format(
                            newFCName, expression, workSpaceTail), True)
                except:
                    san.arc_print(
                        "The unique value ID {0}, could not be extracted. Check arguments of tool.".format(
                            str(newFCName)))
                    pass
            if compactBool:
                try:
                    san.arc_print("Compacting workspace.", True)
                    arcpy.Compact_management(out_ws)
                except:
                    san.arc_print("Not a Compact capable workspace.")
                    pass
            san.arc_print("Tool execution complete.", True)
            pass
        else:
            san.arc_print("The desired workspace does not exist. Tool execution terminated.", True)
            arcpy.AddWarning("The desired workspace does not exist.")

    except arcpy.ExecuteError:
        san.arc_print(arcpy.GetMessages(2))
    except Exception as e:
        san.arc_print(e.args[0])


# Main Script
if __name__ == "__main__":
    # Define Inputs
    inFeatureClass = arcpy.GetParameterAsText(0)
    outWorkSpace = arcpy.GetParameterAsText(1)
    start_time_field = arcpy.GetParameterAsText(2)
    end_time_field = arcpy.GetParameterAsText(3)
    time_interval = arcpy.GetParameter(4)
    bin_start_time = arcpy.GetParameter(5)
    compactWorkspace = arcpy.GetParameter(5)
    temporal_split(inFeatureClass, outWorkSpace, start_time_field, end_time_field, time_interval, bin_start_time,
                   compactWorkspace)
