# Name: CreateClassGroupField.py
# Purpose: Will group selected fields into a unique group field for every unique combination of the selected fields.
# Author: David Wasserman
# Last Modified: 2/7/2021
# Copyright: David Wasserman
# Python Version:   2.7-3.1
# ArcGIS Version: 10.3.1 (Pro)
# --------------------------------
# Copyright 2016 David J. Wasserman
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
import os, arcpy
import SharedArcNumericalLib as san
import itertools


# Function Definitions
def constructChainedSQLQuery(
    fieldNames,
    values,
    dataSource,
    chainOperator="AND",
    equalityOperator="=",
    noneEqualityOperator="is",
):
    """Creates a workspace sensitive equality query that is chained with some intermediary operator. The function
    will strip the last operator added. The passed fieldNames and values are both assumed to be ordered.
    David Wasserman"""
    fieldNamesLength, valuesLength = len(fieldNames), len(values)
    index_range = range(min(fieldNamesLength, valuesLength))
    final_chained_query = ""
    if fieldNamesLength != valuesLength:
        error_pot_string = "WARNING:Construct Chained SQL Query value/fields lengths do not match. Used minimum. QAQC"
        print(error_pot_string)
        arcpy.AddMessage(error_pot_string)
        arcpy.AddWarning(error_pot_string)
    for idx in index_range:
        base_query = san.constructSQLEqualityQuery(
            fieldNames[idx],
            values[idx],
            dataSource,
            equalityOperator,
            noneEqualityOperator,
        )
        if idx == 0:
            final_chained_query = "{0} {1}".format(base_query, final_chained_query)
        else:
            final_chained_query = "{0} {1} {2}".format(
                base_query, chainOperator.strip(), final_chained_query
            )
    return final_chained_query


@san.arc_tool_report
def constructUniqueStringID(values, delimiter="."):
    """Creates a unique string id based on delimited passed values. The function will strip the last/first
    delimiters added.-David Wasserman"""
    final_chained_id = ""
    for value in values:
        final_chained_id = "{0}{1}{2}".format(
            final_chained_id, str(delimiter), str(value)
        )
        final_chained_id = final_chained_id
    final_chained_id = final_chained_id.strip("{0}".format(delimiter))
    return final_chained_id


def create_class_group_field(in_fc, input_fields, basename="GROUP_"):
    """This function will take in an feature class, and use pandas/numpy to calculate Z-scores and then
    join them back to the feature class using arcpy.
        Parameters
    -----------------
    in_fc- input feature class to add percentile fields
    input_fields - input fields to build a unique id from
    basename- base name for group fields."""
    try:
        arcpy.env.overwriteOutput = True
        desc = arcpy.Describe(in_fc)
        workspace = os.path.dirname(desc.catalogPath)
        input_Fields_List = input_fields.split(";")
        san.arc_print("Adding Class Fields.", True)
        valid_num_field = arcpy.ValidateFieldName("{0}_Num".format(basename), workspace)
        valid_text_field = arcpy.ValidateFieldName(
            "{0}_Text".format(basename), workspace
        )
        san.add_new_field(in_fc, valid_num_field, "LONG")
        san.add_new_field(in_fc, valid_text_field, "TEXT")
        san.arc_print("Constructing class groups within dictionary.", True)
        unique_class_dict = {}
        cursor_fields = input_Fields_List + [valid_text_field, valid_num_field]
        with arcpy.da.UpdateCursor(in_fc, cursor_fields) as cursor:
            counter = 0
            group_id = 1
            for row in cursor:
                try:
                    group_field_values = row[:-2]  # Grab all but last two fields.
                    unique_id = constructUniqueStringID(group_field_values)
                    if unique_id not in unique_class_dict:
                        unique_class_dict[unique_id] = group_id
                        group_id += 1
                    row[-1] = unique_class_dict[unique_id]
                    row[-2] = unique_id
                    cursor.updateRow(row)
                    counter += 1
                except Exception as e:
                    san.arc_print(
                        "ERROR: Skipped at iteration {0}. QAQC.".format(counter), True
                    )
                    san.arc_print(str(e.args[0]))
        del unique_class_dict
        san.arc_print("Script Completed Successfully.", True)

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
    except Exception as e:
        arcpy.AddError(e.args[0])
        # End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == "__main__":
    # Define Inputs
    FeatureClass = arcpy.GetParameterAsText(0)  # r"C:"
    InputFields = arcpy.GetParameterAsText(1)  # "CBSA_POP;D5cri"
    BaseName = arcpy.GetParameterAsText(2)  # "GROUP"
    create_class_group_field(FeatureClass, InputFields, BaseName)
