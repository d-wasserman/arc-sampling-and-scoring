# --------------------------------
# Name: TemporalKernelDensity.py
# Purpose: Runs multiple kernel densities on a feature class based on either a single time
#  or a start or end time based on a set datetime. The result is a temporally enabled moasic dataset.
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
outWorkSpace = arcpy.GetParameterAsText(1)
outputTableName = arcpy.GetParameterAsText(2)
outputMosaicName = "TemporalMD" # To be finished...
start_time_field = arcpy.GetParameterAsText(3)
end_time_field = arcpy.GetParameterAsText(4)
time_interval = arcpy.GetParameter(5)
bin_start_time = arcpy.GetParameter(6)
# Kernel Density Params
population_field = arcpy.GetParameterAsText(7)  # Default to NONE
cell_size = arcpy.GetParameter(8)  # Default to 50
search_radius = arcpy.GetParameter(9)  # Required
area_unit_scale_factor = arcpy.GetParameterAsText(10)  # Default "SQUARE_MILES"
out_cell_values = arcpy.GetParameter(11)  # Default "DENSITY"
# Optional Finish
compactWorkspace = arcpy.GetParameter(12)


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
    string_list=[string for string in re.split(r'(\d+)', preprocessed_string) if string]
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


# Main Function Definition
@arcToolReport
def temporal_kernel_density(inFeatureClass, outWorkSpace, outTemporalName, start_time, end_time, time_interval,
                            kernel_pop_field,
                            kernel_cell_size, kernel_search_rad, kernel_area_unit, kernel_out_values="DENSITIES",
                            kernel_method="PLANAR", bin_start=None, compactBool=True):
    """ This tool will split a feature class into multiple kernel densities based on a datetime field and a
    a set time interval. The result will be a time enabled moasic with Footprint. """
    try:
        if arcpy.Exists(outWorkSpace):
            arcpy.env.workspace = outWorkSpace
            arcpy.env.overwriteOutput = True
            arcPrint("The current work space is: {0}.".format(outWorkSpace), True)
            # Set up Work Space Environments
            out_workspace_path_split = os.path.split(outWorkSpace)
            workSpaceTail = out_workspace_path_split[1]
            #arcpy.env.scratchWorkspace = out_workspace_path_split[0]
            inFeatureClassTail = os.path.split(inFeatureClass)[1]
            arcPrint("Gathering describe object information from workspace and input feature class.")
            fc_desc = arcpy.Describe(inFeatureClass)
            #spatial_ref = fc_desc.spatialReference
            ws_desc = arcpy.Describe(outWorkSpace)
            workspace_is_geodatabase =ws_desc.dataType== "Workspace"
            if not workspace_is_geodatabase:
                arcpy.AddWarning("You neeed a valid geodatabase as workspace to create a moasic dataset,"
                                 " this tool will put raw raster files in the output workspace selected.")
            fin_output_workspace = outWorkSpace
            temporal_table_path=os.path.join(outWorkSpace, outTemporalName)
            try:
                arcPrint("Attempting to create Temporal Table in output workspace.")
                arcpy.CreateTable_management(fin_output_workspace,outTemporalName)
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("KernelDensityName",fin_output_workspace),"TEXT")
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("Bin_Number",fin_output_workspace),"LONG")
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("DT_Start_Bin",fin_output_workspace),"DATE",field_alias="Start Bin Datetime")
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("DT_End_Bin",fin_output_workspace),"DATE",field_alias="End Bin Datetime")
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("TXT_Start_Bin",fin_output_workspace),"TEXT",field_alias="Start Bin String")
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("TXT_End_Bin",fin_output_workspace),"TEXT",field_alias="End Bin String")
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("Extract_Query",fin_output_workspace),"TEXT")
                AddNewField(temporal_table_path,arcpy.ValidateFieldName("Raster_Path",fin_output_workspace),"TEXT")
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
            # Transition to kernel density creation
            time_counter = 0
            temporal_record_table=[]
            arcPrint("Generating kernel densities based on {0} queries.".format(len(temporal_queries)), True)
            for query in temporal_queries:
                try:
                    time_counter += 1
                    arcPrint("Determining name and constructing query for new feature class.", True)
                    newFCName = "Bin_{0}_{1}".format(time_counter,
                                                     arcpy.ValidateTableName(inFeatureClassTail, fin_output_workspace))
                    if not workspace_is_geodatabase:
                        newFCName = newFCName[0:13] #Truncate Name if not workspace.
                    arcPrint(
                            "Created Kernel Density {0} with query [{1}] and created a new raster in {2}".format(
                                    newFCName, str(query), workSpaceTail), True)
                    temporary_layer = arcpy.MakeFeatureLayer_management(inFeatureClass, newFCName, query)
                    # Break up general density to have pop field set to none if no actually field exists.
                    if not FieldExist(inFeatureClass, kernel_pop_field):
                        kernel_pop_field = "NONE"
                    out_raster = arcpy.sa.KernelDensity(temporary_layer, kernel_pop_field, kernel_cell_size,
                                                        kernel_search_rad,
                                                        kernel_area_unit, kernel_out_values, kernel_method)



                    arcPrint("Saving output raster: {0}.".format(newFCName))
                    raster_path= os.path.join(fin_output_workspace, str(newFCName))
                    out_raster.save(raster_path)
                    start_date_time=time_bins[time_counter-1][0]
                    end_date_time=time_bins[time_counter-1][1]
                    start_bin_time_string=str(start_date_time)
                    end_bin_time_string=str(end_date_time)
                    if not workspace_is_geodatabase:
                        arcpy.AddWarning("DBF tables can only accept date fields, not datetimes."
                                         " Please check string field.")
                        start_date_time=start_date_time.date()
                        end_date_time=end_date_time.date()
                    temporal_record_table.append([newFCName,time_counter,start_date_time,end_date_time,
                                                  start_bin_time_string,end_bin_time_string,query,raster_path])
                    del out_raster
                except Exception as e:
                    arcPrint(
                            "The feature raster ID {0}, could not be saved. Check arguments".format(
                                    str(newFCName)))
                    arcpy.AddWarning(str(e.args[0]))
                    pass

            arcPrint("Adding record values to Temporal Table with an insert cursor.")
            table_fields= getFields(temporal_table_path)
            with arcpy.da.InsertCursor(temporal_table_path,table_fields) as cursor:
                for records in temporal_record_table:
                    cursor.insertRow(records)
                arcPrint("Finished inserting records for database.")
                del cursor

            if compactBool:
                try:
                    arcPrint("Compacting workspace.", True)
                    arcpy.Compact_management(outWorkSpace)
                except:
                    arcPrint("Not a Compact capable workspace.")
                    pass
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
    temporal_kernel_density(inFeatureClass, outWorkSpace, outputTableName, start_time_field, end_time_field,
                            time_interval,
                            bin_start=bin_start_time, kernel_pop_field=population_field, kernel_cell_size=cell_size,
                            kernel_search_rad=search_radius, kernel_area_unit=area_unit_scale_factor,
                            kernel_out_values=out_cell_values, compactBool=compactWorkspace)
