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
outputMosaicName = arcpy.GetParameterAsText(2)
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


@arcToolReport
def recalculate_mosaic_statistics(mosaic_dataset):
    arcPrint("Recalculating Mosaic Statistics.")
    arcpy.management.CalculateStatistics(mosaic_dataset)
    arcpy.management.BuildPyramidsandStatistics(mosaic_dataset, 'INCLUDE_SUBDIRECTORIES', 'BUILD_PYRAMIDS',
                                                'CALCULATE_STATISTICS')
    arcpy.RefreshCatalog(mosaic_dataset)


@arcToolReport
def FieldExist(featureclass, fieldname):
    # Check if a field in a feature class field exists and return true it does, false if not.
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
    string_list = filter(None, re.split(r'(\d+)', preprocessed_string))
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
def temporal_kernel_density(inFeatureClass, outWorkSpace, outMosaicName, start_time, end_time, time_interval,
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
            scratchDatabase = outWorkSpace
            arcPrint("Gathering describe object information from workspace and input feature class.")
            fc_desc = arcpy.Describe(inFeatureClass)
            spatial_ref = fc_desc.spatialReference
            ws_desc = arcpy.Describe(outWorkSpace)
            if ws_desc.dataType != "Workspace":
                arcpy.AddWarning("You neeed a valid geodatabase as workspace to create a moasic dataset,"
                                 " this tool will put raw raster files in the output workspace selected.")

            created_Moasic = False
            fin_output_workspace = outWorkSpace
            try:
                arcPrint("Attempting to create Mosaic dataset in output workspace.")
                arcpy.CreateMosaicDataset_management(outWorkSpace, outMosaicName, spatial_ref,
                                                     "1", "32_BIT_FLOAT", "NONE", "NONE")
                created_Moasic = True
                fin_output_workspace = os.path.join(outWorkSpace, outMosaicName)
            except:
                arcpy.AddWarning("Could not create Moasic Dataset. Time enablement is not possible.")
                pass

            # Set up Time Deltas and Parse Time String
            arcPrint("Constructing Time Delta from input time period string.", True)
            time_magnitude, time_unit = alphanumeric_split(time_interval)
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
            arcPrint("Generating kernel densities based on {0} queries.".format(len(temporal_queries)), True)
            for query in temporal_queries:
                try:
                    time_counter += 1
                    arcPrint("Determining name and constructing query for new feature class.", True)
                    newFCName = "Bin_{0}_{1}".format(time_counter,
                                                     arcpy.ValidateTableName(inFeatureClassTail, fin_output_workspace))
                    expression = str(query)
                    arcPrint(
                            "Created Kernel Density {0} with query [{1}] and created a new raster in {2}".format(
                                    newFCName, expression, workSpaceTail), True)
                    temporary_layer = arcpy.MakeFeatureLayer_management(inFeatureClass, newFCName, query)
                    # Break up general density to have pop field set to none if no actually field exists.
                    if not FieldExist(inFeatureClass, kernel_pop_field):
                        kernel_pop_field = "NONE"
                    out_raster = arcpy.sa.KernelDensity(temporary_layer, kernel_pop_field, kernel_cell_size,
                                                        kernel_search_rad,
                                                        kernel_area_unit, kernel_out_values, kernel_method)
                    temporary_raster_path = os.path.join(scratchDatabase, str(newFCName))
                    out_raster.save(temporary_raster_path)

                    if created_Moasic:
                        arcPrint("Adding raster {0}, to Mosaic dataset.".format(newFCName))
                        arcpy.AddRastersToMosaicDataset_management(fin_output_workspace, "Raster Dataset",
                                                                   temporary_raster_path,
                                                                   update_cellsize_ranges="UPDATE_CELL_SIZES",
                                                                   update_overviews="UPDATE_OVERVIEWS",
                                                                   sub_folder="NO_SUBFOLDERS",
                                                                   build_pyramids="BUILD_PYRAMIDS",
                                                                   calculate_statistics="CALCULATE_STATISTICS",
                                                                   duplicate_items_action="OVERWRITE_DUPLICATES")
                    else:
                        arcPrint("Not saving rasters in a Mosaic dataset, saving it in work space: {0}.".format(
                                fin_output_workspace))
                        out_raster.save(os.path.join(fin_output_workspace, str(newFCName)[0:13]))
                    del out_raster
                except Exception as e:
                    arcPrint(
                            "The feature raster ID {0}, could not be extracted to Mosaic. Check arguments".format(
                                    str(newFCName)))
                    arcpy.AddWarning(str(e.args[0]))
                    pass
            #Synchronize and update
            arcpy.SynchronizeMosaicDataset_management()
            # Database Clean up
            if arcpy.Exists(scratchDatabase):
                arcpy.Delete_management(scratchDatabase)
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
    temporal_kernel_density(inFeatureClass, outWorkSpace, outputMosaicName, start_time_field, end_time_field,
                            time_interval,
                            bin_start=bin_start_time, kernel_pop_field=population_field, kernel_cell_size=cell_size,
                            kernel_search_rad=search_radius, kernel_area_unit=area_unit_scale_factor,
                            kernel_out_values=out_cell_values, compactBool=compactWorkspace)
