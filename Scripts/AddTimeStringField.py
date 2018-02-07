# Name: AddTimeStringField.py
# Purpose: Will take a selected datetime field and will try to add text field with a formatted date time.
# See http://strftime.org/ for details.
# Author: David Wasserman
# Last Modified: 2/7/2018
# Copyright: David Wasserman
# Python Version:   2.7-3.1
# ArcGIS Version: 10.4 (Pro)
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
import os, arcpy, datetime
import pandas as pd
import SharedArcNumericalLib as san


# Function Definitions

@san.functionTime(reportTime=False)
def add_Time_String_Field(in_fc, input_field, new_field_name, time_format):
    """ This function will take in an feature class, and use pandas/numpy to format a date string based on
    the input time format. """
    try:
        # arc_print(pd.__version__) Does not have dt lib.
        arcpy.env.overwriteOutput = True
        desc = arcpy.Describe(in_fc)
        workspace = os.path.dirname(desc.catalogPath)
        col_new_field = arcpy.ValidateFieldName(san.create_unique_field_name(new_field_name, in_fc), workspace)
        san.add_new_field(in_fc, col_new_field, "TEXT")
        OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
        san.arc_print("Creating Pandas Dataframe from input table.")
        query = "{0} {1} {2}".format(arcpy.AddFieldDelimiters(in_fc, input_field), "is NOT", "NULL")
        fcDataFrame = san.arcgis_table_to_dataframe(in_fc, [input_field, col_new_field], query)
        JoinField = arcpy.ValidateFieldName("DFIndexJoin", workspace)
        fcDataFrame[JoinField] = fcDataFrame.index
        try:
            san.arc_print("Creating new text column based on field {0}.".format(str(input_field)), True)
            fcDataFrame[col_new_field] = fcDataFrame[input_field].apply(lambda dt: dt.strftime(time_format))
            del fcDataFrame[input_field]
        except Exception as e:
            del fcDataFrame[input_field]
            san.arc_print(
                "Could not process datetime field. "
                "Check that datetime is a year appropriate to your python version and that "
                "the time format string is appropriate.")
            san.arc_print(e.args[0])
            pass

        san.arc_print("Exporting new time field dataframe to structured numpy array.", True)
        finalStandardArray = fcDataFrame.to_records()
        san.arc_print("Joining new time string field to feature class.", True)
        arcpy.da.ExtendTable(in_fc, OIDFieldName, finalStandardArray, JoinField, append_only=False)
        san.arc_print("Delete temporary intermediates.")
        del fcDataFrame, finalStandardArray
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
    # Define Inputs
    FeatureClass = arcpy.GetParameterAsText(0)
    InputField = arcpy.GetParameterAsText(1)
    NewTextFieldName = arcpy.GetParameterAsText(2)
    TimeFormat = arcpy.GetParameterAsText(3)
    add_Time_String_Field(FeatureClass, InputField, NewTextFieldName, TimeFormat)
