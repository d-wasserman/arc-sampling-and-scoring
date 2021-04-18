# --------------------------------
# Name: ProportionalAllocation.py
# Purpose: This script is intended to provide a way to use sampling geography that will calculate proportional
# averages or sums based on the percentage of an intersection covered by the sampling geography. The output is
# the sampling geography with fields sampled from the base features.
# Current Owner: David Wasserman
# Last Modified: 4/17/2021
# Copyright:   David Wasserman
# ArcGIS Version:   ArcGIS Pro
# Python Version:   3.6
# --------------------------------
# Copyright 2021 David J. Wasserman
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
import os
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

import SharedArcNumericalLib as san


# Function Definitions

def proportional_allocation(sampling_features, base_features, out_feature_class,
                            sum_fields=[], mean_fields=[]):
    """This script is intended to provide a way to use sampling geography that will calculate proportional
     averages or sums based on the percentage of an intersection covered by the sampling geography. The output is
     the sampling geography with fields sampled from the base features.
     Parameters
     --------------------
     sampling_features - The sampling features are the features you want to associate proportional averages or sums
     from the attributes in the base features. The output will look like this input polygon layer with new fields.
     base_features- The base features have the attributes being sampled by the polygon sampling features.
     out_feature_class - The output feature class is a copy of the sampling features with new sum & average fields
     sum_fields - Fields to proportionally sum (based on the overlapping areas between the sampling and base features)
     from the base to the sampling features.
     mean_fields - Fields to proportionally average (based on the overlapping areas between the sampling and base features)
     from the base to the sampling features.
     """
    try:
        arcpy.env.overwriteOutput = True
        # Start Analysis
        temp_intersect = os.path.join("in_memory", "temp_intersect")
        san.arc_print("Calculating original areas...")
        base_area_col = "Base_Area_SQMI"
        inter_area_col = "Inter_Area_SQMI"
        sampling_id = "Sampling_ID"
        ratio_coverage = "Proportion"
        san.add_new_field(base_features, base_area_col, "DOUBLE")
        arcpy.CalculateField_management(base_features, base_area_col, "!shape.area@SQUAREMILES!")
        san.add_new_field(sampling_features, "Sampling_ID", "LONG")
        oid_s = arcpy.Describe(sampling_features).OIDFieldName
        arcpy.CalculateField_management(sampling_features, sampling_id, "!{0}!".format(oid_s))
        san.arc_print("Conducting an intersection...", True)
        arcpy.Intersect_analysis([[sampling_features, 1], [base_features, 1]], temp_intersect)
        san.add_new_field(temp_intersect, inter_area_col, "DOUBLE")
        arcpy.CalculateField_management(temp_intersect, inter_area_col, "!shape.area@SQUAREMILES!")
        san.arc_print("Calculating proportional sums and/or averages...", True)
        all_fields = [sampling_id, inter_area_col, base_area_col] + sum_fields + mean_fields
        inter_df = san.arcgis_table_to_df(temp_intersect, all_fields)
        inter_df[ratio_coverage] = inter_df[inter_area_col].fillna(0) / inter_df[base_area_col].fillna(1)
        all_stats = sum_fields + mean_fields
        for field in all_stats:
            inter_df[field] = inter_df[field] * inter_df[ratio_coverage]  # Weight X Value
        inter_groups = inter_df.groupby(sampling_id).sum()
        for mean in mean_fields:
            inter_groups[mean] = inter_groups[mean] / inter_groups[ratio_coverage]  # Divide by sum of weights for wm
        san.arc_print("Associating results to sampled SEDF...")
        samp_df = pd.DataFrame.spatial.from_featureclass(sampling_features)
        samp_df = samp_df.merge(inter_groups, how="left", left_on=sampling_id, right_index=True,
                                suffixes=("DELETE_X", "DELETE_Y"))
        kept_cols = [i for i in samp_df.columns if "DELETE" not in i]
        samp_df = samp_df[kept_cols].copy()
        sum_rename = {i:"SUM_"+str(i) for i in sum_fields}
        mean_rename = {i: "MEAN_" + str(i) for i in mean_fields}
        sum_rename.update(mean_rename)
        samp_df = samp_df.rename(columns=sum_rename)
        san.arc_print("Exporting results...", True)
        samp_df.spatial.to_featureclass(out_feature_class)
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
    target_feature_class = arcpy.GetParameterAsText(0)
    join_feature_class = arcpy.GetParameterAsText(1)
    output_feature_class = arcpy.GetParameterAsText(2)
    sum_fields = arcpy.GetParameterAsText(3).split(";")
    mean_fields = arcpy.GetParameterAsText(4).split(";")
    proportional_allocation(target_feature_class, join_feature_class, output_feature_class, sum_fields, mean_fields)
