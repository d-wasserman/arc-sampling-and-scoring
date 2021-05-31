# Name: PercentileScoreFields.py
# Purpose: Will add selected fields as percentile scores by extending a numpy array to the feature class.
# Author: David Wasserman
# Last Modified: 4/15/2021
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
import arcpy
import datetime
import numpy as np
import os
import pandas as pd
from scipy import stats

import SharedArcNumericalLib as san


# Function Definitions


def add_percentile_fields(in_fc, input_fields, percentile_method="average", ignore_nulls=True):
    """ This function will take in an feature class, and use pandas/numpy to calculate percentile scores and then
    join them back to the feature class using arcpy.
    Parameters
    -----------------
    in_fc- input feature class to add percentile fields
    input_fields - table fields to percentile score
    percentile_method - {‘average’, ‘min’, ‘max’, ‘dense’, ‘ordinal’}, optional
        The method used to assign percentile ranks to tied elements.
        The following methods are available (default is ‘average’):
        ‘average’: The average of the ranks that would have been assigned to all the tied values is assigned to each
        value.
        ‘min’: The minimum of the ranks that would have been assigned to all the tied values is assigned to each value.
         (This is also referred to as “competition” ranking.)
        ‘max’: The maximum of the ranks that would have been assigned to all the tied values is assigned to each value.
        ‘dense’: Like ‘min’, but the rank of the next highest element is assigned the rank immediately after those
        assigned to the tied elements.
        ‘ordinal’: All values are given a distinct rank, corresponding to the order that the values occur in a.
    ignore_nulls - ignore null values in percentile calculations
    """
    try:
        arcpy.env.overwriteOutput = True
        desc = arcpy.Describe(in_fc)
        OIDFieldName = desc.OIDFieldName
        workspace = os.path.dirname(desc.catalogPath)
        input_Fields_List = input_fields
        finalColumnList = []
        scored_df = None
        for column in input_Fields_List:
            try:
                field_series = san.arcgis_table_to_dataframe(in_fc, [column], skip_nulls=ignore_nulls)
                san.arc_print("Creating percentile column for field {0}.".format(str(column)), True)
                col_per_score = arcpy.ValidateFieldName("Perc_" + column, workspace)
                field_series[col_per_score] = stats.rankdata(field_series, percentile_method) / len(field_series)
                finalColumnList.append(col_per_score)
                if col_per_score != column:
                    del field_series[column]
                if scored_df is None:
                    scored_df = field_series
                else:
                    scored_df = pd.merge(scored_df, field_series, how="outer", left_index=True, right_index=True)
            except Exception as e:
                san.arc_print("Could not process field {0}".format(str(column)))
                san.arc_print(e.args[0])
                pass
        JoinField = arcpy.ValidateFieldName("DFIndexJoin", workspace)
        scored_df[JoinField] = scored_df.index
        finalColumnList.append(JoinField)
        san.arc_print("Exporting new percentile dataframe to structured numpy array.", True)
        finalStandardArray = scored_df.to_records()
        san.arc_print(
            "Joining new standarized fields to feature class. The new fields are {0}".format(str(finalColumnList))
            , True)
        arcpy.da.ExtendTable(in_fc, OIDFieldName, finalStandardArray, JoinField, append_only=False)
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
    InputFields = arcpy.GetParameterAsText(1).split(";")
    IgnoreNulls = bool(arcpy.GetParameter(2))
    add_percentile_fields(FeatureClass, InputFields, ignore_nulls=IgnoreNulls)
