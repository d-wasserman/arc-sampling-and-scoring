# Name: MinMaxScalingFields.py
# Purpose: Adds selected fields after applying min-max scaling by extending a numpy array to the feature class.
# Author: David Wasserman
# Last Modified: 10/13/2023
# Python Version: 3.X
# ArcGIS Version: 10.4 (Pro)
# --------------------------------
# Import Modules
import arcpy
import numpy as np
import os
import pandas as pd

# Function Definitions
def add_min_max_scaled_fields(in_fc, input_fields, min_percentile=None, max_percentile=None, target_min=1, target_max=10):
    """
    This function takes an input feature class and fields, performs min-max scaling on the fields,
    and adds them back to the feature class. The percentile options can be used to adjust what is considered the minimum
    or maximum based on a percentile scoring. 
    Parameters
    ----------
    in_fc: str
        Input feature class.
    input_fields: list
        List of fields to be scaled.
    min_percentile: float, optional
        Minimum percentile for scaling.
    max_percentile: float, optional
        Maximum percentile for scaling.
    target_min: float
        Minimum value of the target range for scaling.
    target_max: float
        Maximum value of the target range for scaling.
    """
    try:
        arcpy.env.overwriteOutput = True
        desc = arcpy.Describe(in_fc)
        OIDFieldName = desc.OIDFieldName
        workspace = os.path.dirname(desc.catalogPath)

        df = pd.DataFrame(arcpy.da.TableToNumPyArray(in_fc, input_fields))

        for field in input_fields:
            min_val = np.percentile(df[field], min_percentile) if min_percentile is not None else df[field].min()
            max_val = np.percentile(df[field], max_percentile) if max_percentile is not None else df[field].max()
            df[f"{field}_SCALED"] = target_min + (df[field] - min_val) * (target_max - target_min) / (max_val - min_val)
            df[f"{field}_SCALED"] = df[f"{field}_SCALED"].clip(target_min,target_max)

        df.drop(columns=input_fields, inplace=True)
        join_field = arcpy.ValidateFieldName("DFIndexJoin", workspace)
        df[join_field] = df.index

        final_scaled_array = df.to_records()

        arcpy.da.ExtendTable(in_fc, OIDFieldName, final_scaled_array, join_field, append_only=False)
        arcpy.AddMessage("Script completed successfully.")

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
    except Exception as e:
        arcpy.AddError(str(e))

# Main function
if __name__ == '__main__':
    FeatureClass = arcpy.GetParameterAsText(0)
    InputFields = arcpy.GetParameterAsText(1).split(";")
    MinPercentile = float(arcpy.GetParameterAsText(2)) if arcpy.GetParameterAsText(2) != "#" else None
    MaxPercentile = float(arcpy.GetParameterAsText(3)) if arcpy.GetParameterAsText(3) != "#" else None
    TargetMin = float(arcpy.GetParameterAsText(4)) if arcpy.GetParameterAsText(4) != "#" else 1
    TargetMax = float(arcpy.GetParameterAsText(5)) if arcpy.GetParameterAsText(5) != "#" else 5
    add_min_max_scaled_fields(FeatureClass, InputFields, MinPercentile, MaxPercentile, TargetMin, TargetMax)
