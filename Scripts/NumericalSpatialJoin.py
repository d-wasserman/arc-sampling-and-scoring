# --------------------------------
# Name: NumericalSpatialJoin.py
# Purpose: This script is intended to provide an alternative method and GUI for spatial joins so that target feature
# classes are set to first and additional join fields are chosen by statistic. A field is provided to change the name.
# Current Owner: David Wasserman
# Last Modified: 10/15/2017
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


# Function Definitions
def func_report(function=None, reportBool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def func_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if reportBool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Ouput(s):{0}".format(str(func_result)))
                return func_result
            except Exception as e:
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return func_wrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return func_report_decorator(function)

        return waiting_for_function
    else:
        return func_report_decorator(function)


def arc_tool_report(function=None, arcToolMessageBool=False, arcProgressorBool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def arc_tool_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if arcToolMessageBool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(func_result)))
                if arcProgressorBool:
                    arcpy.SetProgressorLabel("Function:{0}".format(str(function.__name__)))
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel("     Ouput(s):{0}".format(str(func_result)))
                return func_result
            except Exception as e:
                arcpy.AddMessage(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__),
                                                                                    str(args)))
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return func_wrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return arc_tool_report_decorator(function)

        return waiting_for_function
    else:
        return arc_tool_report_decorator(function)


@arc_tool_report
def arc_print(string, progressor_Bool=False):
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


@arc_tool_report
def field_exist(featureclass, fieldname):
    """ArcFunction
     Check if a field in a feature class field exists and return true it does, false if not.- David Wasserman"""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False


@arc_tool_report
def get_duplicates(items):
    """Return a list of duplicates items found in a provided list/sequence."""
    seen_items = set()
    seen_add = seen_items.add
    seen_twice = set(field for field in items if field in seen_items or seen_add(field))
    return list(seen_twice)

def generate_statistical_fieldmap(target_features, join_features,prepended_name="", merge_rule_dict={}):
    """Generates field map object based on passed field objects based on passed tables (list),
    input_field_objects (list), and passed statistics fields to choose for numeric and categorical variables. Output
    fields take the form of *merge rule*+*prepended_name*+*fieldname*"""
    field_mappings = arcpy.FieldMappings()
    # We want every field in 'target_features' and all fields in join_features that are present
    # in the field statistics mappping.
    field_mappings.addTable(target_features)
    for merge_rule in merge_rule_dict:
        for field in merge_rule_dict[merge_rule]:
            new_field_map=arcpy.FieldMap()
            new_field_map.addInputField(join_features,field)
            new_field_map.mergeRule = merge_rule
            out_field = new_field_map.outputField
            out_field.name = str(merge_rule) + str(prepended_name) + str(field)
            out_field.aliasName = str(merge_rule) + str(prepended_name) + str(field)
            new_field_map.outputField=out_field
            field_mappings.addFieldMap(new_field_map)
    return field_mappings

def statistical_spatial_join(target_feature, join_features, out_feature_class, prepended_field_name="",
                             join_operation="JOIN_ONE_TO_ONE", join_type=True, match_option="INTERSECT",
                             search_radius=None, merge_rule_dict={}):
    """This function will join features to a target feature class using merge fields that are chosen based on the
     chosen summary statistics fields from the join feature class while keeping all the fields in the target."""
    try:
        arcpy.env.overwriteOutput = True
        # Start Analysis
        arc_print("Generating fieldmapping...")
        f_map = generate_statistical_fieldmap(target_feature,join_features,prepended_field_name,merge_rule_dict)
        arc_print("Conducting spatial join...")
        arcpy.SpatialJoin_analysis(target_features=target_feature, join_features=join_features,
                                   out_feature_class=out_feature_class, join_operation=join_operation,
                                   join_type=join_type, match_option=match_option, search_radius=search_radius
                                   , field_mapping=f_map)
        arc_print("Script Completed Successfully.", True)
    except arcpy.ExecuteError:
        arc_print(arcpy.GetMessages(2))
    except Exception as e:
        arc_print(e.args[0])

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
                                       field_exist(join_feature_class, field)]
    statistical_spatial_join(target_feature_class, join_feature_class, output_feature_Class, prepended_field_name,
                             join_operation, join_type, match_option, search_radius, merge_rule_dict)
