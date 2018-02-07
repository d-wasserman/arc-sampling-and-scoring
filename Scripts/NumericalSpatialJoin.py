# --------------------------------
# Name: NumericalSpatialJoin.py
# Purpose: This script is intended to provide an alternative method and GUI for spatial joins so that target feature
# classes are set to first and additional join fields are chosen by statistic. A field is provided to change the name.
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
import SharedArcNumericalLib as san


# Function Definitions

def statistical_spatial_join(target_feature, join_features, out_feature_class, prepended_field_name="",
                             join_operation="JOIN_ONE_TO_ONE", join_type=True, match_option="INTERSECT",
                             search_radius=None, merge_rule_dict={}):
    """This function will join features to a target feature class using merge fields that are chosen based on the
     chosen summary statistics fields from the join feature class while keeping all the fields in the target."""
    try:
        arcpy.env.overwriteOutput = True
        # Start Analysis
        san.arc_print("Generating fieldmapping...")
        f_map = san.generate_statistical_fieldmap(target_feature, join_features, prepended_field_name, merge_rule_dict)
        san.arc_print("Conducting spatial join...")
        arcpy.SpatialJoin_analysis(target_features=target_feature, join_features=join_features,
                                   out_feature_class=out_feature_class, join_operation=join_operation,
                                   join_type=join_type, match_option=match_option, search_radius=search_radius
                                   , field_mapping=f_map)
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
    output_feature_Class = arcpy.GetParameterAsText(2)
    prepended_field_name = arcpy.GetParameterAsText(3)
    join_operation = arcpy.GetParameterAsText(4)
    join_type = "KEEP_ALL" if bool(arcpy.GetParameter(5)) else "KEEP_COMMON"
    match_option = str(arcpy.GetParameterAsText(6)).strip()
    search_radius = arcpy.GetParameter(7)
    # Simplify processing by associating input lists to target merge rules
    merge_rule_dict = {}
    merge_rule_identifiers = ["SUM", "MEAN", "MEDIAN", "MODE", "STD", "MIN", "MAX", "RANGE", "COUNT", "FIRST"]
    for merge_rule, index in zip(merge_rule_identifiers, range(8, 17)):
        merge_rule_dict[merge_rule] = [field for field in arcpy.GetParameterAsText(index).split(";") if
                                       san.field_exist(join_feature_class, field)]
    statistical_spatial_join(target_feature_class, join_feature_class, output_feature_Class, prepended_field_name,
                             join_operation, join_type, match_option, search_radius, merge_rule_dict)
