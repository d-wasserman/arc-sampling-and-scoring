#ArcNumerical Tools
These tools are a collection of ArcGIS scripting tools that use numpy and pandas to help with various data and spatial analysis tasks in ArcGIS. 
The current tools included are:
1. Standardize Fields- will calculate Z Scores for any selected field. 
2. Group Field - will create a group id based on the unique values in selected fields. 
# StandarizeFields Summary
This 10.4 ArcGIS scripting tool is designed to take selected fields and create an added field with a Z score for each one of the selected fields. 
# Usage
The goal of this script is to add new fields with standarized Z Scores for every field selected. The Z Scores are based on the values of each column, so they will change depending on the extent of the current data set.
![alt tag](https://github.com/Holisticnature/StandarizeFields/blob/master/Help/Test.jpg?raw=true)
#Parameters
<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input_Feature_Class</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><div><p><span>This is the selected input feature class that will have new </span><a href="http://pro.arcgis.com/en/pro-app/tool-reference/spatial-statistics/what-is-a-z-score-what-is-a-p-value.htm"><span>fields with Z scores calculated </span></a><span>joined to it. If the fields already exist, they will be updated by the tool. </span></p></div></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<span style="font-weight: bold">Python Reference</span><br><div style="text-align:Left;"><div><div><p><span>The feature class uses the </span><a href="http://pro.arcgis.com/en/pro-app/arcpy/data-access/extendtable.htm"><span>ExtendTable function </span></a><span>used from the DA module of arcpy to join a modified structured numpy array with column-wise calculated Z scores joined to it. </span></p></div></div></div></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Fields_to_Standarize</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>These are the fields that will have their Z scores calculated within a </span><a href="http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html"><span>Pandas data frames</span></a><span>, converted to a structured numpy array, and then joined to the input feature class based on the object ID. The fields added will be in the form of "Zscore_"+%FieldName%. If a field of that form already exists in the table, it will be updated.</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<span style="font-weight: bold">Python Reference</span><br><div style="text-align:Left;"><div><p><span>Generally the fields are selected from the feature class to be converted into a numpy array, then into a pandas data frame, then back to structured numpy array to be joined based on the object ID. This tool assumes there is an object ID to use to join to. </span></p></div></div></td>
<td class="info" align="left">Multiple Value</td>
</tr>
</tbody>
</table>
# CreateClassField Summary
This scripting tool is designed to take selected fields and create an added field that classifies based on their unique combinations of values using numpy.
# Usage
The goal of this script is to add a group field based on a selection of fields chosen in the tool. Two fields will be added, one with a number representing the group ID (can be dissolved or summarized on), and another with a string with the query used to isolate it. The names of the fields are based on the base name parameter. 
# Parameters
<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input_Feature_Class</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the selected input feature class that will have new group fields joined to it. If the fields already exist, they will be updated by the tool. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>The feature class uses the </SPAN><A href="http://pro.arcgis.com/en/pro-app/arcpy/data-access/extendtable.htm"><SPAN>ExtendTable function </SPAN></A><SPAN>used from the DA module of arcpy to join a modifed structured numpy array with column-wise group IDs joined to it. </SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Fields_to_Group</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>These are the fields you want unique group categories of. It can be used to make a unique ID out of serveral different field attributes. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Uses dynamic query creation to generate isolated numpy arrays to join to the input table. </SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Multiple Value</td>
</tr>
<tr>
<td class="info">Base_Name</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the string that is prepended to the the new field names. The field name will be this basename  along with either the strings "Num" or "String" appended to the end. </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The fields will validated based on the work space. </SPAN></P></DIV></DIV></td>
<td class="info" align="left">String</td>
</tr>
</tbody>
</table>
</div>
