# Name: PercentileScoreFields.py
# Purpose: Will add selected fields as percentile scores by extending a numpy array to the feature class.
# Author: David Wasserman
# Last Modified: 4/15/2017
# Copyright: David Wasserman
# Python Version:   2.7-3.1
# ArcGIS Version: 10.4 (Pro)
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
import os, arcpy, datetime
import numpy as np
import pandas as pd
from scipy import stats
# Define Inputs
FeatureClass = arcpy.GetParameterAsText(0)
InputFields = arcpy.GetParameterAsText(1).split(";")
IgnoreNulls = bool(arcpy.GetParameter(2))



# Function Definitions
def funcReport(function=None,reportBool=False):
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
                print("{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])
        return funcWrapper
    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return funcReport_Decorator(function)
        return waiting_for_function
    else:
        return funcReport_Decorator(function)

def functionTime(function=None,reportTime=True):
    """ If a report time boolean is true, it will print the datetime before and after function run. Includes
    import with a rare namespace.-David Wasserman"""
    def funcReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            if reportTime:
                try:
                    #from datetime import datetime as functionDateTime_nsx978 #Optional, but removed
                    print("{0} Function Start:{1}".format(str(function.__name__),str(datetime.datetime.now())))
                except:
                    pass
            funcResult = function(*args, **kwargs)
            if reportTime:
                try:
                    print("{0} Function End:{1}".format(str(function.__name__),str(datetime.datetime.now())))
                except:
                    pass
            return funcResult
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
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print("{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])
        return funcWrapper
    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return  arcToolReport_Decorator(function)
        return waiting_for_function
    else:
        return arcToolReport_Decorator(function)

@arcToolReport
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


@arcToolReport
def ArcGISTabletoDataFrame(in_fc, input_Fields, query="", skip_nulls=False, null_values=None):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields."""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    final_Fields = [OIDFieldName] + input_Fields
    arc_print("Converting feature class table to numpy array.", True)
    npArray = arcpy.da.TableToNumPyArray(in_fc, final_Fields, query, skip_nulls, null_values)
    objectIDIndex = npArray[OIDFieldName]
    arc_print("Converting feature class numpy array into pandas dataframe.", True)
    fcDataFrame = pd.DataFrame(npArray, index=objectIDIndex, columns=input_Fields)
    return fcDataFrame



@functionTime(reportTime=False)
def add_Percentile_Fields(in_fc, input_fields, ignore_nulls):
    """ This function will take in an feature class, and use pandas/numpy to calculate percentile scores and then
    join them back to the feature class using arcpy."""
    try:
        arcpy.env.overwriteOutput = True
        desc = arcpy.Describe(in_fc)
        OIDFieldName=desc.OIDFieldName
        workspace= os.path.dirname(desc.catalogPath)
        input_Fields_List=input_fields
        fcDataFrame=ArcGISTabletoDataFrame(in_fc,input_Fields_List,skip_nulls=ignore_nulls)
        finalColumnList=[]
        for column in fcDataFrame:
            try:
                arc_print("Creating percentile column for field {0}.".format(str(column)), True)
                col_per_score = arcpy.ValidateFieldName("Perc_"+column,workspace)
                fcDataFrame[col_per_score] = stats.rankdata(fcDataFrame[column], "average")/len(fcDataFrame[column])
                finalColumnList.append(col_per_score)
                if col_per_score==column:
                    continue
                del fcDataFrame[column]
            except Exception as e:
                arc_print("Could not process field {0}".format(str(column)))
                print(e.args[0])
                pass
        JoinField=arcpy.ValidateFieldName("DFIndexJoin",workspace)
        fcDataFrame[JoinField]=fcDataFrame.index
        finalColumnList.append(JoinField)
        arc_print("Exporting new percentile dataframe to structured numpy array.", True)
        finalStandardArray= fcDataFrame.to_records()
        arcPrint("Joining new standarized fields to feature class. The new fields are {0}".format(str(finalColumnList))
                 , True)
        arcpy.da.ExtendTable(in_fc,OIDFieldName,finalStandardArray,JoinField,append_only=False)
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
    add_Percentile_Fields(FeatureClass, InputFields, IgnoreNulls)
