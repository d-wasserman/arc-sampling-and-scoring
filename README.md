# Distribution Summary
A set of ArcGIS tools that assist with sampling and scoring spatial data by enabling proportional allocations, density sampling, and different scoring methods. The documentation for each tool in the scripts folder and toolbox will be placed in the read me in the section below.

# arc-sample-and-score tbx

# Proportional Allocation Summary
This tool intended to provide a way to use sampling geography that will calculate proportional averages or sums based on the percentage of an intersection covered by the sampling geography. The output is  the sampling geography with fields sampled from the base features.
# Usage
The goal of this script is to enable analysis of demographic or other area based data based on arbitrary sampling polygons. 

![alt tag](https://github.com/Holisticnature/ArcNumerical-Tools/blob/main/Help/Assets/ProportionalAllocation@2x.png?raw=true)

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
<td class="info">Sampling_Features</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><div><p><span>The sampling features are the features you want to associate proportional averages or sums from the attributes in the base features. The output will look like this input polygon layer with new fields.</span></p></div></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
</p></div></div></div></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Base Features</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>The base features have the attributes being sampled by the polygon sampling features.
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
</p></div></div></td>
<td class="info" align="left">Multiple Value</td>
</tr>
 <tr>
<td class="info">Output Features</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>The output feature class is a copy of the sampling features with new sum & average field.
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
</p></div></div></td>
<td class="info" align="left">Multiple Value</td>
</tr>
 <tr>
<td class="info">Sum Fields</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>Fields to proportionally sum (based on the overlapping areas between the sampling and base features) from the base to the sampling features.
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
</p></div></div></td>
<td class="info" align="left">Multiple Value</td>
</tr>
<tr>
<td class="info">Mean Fields</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>Fields to proportionally average (based on the overlapping areas between the sampling and base features from the base to the sampling features.
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
</p></div></div></td>
<td class="info" align="left">Multiple Value</td>
</tr>
</tbody>
</table>

# Standarize Fields Summary
This ArcGIS scripting tool is designed to take selected fields and create an added field with a Z score for each one of the selected fields. 
# Usage
The goal of this script is to add new fields with standardized Z Scores for every field selected. The Z Scores are based on the values of each column, so they will change depending on the extent of the current data set.
![alt tag](https://github.com/Holisticnature/ArcNumerical-Tools/blob/main/Help/Assets/Test.jpg?raw=true)

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
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><div><p><span>This is the selected input feature class that will have new </span><a href="http://pro.arcgis.com/en/pro-app/tool-reference/spatial-statistics/what-is-a-z-score-what-is-a-p-value.htm"><span>fields with Z scores calculated </span></a><span>and joined to it. If the fields already exist, they will be updated by the tool. </span></p></div></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
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

# Percentile Fields Summary
This ArcGIS scripting tool is designed to take selected fields and create an added field with a percentile score for each one of the selected fields. 
# Usage
The goal of this script is to add new fields with percentile scores for every field selected. The percentile scores
are based on the values of each column, so they will change depending on the extent of the current data set. 

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
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><div><p><span>This is the selected input feature class that will have new fields with percentiles calculated and joined to it. If the fields already exist, they will be updated by the tool. </span></p></div></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<span style="font-weight: bold">Python Reference</span><br><div style="text-align:Left;"><div><div><p><span>The feature class uses the </span><a href="http://pro.arcgis.com/en/pro-app/arcpy/data-access/extendtable.htm"><span>ExtendTable function </span></a><span>used from the DA module of arcpy to join a modified structured numpy array with column-wise calculated Z scores joined to it. </span></p></div></div></div></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Percentile_Fields</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>These are the fields that percentiles scores added to the input feature class will be based. 
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<span style="font-weight: bold">Python Reference</span><br><div style="text-align:Left;"><div><p><span>Generally the fields are selected from the feature class to be converted into a numpy array, then into a pandas data frame, then back to structured numpy array to be joined based on the object ID. This tool assumes there is an object ID to use to join to from a table. These percentile scores are made of percent ranks using the pandas rank function. </span></p></div></div></td>
<td class="info" align="left">Multiple Value</td>
</tr>
<tr>
<td class="info">Other Parameters*</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>This tool has a host of other parameters including parameters to invert scores (change from high to low to low to high, etc.), change the method of ranking (average vs. max), designated values to fill null scores, and the choice of relative ranking field groups. These parameters are documented in the tool metadata. 
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<span style="font-weight: bold">Python Reference</span><br><div style="text-align:Left;"><div><p><span>Generally the fields are selected from the feature class to be converted into a numpy array, then into a pandas data frame, then back to structured numpy array to be joined based on the object ID. This tool assumes there is an object ID to use to join to. </span></p></div></div></td>
<td class="info" align="left">Multiple Value</td>
</tr>
</tbody>
</table>



# Create Class Field Summary
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
 <span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>The feature class uses the </SPAN><A href="http://pro.arcgis.com/en/pro-app/arcpy/data-access/extendtable.htm"><SPAN>ExtendTable function </SPAN></A><SPAN>used from the DA module of arcpy to join a modified structured numpy array with column-wise group IDs joined to it. </SPAN></P></DIV></DIV></DIV></td>
 <td class="info" align="left">Feature Layer</td>
 </tr>
 <tr>
 <td class="info">Fields_to_Group</td>
 <td class="info" align="left">
 <span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>These are the fields you want unique group categories of. It can be used to make a unique ID out of several different field attributes. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
 <span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Uses dynamic query creation to generate isolated numpy arrays to join to the input table. </SPAN></P></DIV></DIV></DIV></td>
 <td class="info" align="left">Multiple Value</td>
 </tr>
 <tr>
 <td class="info">Base_Name</td>
 <td class="info" align="left">
 <span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the string that is prepended to the the new field names. The field name will be this base name  along with either the strings "Num" or "String" appended to the end. </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
 <span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The fields will validated based on the work space. </SPAN></P></DIV></DIV></td>
 <td class="info" align="left">String</td>
 </tr>
 </tbody>
 </table>
 </div>


# Density To Vector Summary
This script is intended to help aid a density based network/vector analysis process by computing KDEs, associating
them with a target vector file, and computing percentile scores of non-zero/null density scores. This helps with
cartography and analysis on networks and other vector data. 

# Usage
The goal of this script is to assist in creating clean density maps using networks and to assist with planning prioritization processes by scoring those chosen densities according to multiple weights in a single step. This tool leverages memory workspaces only usable in ArcGIS Pro, and it will no longer operate in ArcMap.  

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
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><div><p><span>Feature class of point values that will be used to compute kernel densities. If the fields already exist, they will be updated by the tool. </span></p></div></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<td class="info" align="left">Feature Class</td>
</tr>
<tr>
<td class="info">Weight_Fields</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>Density feature class fields that are used to both
weight and filter kernel density estimates. Each kernel density is computed on non-null values, but a weight of 0 will still be treated as non-existent data. 
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<td class="info" align="left">Fields</td>
</tr>
<tr>
<td class="info">Input_Target_Vector</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>This is the target network/vector that the kernel
densities will be associated with. Zero values will be turned into nulls. 
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<td class="info" align="left">Feature Class</td>
</tr>
<tr>
<td class="info">Add_Percentiles (Optional)</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>If true, this will add a percentile calculation for every weight field. 
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<td class="info" align="left">Boolean</td>
</tr>
<tr>
<td class="info">Cell_Size,Search_Radius, and Unit Area Factor</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>These are the KDE control fields that the tool will use to compute the kernel densities of all the weighted elements in the input feature class. You can find out more information on the Kernel Density tools documentation. 
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<td class="info" align="left">Multiple Values</td>
</tr>
<tr>
<td class="info">Barrier Features</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br><div style="text-align:Left;"><div><p><span>The dataset that defines the barriers for KDE estimation (impacts shortest distances). The barriers can be a feature layer of polyline or polygon features. 
</span></p></div></div><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br>
<td class="info" align="left">Multiple Values</td>
</tr>
</tbody>
</table>
 
