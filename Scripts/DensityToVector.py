# --------------------------------
# Name: DensityToVector.py
# Purpose: This script is intended to help aid the network/vector analysis process by computing weighted kernel densities on
# list of incoming fields which represent weights for the KDE estimation. These estimations are then joined back to
# a network feature class. If provided a list of numbers, the tool will compute percentiles of the input densities
# and will add percentile scores to the input densities for non-zero/non-null values.
# Current Owner: David Wasserman
# Last Modified: 2/7/2018
# Copyright:   David Wasserman
# ArcGIS Version:   ArcGIS Pro/10.4
# Python Version:   3.5/2.7
# --------------------------------
# Copyright 2017 David J. Wasserman
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
import arcpy
import numpy as np
import SharedArcNumericalLib as san

try:
    import pandas as pd
except:
    arcpy.AddError("This library requires Pandas installed in the ArcGIS Python Install."
                   " Might require installing pre-requisite libraries and software.")
try:
    arcpy.CheckExtension("Spatial")
except:
    arcpy.AddError("This tool requires spatial analyst to function. Please add SA.")


# Function Definitions


def density_to_vector(in_fc, weighted_fields, input_network, percentile_bool=True, field_edit="", cell_size=500,
                      search_radius=800, area_unit="SQUARE_MILES",sample_points=1):
    """This function will compute kernel densities and associate them with a target network/vector file. If the
     percentile bool is true, percentile scores are added along side each density. """
    try:
        arcpy.env.overwriteOutput = True
        # Start Analysis
        desc = arcpy.Describe(input_network)
        work_space = desc.catalogPath
        temp_out_sample = "in_memory/sample_points_out"
        temp_sample_points = "in_memory/sample_points"
        temp_input_layer = "Temp_Input_Layer"
        san.arc_print("Generating sample points from feature class in memory...")
        arcpy.FeatureToPoint_management(input_network, temp_sample_points, True)
        final_df = None
        join_field = "JNField"
        oid_field = str(desc.OIDFieldName)
        for field in weighted_fields:
            san.arc_print("Computing density for field {0}...".format(field))
            arcpy.MakeFeatureLayer_management(in_fc, temp_input_layer,
                                              san.construct_sql_equality_query(field, None, work_space,
                                                                               noneEqualityOperator="is not"))
            output_kde = arcpy.sa.KernelDensity(in_fc, str(field), cell_size, search_radius, area_unit)
            arcpy.sa.ExtractValuesToPoints(temp_sample_points, output_kde, temp_out_sample, True)
            raw_sample_df = san.arcgis_table_to_dataframe(temp_out_sample, ["RASTERVALU"])
            new_field_name = "DN_" + str(field_edit) + str(field)
            raw_sample_df[new_field_name] = raw_sample_df["RASTERVALU"]
            raw_sample_df[new_field_name].replace([0], np.NaN, inplace=True)
            if percentile_bool:
                new_percentile_field = "Per_" + str(field_edit) + str(field)
                raw_sample_df[new_percentile_field] = raw_sample_df[new_field_name].rank(pct=True)
            field_list = [new_field_name, new_percentile_field] if percentile_bool else [new_field_name]
            if final_df is not None:
                final_df = pd.concat([final_df, raw_sample_df[field_list]], axis=1)
            else:
                raw_sample_df[join_field] = raw_sample_df.index
                final_df = raw_sample_df[[join_field] + field_list]
        san.arc_print("Extending density fields to table...")
        final_df = san.validate_df_names(final_df, work_space)
        fin_records = final_df.to_records()
        arcpy.da.ExtendTable(input_network, oid_field, fin_records, join_field, append_only=False)
        san.arc_print("Script Completed Successfully.", True)
    except arcpy.ExecuteError:
        san.arc_print(arcpy.GetMessages(2))
    except Exception as e:
        san.arc_print(e.args[0])


# End do_analysis function

# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Define input parameters
    input_feature_class = arcpy.GetParameterAsText(0)
    weighted_fields = arcpy.GetParameter(1)
    input_network = arcpy.GetParameterAsText(2)
    percentile_bool = arcpy.GetParameter(3)
    field_edit = arcpy.GetParameterAsText(4)
    cell_size = arcpy.GetParameter(5)
    search_radius = arcpy.GetParameter(6)
    area_unit_factor = arcpy.GetParameter(7)
    density_to_vector(input_feature_class, weighted_fields, input_network, bool(percentile_bool), field_edit, cell_size,
                      search_radius, area_unit_factor)
