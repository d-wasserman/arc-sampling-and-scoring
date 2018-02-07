# --------------------------------
# Name: TemporalKernelDensity.py
# Purpose: Runs multiple kernel densities on a feature class based on either a single time
#  or a start or end time based on a set datetime. The result is a temporally enabled moasic dataset.
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

@san.arc_tool_report
def recalculate_mosaic_statistics(mosaic_dataset):
    """ Recalculates ArcGIS Mosaic statistics and pyramids."""
    san.arc_print("Recalculating Mosaic Statistics.")
    arcpy.management.CalculateStatistics(mosaic_dataset)
    arcpy.management.BuildPyramidsandStatistics(mosaic_dataset, 'INCLUDE_SUBDIRECTORIES', 'BUILD_PYRAMIDS',
                                                'CALCULATE_STATISTICS')
    arcpy.RefreshCatalog(mosaic_dataset)


# Main Function Definition
@san.arc_tool_report
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
            san.arc_print("The current work space is: {0}.".format(outWorkSpace), True)
            # Set up Work Space Environments
            out_workspace_path_split = os.path.split(outWorkSpace)
            workSpaceTail = out_workspace_path_split[1]
            # arcpy.env.scratchWorkspace = out_workspace_path_split[0]
            inFeatureClassTail = os.path.split(inFeatureClass)[1]
            san.arc_print("Gathering describe object information from workspace and input feature class.")
            fc_desc = arcpy.Describe(inFeatureClass)
            # spatial_ref = fc_desc.spatialReference
            ws_desc = arcpy.Describe(outWorkSpace)
            workspace_is_geodatabase = ws_desc.dataType == "Workspace" or ws_desc.dataType == "FeatureDataset"
            if not workspace_is_geodatabase:
                arcpy.AddWarning("You neeed a valid geodatabase as workspace to create a moasic dataset,"
                                 " this tool will put raw raster files in the output workspace selected.")
            fin_output_workspace = outWorkSpace
            temporal_table_path = os.path.join(outWorkSpace, outTemporalName)
            try:
                san.arc_print("Attempting to create Temporal Table in output workspace.")

                arcpy.CreateTable_management(fin_output_workspace, outTemporalName)
                san.add_new_field(temporal_table_path,
                                  arcpy.ValidateFieldName("KernelDensityName", fin_output_workspace), "TEXT")
                san.add_new_field(temporal_table_path, arcpy.ValidateFieldName("Bin_Number", fin_output_workspace),
                                  "LONG")
                san.add_new_field(temporal_table_path, arcpy.ValidateFieldName("DT_Start_Bin", fin_output_workspace),
                                  "DATE", field_alias="Start Bin Datetime")
                san.add_new_field(temporal_table_path, arcpy.ValidateFieldName("DT_End_Bin", fin_output_workspace),
                                  "DATE", field_alias="End Bin Datetime")
                san.add_new_field(temporal_table_path, arcpy.ValidateFieldName("TXT_Start_Bin", fin_output_workspace),
                                  "TEXT", field_alias="Start Bin String")
                san.add_new_field(temporal_table_path, arcpy.ValidateFieldName("TXT_End_Bin", fin_output_workspace),
                                  "TEXT", field_alias="End Bin String")
                san.add_new_field(temporal_table_path, arcpy.ValidateFieldName("Extract_Query", fin_output_workspace),
                                  "TEXT")
                san.add_new_field(temporal_table_path, arcpy.ValidateFieldName("Raster_Path", fin_output_workspace),
                                  "TEXT")
            except:
                arcpy.AddWarning("Could not create Moasic Dataset Time Table. Time enablement is not possible.")
                pass
            try:
                arcpy.RefreshCatalog(outWorkSpace)
            except:
                san.arc_print("Could not refresh catalog.")
                pass
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
            # Transition to kernel density creation
            time_counter = 0
            temporal_record_table = []
            san.arc_print("Generating kernel densities based on {0} queries.".format(len(temporal_queries)), True)
            for query in temporal_queries:
                try:
                    time_counter += 1
                    san.arc_print("Determining name and constructing query for new feature class.", True)
                    newFCName = "Bin_{0}_{1}".format(time_counter,
                                                     arcpy.ValidateTableName(inFeatureClassTail, fin_output_workspace))
                    if not workspace_is_geodatabase:
                        newFCName = newFCName[0:13]  # Truncate Name if not workspace.
                    san.arc_print(
                        "Created Kernel Density {0} with query '{1}' and created a new raster in {2}".format(
                            newFCName, str(query), workSpaceTail), True)
                    temporary_layer = arcpy.MakeFeatureLayer_management(inFeatureClass, newFCName, query)
                    # Break up general density to have pop field set to none if no actually field exists.
                    if not san.field_exist(inFeatureClass, kernel_pop_field):
                        kernel_pop_field = "NONE"
                    out_raster = arcpy.sa.KernelDensity(temporary_layer, kernel_pop_field, kernel_cell_size,
                                                        kernel_search_rad,
                                                        kernel_area_unit, kernel_out_values, kernel_method)

                    san.arc_print("Saving output raster: {0}.".format(newFCName))
                    raster_path = os.path.join(fin_output_workspace, str(newFCName))
                    out_raster.save(raster_path)
                    start_date_time = time_bins[time_counter - 1][0]
                    end_date_time = time_bins[time_counter - 1][1]
                    start_bin_time_string = str(start_date_time)
                    end_bin_time_string = str(end_date_time)
                    if not workspace_is_geodatabase:
                        arcpy.AddWarning("DBF tables can only accept date fields, not datetimes."
                                         " Please check string field.")
                        start_date_time = start_date_time.date()
                        end_date_time = end_date_time.date()
                    temporal_record_table.append([newFCName, time_counter, start_date_time, end_date_time,
                                                  start_bin_time_string, end_bin_time_string, query, raster_path])
                    del out_raster
                except Exception as e:
                    san.arc_print(
                        "The feature raster ID {0}, could not be saved. Check arguments".format(
                            str(newFCName)))
                    arcpy.AddWarning(str(e.args[0]))
                    pass

            san.arc_print("Adding record values to Temporal Table with an insert cursor.")
            table_fields = san.get_fields(temporal_table_path)
            with arcpy.da.InsertCursor(temporal_table_path, table_fields) as cursor:
                for records in temporal_record_table:
                    cursor.insertRow(records)
                san.arc_print("Finished inserting records for database.")
                del cursor

            if compactBool:
                try:
                    san.arc_print("Compacting workspace.", True)
                    arcpy.Compact_management(outWorkSpace)
                except:
                    san.arc_print("Not a Compact capable workspace.")
                    pass
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
    outWorkSpace = arcpy.GetParameterAsText(1)
    outputTableName = arcpy.GetParameterAsText(2)
    outputMosaicName = "TemporalMD"  # To be finished...
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
    temporal_kernel_density(inFeatureClass, outWorkSpace, outputTableName, start_time_field, end_time_field,
                            time_interval,
                            bin_start=bin_start_time, kernel_pop_field=population_field, kernel_cell_size=cell_size,
                            kernel_search_rad=search_radius, kernel_area_unit=area_unit_scale_factor,
                            kernel_out_values=out_cell_values, compactBool=compactWorkspace)
