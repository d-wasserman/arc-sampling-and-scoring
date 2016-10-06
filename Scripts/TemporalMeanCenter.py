# --------------------------------
# Name: TemporalMeanCenter.py
# Purpose: Runs multiple mean center(s) (analysis)  on a feature class based on either a single time
#  or a start or end time based on a set datetime. The result is a merged feature class.
# Current Owner: David Wasserman
# Last Modified: 7/28/2016
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
import numpy as np

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


# Function Definitions
def funcReport(function=None, reportBool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def funcReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if reportBool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return funcWrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return funcReport_Decorator(function)

        return waiting_for_function
    else:
        return funcReport_Decorator(function)


def arcToolReport(function=None, arcToolMessageBool=False, arcProgressorBool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def arcToolReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if arcToolMessageBool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(funcResult)))
                if arcProgressorBool:
                    arcpy.SetProgressorLabel("Function:{0}".format(str(function.__name__)))
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                arcpy.AddMessage(
                        "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__),
                                                                                        str(args)))
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return funcWrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return arcToolReport_Decorator(function)

        return waiting_for_function
    else:
        return arcToolReport_Decorator(function)


def getFields(featureClass, excludedTolkens=["OID", "Geometry"], excludedFields=["shape_area", "shape_length"]):
    try:
        fcName = os.path.split(featureClass)[1]
        field_list = [f.name for f in arcpy.ListFields(featureClass) if f.type not in excludedTolkens
                      and f.name.lower() not in excludedFields]
        arcPrint("The field list for {0} is:{1}".format(str(fcName), str(field_list)), True)
        return field_list
    except:
        arcPrint("Could not get fields for the following input {0}, returned an empty list.".format(str(featureClass)),
                 True)
        arcpy.AddWarning(
                "Could not get fields for the following input {0}, returned an empty list.".format(str(featureClass)))
        field_list = []
        return field_list


@arcToolReport
def FieldExist(featureclass, fieldname):
    """ Check if a field in a feature class field exists and return true it does, false if not."""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False


@arcToolReport
def AddNewField(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    # Add a new field if it currently does not exist...add field alone is slower than checking first.
    if FieldExist(in_table, field_name):
        print(field_name + " Exists")
        arcpy.AddMessage(field_name + " Exists")
    else:
        print("Adding " + field_name)
        arcpy.AddMessage("Adding " + field_name)
        arcpy.AddField_management(in_table, field_name, field_type, field_precision, field_scale,
                                  field_length,
                                  field_alias,
                                  field_is_nullable, field_is_required, field_domain)

@arcToolReport
def arcPrint(string, progressor_Bool=False):
    """ This function is used to simplify using arcpy reporting for tool creation,if progressor bool is true it will
    create a tool label."""
    casted_string = str(string)
    if progressor_Bool:
        arcpy.SetProgressorLabel(casted_string)
        arcpy.AddMessage(casted_string)
        print(casted_string)
    else:
        arcpy.AddMessage(casted_string)
        print(casted_string)


@arcToolReport
def get_min_max_from_field(table, field):
    """Get min and max value from input feature class/table."""
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        data = [row[0] for row in cursor if row[0]]
        return min(data), max(data)


@arcToolReport
def construct_time_bin_ranges(first_time, last_time, time_delta):
    temporal_counter = first_time
    total_time_range = last_time - first_time
    bin_count = int(np.ceil(total_time_range.total_seconds() / time_delta.total_seconds()))
    nested_time_bin_pairs = []
    for bin in range(bin_count):
        start_time = temporal_counter
        end_time = temporal_counter + time_delta
        nested_time_bin_pairs.append([start_time, end_time])
        temporal_counter = end_time
    return nested_time_bin_pairs


@arcToolReport
def construct_sql_queries_from_time_bin(nested_time_bin_pairs, dataSource, start_time_field, end_time_field=None):
    """Takes in nested time bin pairs and constructed ESRI file formatted SQL queries to extract data between the
    two date time pairs of each bin. Returns a list of SQL queries based on the time bins. """
    if end_time_field is None:
        end_time_field = start_time_field
    QueryList = []
    time_format = "%Y-%m-%d %H:%M:%S"
    prepended_sql_time = "date "
    start_field = arcpy.AddFieldDelimiters(dataSource, start_time_field)
    end_field = arcpy.AddFieldDelimiters(dataSource, end_time_field)
    for bin in nested_time_bin_pairs:
        start_time = bin[0]
        end_time = bin[1]
        start_string = start_time.strftime(time_format)
        end_string = end_time.strftime(time_format)
        SQLQuery = "{0} >= {1} '{2}' AND {3} < {4} '{5}'".format(start_field, prepended_sql_time, start_string,
                                                                 end_field, prepended_sql_time, end_string)
        QueryList.append(SQLQuery)
    return QueryList


@arcToolReport
def alphanumeric_split(time_string):
    """Splits an incoming string based on the first encounter of a alphabetic character after encountering digits.
     It will lower case and remove all white space in the string first, and return a number as float and alpha text
     as a string. """
    preprocessed_string = str(time_string).replace(" ", "").lower()
    string_list = [string for string in re.split(r'(\d+)', preprocessed_string) if string]
    number = float(string_list[0])
    string = str(string_list[1])
    return number, string


@arcToolReport
def parse_time_units_to_dt(float_magnitude, time_units):
    """This function will take a string with time units and a float associated with it. It will return
    a delta time based on the float and the passed time units. So float is 1 and time_units is 'hour' then
    it returns a time delta object equal to 1 hour"""
    micro_search = re.compile(r"microsecond")
    milli_search = re.compile(r"millisecond")
    second_search = re.compile(r"second")
    minute_search = re.compile(r"minute")
    hour_search = re.compile(r"hour")
    day_search = re.compile(r"day")
    week_search = re.compile(r"week")
    microseconds = 0
    milliseconds = 0
    seconds = 0
    minutes = 0
    hours = 0
    days = 0
    weeks = 0
    if re.search(micro_search, str(time_units)):
        microseconds = float_magnitude
    if re.search(milli_search, str(time_units)):
        milliseconds = float_magnitude
    if re.search(second_search, str(time_units)):
        seconds = float_magnitude
    if re.search(minute_search, str(time_units)):
        minutes = float_magnitude
    if re.search(hour_search, str(time_units)):
        hours = float_magnitude
    if re.search(day_search, str(time_units)):
        days = float_magnitude
    if re.search(week_search, str(time_units)):
        weeks = float_magnitude
    return datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds, minutes=minutes,
                              milliseconds=milliseconds, hours=hours, weeks=weeks)


@arcToolReport
def constructUniqueStringID(values, delimiter="."):
    """Creates a unique string id based on delimited passed values. The function will strip the last/first
     delimiters added.-David Wasserman"""
    final_chained_id = ""
    for value in values:
        final_chained_id = "{0}{1}{2}".format(final_chained_id, str(delimiter), str(value))
        final_chained_id = final_chained_id
    final_chained_id = final_chained_id.strip("{0}".format(delimiter))
    return final_chained_id


def join_record_dictionary(in_feature_class,join_dictionary,unique_id_field,join_fields_order):
    """Uses an arc update cursor to join fields to an input feature class. Inputs are a feature class, a
    join dictionary of form {unique_id_field:[ordered,join,field,list],the feature class join field, and the join fields
    in the same order as the lists in the join dictionary. """
    unique_id_list=join_dictionary.keys()
    cursor_fields= [unique_id_field]+join_fields_order
    feature_name=os.path.split(in_feature_class)[1]
    arcPrint("Joining dictionary to input feature class {0}.".format(feature_name),True)
    with arcpy.da.UpdateCursor(in_feature_class,cursor_fields) as join_cursor:
        for row in join_cursor:
            if row[0] in unique_id_list:
                values=join_dictionary[row[0]]
                if len(values)!= len(join_fields_order):
                    arcpy.AddError("Length of values in dictionary does not match join_fields_order.")
                value_index_list=enumerate(values,start=1)
                for index_value_pair in value_index_list :
                    try:
                        row[index_value_pair[0]]=index_value_pair[1]
                    except:
                        pass
            join_cursor.updateRow(row)



# Main Function Definition
@arcToolReport
def temporal_mean_center(inFeatureClass, outFeatureClass, start_time, end_time, time_interval, bin_start,
                         weight_field, case_field, dimension_field):
    """ This tool will split a feature class into multiple kernel densities based on a datetime field and a
    a set time interval. The result will be a time enabled moasic with Footprint. """
    try:
        outWorkSpace = os.path.dirname(outFeatureClass)
        if arcpy.Exists(outWorkSpace):
            arcpy.env.workspace = outWorkSpace
            arcpy.env.overwriteOutput = True
            arcPrint("The current work space is: {0}.".format(outWorkSpace), True)
            # Set up Work Space Environments
            out_workspace_path_split = os.path.split(outWorkSpace)
            workSpaceTail = out_workspace_path_split[1]
            inFeatureClassTail = os.path.split(inFeatureClass)[1]
            arcPrint("Gathering describe object information from workspace and input feature class.")
            ws_desc = arcpy.Describe(outWorkSpace)
            workspace_is_geodatabase = ws_desc.dataType == "Workspace" or ws_desc.dataType == "FeatureDataset"
            fin_output_workspace = outWorkSpace

            # Set up Time Deltas and Parse Time String
            arcPrint("Constructing Time Delta from input time period string.", True)
            time_magnitude, time_unit = alphanumeric_split(str(time_interval))
            time_delta = parse_time_units_to_dt(time_magnitude, time_unit)
            arcPrint(
                    "Using datetime fields to generate new feature classes in {0}.".format(
                            str(workSpaceTail)))
            arcPrint("Getting start and final times in start time field {0}.".format(start_time))
            start_time_min, start_time_max = get_min_max_from_field(inFeatureClass, start_time)
            # Establish whether to use end time field or only a start time (Single Date Field)
            if FieldExist(inFeatureClass, end_time) and end_time:
                arcPrint("Using start and end time to grab feature classes whose bins occur within an events "
                         "start or end time.")
                end_time_min, end_time_max = get_min_max_from_field(inFeatureClass, end_time)
                start_time_field = start_time
                end_time_field = end_time
                start_time_range = start_time_min
                end_time_range = end_time_max
            else:
                arcPrint("Using only first datetime start field to construct time bin ranges.")
                start_time_field = start_time
                end_time_field = start_time
                start_time_range = start_time_min
                end_time_range = start_time_max
            if isinstance(bin_start, datetime.datetime) or isinstance(bin_start, datetime.date):
                start_time_range = bin_start
                arcPrint("Bin Start Time was selected, using {0} as bin starting time period."
                         .format(str(bin_start_time)))
            time_bins = construct_time_bin_ranges(start_time_range, end_time_range, time_delta)
            arcPrint("Constructing queries based on datetime ranges.")
            temporal_queries = construct_sql_queries_from_time_bin(time_bins, inFeatureClass, start_time_field,
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
            temporal_record_dict={}
            arcPrint("Generating Mean Centers based on {0} queries.".format(len(temporal_queries)), True)
            for query in temporal_queries:
                try:
                    time_counter += 1
                    newFCName = "TempFCBin_{0}".format(str(time_counter))
                    if not workspace_is_geodatabase:
                        newFCName = newFCName[0:13]  # Truncate Name if not workspace.
                    arcPrint("Creating Mean Center with query '{0}'.".format(str(query)), True)
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
                    AddNewField(temporal_mean_center, join_id_field, "TEXT", field_alias="TEMPORAL_JOIN_ID")
                    join_fields = [join_id_field]
                    case_present = False
                    if FieldExist(temporal_mean_center, case_field):
                        join_fields = [join_id_field, case_field]
                        case_present = True
                    with arcpy.da.UpdateCursor(temporal_mean_center, join_fields) as join_cursor:
                        for row in join_cursor:
                            unique_id = constructUniqueStringID([str("1"), str(time_counter)])
                            if case_present:
                                unique_id = constructUniqueStringID([str(row[1]), str(time_counter)])
                            row[0] = unique_id
                            join_cursor.updateRow(row)
                            temporal_record_dict[unique_id]=[time_counter, start_date_time, end_date_time,
                                                          start_bin_time_string, end_bin_time_string, query]

                    if time_counter == 1:
                        arcPrint("Copying First Mean Center to Output Feature Class.")
                        arcpy.CopyFeatures_management(temporal_mean_center, outFeatureClass)
                    else:
                        arcPrint("Appending Mean Center to Output Feature Class.")
                        arcpy.Append_management(temporal_mean_center, outFeatureClass)
                    arcpy.Delete_management(temporal_mean_center)  # memory management
                except:
                    arcpy.AddWarning("Could not process query {0}.".format(str(query)))
            arcPrint("Adding time fields to output temporal feature class.", True)
            AddNewField(outFeatureClass, bin_number, "LONG")
            AddNewField(outFeatureClass, dt_starttime, "DATE", field_alias="Start Bin Datetime")
            AddNewField(outFeatureClass, dt_endtime, "DATE", field_alias="End Bin Datetime")
            AddNewField(outFeatureClass, txt_starttime, "TEXT", field_alias="Start Bin String")
            AddNewField(outFeatureClass, txt_endtime, "TEXT", field_alias="End Bin String")
            AddNewField(outFeatureClass, extract_query_field, "TEXT")

            arcPrint("Joining Temporal values by joining a dictionary to the unique ID.", True)
            table_fields = [bin_number,dt_starttime,dt_endtime,txt_starttime,txt_endtime,
                            extract_query_field]
            join_record_dictionary(outFeatureClass,temporal_record_dict,join_id_field, table_fields)
            arcPrint("Tool execution complete.", True)
            pass
        else:
            arcPrint("The desired workspace does not exist. Tool execution terminated.", True)
            arcpy.AddWarning("The desired workspace does not exist.")

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        arcPrint(str(e.args[0]))


# Main Script
if __name__ == "__main__":
    temporal_mean_center(inFeatureClass, outFeatureClass, start_time_field, end_time_field,
                         time_interval, bin_start_time, weight_field, case_field, dimension_field)
