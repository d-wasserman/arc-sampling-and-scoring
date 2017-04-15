# --------------------------------
# Name: TemporalAggregator.py
# Purpose: Bin on a temporal field and generate summary statistics in a new stacked feature class based on either a
# single time or a start or end time based on a set datetime. The result is a temporally enabled moasic dataset.
# Current Owner: David Wasserman
# Last Modified: 8/17/2016
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
import arcpy, os, datetime, re
import pandas as pd
import numpy as np

# Define Inputs
# Temporal Params
inFeatureClass = arcpy.GetParameterAsText(0)
outputFeatureclass = arcpy.GetParameterAsText(1)
start_time_field = arcpy.GetParameterAsText(3)
end_time_field = arcpy.GetParameterAsText(4)
time_interval = arcpy.GetParameter(5)
bin_start_time = arcpy.GetParameter(6)
# Kernel Density Params
case_field = arcpy.GetParameter(7)
weight_field = arcpy.GetParameter(8)  # Default to NONE
summary_field = arcpy.GetParameter(9)


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
def recalculate_mosaic_statistics(mosaic_dataset):
    """ Recalculates ArcGIS Mosaic statistics and pyramids."""
    arcPrint("Recalculating Mosaic Statistics.")
    arcpy.management.CalculateStatistics(mosaic_dataset)
    arcpy.management.BuildPyramidsandStatistics(mosaic_dataset, 'INCLUDE_SUBDIRECTORIES', 'BUILD_PYRAMIDS',
                                                'CALCULATE_STATISTICS')
    arcpy.RefreshCatalog(mosaic_dataset)


@arcToolReport
def FieldExist(featureclass, fieldname):
    """ Check if a field in a feature class field exists and return true it does, false if not."""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1):  # If there is one or more of this field return true
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
    """Get min and max value from input data."""
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        data = [row[0] for row in cursor]
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
def ArcGISTabletoDataFrame(in_fc, input_Fields, query="", skip_nulls=False, null_values=None):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields."""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    final_Fields = [OIDFieldName] + input_Fields
    arcPrint("Converting feature class table to numpy array.", True)
    npArray = arcpy.da.TableToNumPyArray(in_fc, final_Fields, query, skip_nulls, null_values)
    objectIDIndex = npArray[OIDFieldName]
    arcPrint("Converting feature class numpy array into pandas dataframe.", True)
    fcDataFrame = pd.DataFrame(npArray, index=objectIDIndex, columns=input_Fields)
    return fcDataFrame


# Main Function Definition
@arcToolReport
def temporal_aggregate_field(inFeatureClass, outFeatureClass, start_time, end_time, time_interval,
                             weight_field="#", case_field="#", summary_field="#", bin_start=None):
    """ This tool will split a feature class into multiple kernel densities based on a datetime field and a
    a set time interval. The result will be a time enabled moasic with Footprint. """
    try:
        splitOutPath = os.path.split(outFeatureClass)
        outWorkSpace = splitOutPath[0]
        outFCTail = splitOutPath[1]
        fin_output_workspace = outWorkSpace
        if arcpy.Exists(fin_output_workspace):
            arcpy.env.workspace = fin_output_workspace
            arcpy.env.overwriteOutput = True
            arcPrint("The current work space is: {0}.".format(fin_output_workspace), True)
            # Set up Work Space Environments
            out_workspace_path_split = os.path.split(fin_output_workspace)
            workSpaceTail = out_workspace_path_split[1]
            inFeatureClassTail = os.path.split(inFeatureClass)[1]
            ws_desc = arcpy.Describe(fin_output_workspace)
            workspace_is_geodatabase = ws_desc.dataType == "Workspace"
            arcPrint("Gathering describe object information from fields and input feature class.")
            fc_desc = arcpy.Describe(inFeatureClass)
            summary_field_type = arcpy.Describe(weight_field).type

            try:
                arcPrint("Attempting to create Temporal Table in output workspace.")
                arcpy.CreateFeatureclass_management(splitOutPath, outFCTail, 'POINT')
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Unique_ID", fin_output_workspace), "TEXT")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_Number", fin_output_workspace), "LONG")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("DT_Start_Bin", fin_output_workspace), "DATE",
                            field_alias="Start Bin Datetime")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("DT_End_Bin", fin_output_workspace), "DATE",
                            field_alias="End Bin Datetime")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("TXT_Start_Bin", fin_output_workspace), "TEXT",
                            field_alias="Start Bin String")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("TXT_End_Bin", fin_output_workspace), "TEXT",
                            field_alias="End Bin String")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Extract_Query", fin_output_workspace), "TEXT")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_Count", fin_output_workspace), "DOUBLE")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_Mean", fin_output_workspace), "DOUBLE")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_Median", fin_output_workspace), "DOUBLE")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_Sum", fin_output_workspace), "DOUBLE")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_StdDev", fin_output_workspace), "DOUBLE")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_Min", fin_output_workspace), "DOUBLE")
                AddNewField(outFeatureClass, arcpy.ValidateFieldName("Bin_Max", fin_output_workspace), "DOUBLE")
            except:
                arcpy.AddWarning("Could not create Moasic Dataset. Time enablement is not possible.")
                pass
            try:
                arcpy.RefreshCatalog(outWorkSpace)
            except:
                arcPrint("Could not refresh catalog.")
                pass
            # Set up Time Deltas and Parse Time String
            arcPrint("Constructing Time Delta from input time period string.", True)
            arcPrint(str(time_interval))
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
            temporary_fc_name = "Temp_{1}".format(
                    arcpy.ValidateTableName(inFeatureClassTail, fin_output_workspace)[0:13])
            temporary_fc_path = os.path.join(fin_output_workspace, temporary_fc_name)
            # Transition to kernel density creation
            time_counter = 0
            temporal_record_table = []
            arcPrint("Generating kernel densities based on {0} queries.".format(len(temporal_queries)), True)
            for query in temporal_queries:
                try:
                    time_counter += 1
                    arcPrint("Determining name and constructing query for new feature class.", True)
                    # Break up general density to have pop field set to none if no actually field exists.

                    temporary_layer = arcpy.MakeFeatureLayer_management(inFeatureClass, temporary_fc_name, query)
                    tempoary_dataframe = ArcGISTabletoDataFrame()
                    arcPrint(
                            "Created Mean Center {0} with query [{1}], appending to master feature class.".format(
                                    temporary_fc_name, str(query)), True)
                    arcpy.MeanCenter_stats(temporary_layer, temporary_fc_path, weight_field, case_field)
                    start_date_time = time_bins[time_counter - 1][0]
                    end_date_time = time_bins[time_counter - 1][1]
                    start_bin_time_string = str(start_date_time)
                    end_bin_time_string = str(end_date_time)
                    if not workspace_is_geodatabase:
                        arcpy.AddWarning("DBF tables can only accept date fields, not datetimes."
                                         " Please check string field.")
                        start_date_time = start_date_time.date()
                        end_date_time = end_date_time.date()
                    temporal_record_table.append([time_counter, start_date_time, end_date_time,
                                                  start_bin_time_string, end_bin_time_string, query])

                except Exception as e:
                    arcPrint(
                            "The feature bin ID {0}, could not be processed. Check arguments".format(
                                    str(query)))
                    arcpy.AddWarning(str(e.args[0]))
                    pass

            # arc_print("Adding record values to Temporal Table with an insert cursor.")
            # table_fields= get_fields(outFeatureClass)
            # with arcpy.da.InsertCursor(outFeatureClass,table_fields) as cursor:
            #     for records in temporal_record_table:
            #         cursor.insertRow(records)
            #     arc_print("Finished inserting records for database.")
            #     del cursor
            # arc_print("Tool execution complete.", True)
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
    temporal_aggregate_field(inFeatureClass, outputFeatureclass, start_time_field, end_time_field,
                             time_interval, bin_start=bin_start_time, weight_field=weight_field,
                             case_field=case_field, summary_field=summary_field)
