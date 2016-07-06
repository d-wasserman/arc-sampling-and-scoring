# Distribution Summary
A set of ArcGIS tools that use Numpy and Pandas to help with different data analysis tasks such as standarizing data and creating group IDs. The documentation for each tool in the scripts folder and toolbox will be placed in the read me in the section below. 
# ArcNumerical TBX
# StandarizeFields Summary
This 10.4 ArcGIS scripting tool is designed to take selected fields and create an added field with a Z score for each one of the selected fields. 
# Usage
The goal of this script is to add new fields with standarized Z Scores for every field selected. The Z Scores are based on the values of each column, so they will change depending on the extent of the current data set.
![alt tag](https://github.com/Holisticnature/ArcNumerical-Tools/blob/master/Help/Test.jpg?raw=true)

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

# TruncateDatetime
This tool is a simple geoprocessing scripting tool intended to assist with temporal data preparation by truncating the date time object to set constants for better grouping and aggregation for time space cubes and other analysis methods. If the set times are -1, the current date and time will be used for that parameter.  

# Usage
Use this script with an input date field to create a formated time string based on your needs. 

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
# ArcTime TBX
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
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Is the input feature class or table for which a new time field will be added. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Depends on https://docs.python.org/2/library/time.html#time.strftime. </SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Date_Time_Field</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the ArcGIS date field that will be used to construct the datetime objects used in the created Pandas data frame. Years allowed by the tool will dependon python version. For example 2.7 cannot handle years before 1900. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Generally the fields are selected from the feature class to be converted into a numpy array, then into a pandas data frame, then back to structured numpy array to be joined based on the object ID. This tool assumes there is an object ID to use to join to.</SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Field</td>
</tr>
<tr>
<td class="info">New_Field_Name</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the name of the new text field that will be added to the feature class and then populated by a new time string based on the format string. If the name already exists, then a unique one will be added. </SPAN></P></DIV></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">String</td>
</tr>
<tr>
<td class="info">Set_Year</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the year you want to set all the datetimes to for the new field. If it is -1, it will use the current timeperiod determined by the datetime object. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Set_Month</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the month you want to set all the datetimes to for the new field. If it is -1, it will use the current timeperiod determined by the datetime object. </SPAN></P></DIV><DIV><P><SPAN /></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Set_Day</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the day you want to set all the datetimes to for the new field. If it is -1, it will use the current timeperiod determined by the datetime object. </SPAN></P></DIV><DIV><P><SPAN /></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Set_Hour</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the hour you want to set all the datetimes to for the new field. If it is -1, it will use the current timeperiod determined by the datetime object. </SPAN></P></DIV><DIV><P><SPAN /></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Set_Minute</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the minute you want to set all the datetimes to for the new field. If it is -1, it will use the current timeperiod determined by the datetime object. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Set_Second</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the second you want to set all the datetimes to for the new field. If it is -1, it will use the current timeperiod determined by the datetime object. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
</tbody>
</table>

# AddTimeStringField

This tool is a simple strf time script intended to add a new text field with a formatted string based on the format string input into it. This tool uses pandas to convert and add the new unique field using the arcpy.da extend table function.

# Usage
This tool is intended to provide an easy way to created formatted string fields using the </SPAN><A href="https://docs.python.org/2/library/time.html"><SPAN>strftime function</SPAN></A><SPAN>. 

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
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Is the input feature class or table for which a new time field will be added. </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Depends on https://docs.python.org/2/library/time.html#time.strftime. </SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Date_Time_Field</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the ArcGIS date field that will be used to construct the datetime objects used in the created Pandas data frame. </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Generally the fields are selected from the feature class to be converted into a numpy array, then into a pandas data frame, then back to structured numpy array to be joined based on the object ID. This tool assumes there is an object ID to use to join to.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Field</td>
</tr>
<tr>
<td class="info">New_Field_Name</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the name of the new text field that will be added to the feature class and then populated by a new time string based on the format string. If the name already exists, then a unique one will be added. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">String</td>
</tr>
<tr>
<td class="info">Format_String</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>The format string determines the output time format. Do not add quotes. </SPAN></P><P><SPAN>Check the documentation </SPAN><A href="https://docs.python.org/2/libarary/time.html"><SPAN>link here for details</SPAN></A><SPAN>. </SPAN></P><P><SPAN>Directive	Meaning	Notes</SPAN></P><P><SPAN>%a	Localeӳ abbreviated weekday name.	 </SPAN></P><P><SPAN>%A	Localeӳ full weekday name.	 </SPAN></P><P><SPAN>%b	Localeӳ abbreviated month name.	 </SPAN></P><P><SPAN>%B	Localeӳ full month name.	 </SPAN></P><P><SPAN>%c	Localeӳ appropriate date and time representation.	 </SPAN></P><P><SPAN>%d	Day of the month as a decimal number [01,31].	 </SPAN></P><P><SPAN>%H	Hour (24-hour clock) as a decimal number [00,23].	 </SPAN></P><P><SPAN>%I	Hour (12-hour clock) as a decimal number [01,12].	 </SPAN></P><P><SPAN>%j	Day of the year as a decimal number [001,366].	 </SPAN></P><P><SPAN>%m	Month as a decimal number [01,12].	 </SPAN></P><P><SPAN>%M	Minute as a decimal number [00,59].	 </SPAN></P><P><SPAN>%p	Localeӳ equivalent of either AM or PM.	(1)</SPAN></P><P><SPAN>%S	Second as a decimal number [00,61].	(2)</SPAN></P><P><SPAN>%U	Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0.	(3)</SPAN></P><P><SPAN>%w	Weekday as a decimal number [0(Sunday),6].	 </SPAN></P><P><SPAN>%W	Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0.	(3)</SPAN></P><P><SPAN>%x	Localeӳ appropriate date representation.	 </SPAN></P><P><SPAN>%X	Localeӳ appropriate time representation.	 </SPAN></P><P><SPAN>%y	Year without century as a decimal number [00,99].	 </SPAN></P><P><SPAN>%Y	Year with century as a decimal number.	 </SPAN></P><P><SPAN>%Z	Time zone name (no characters if no time zone exists).	 </SPAN></P><P><SPAN>%%	A literal '%' character.	 </SPAN></P><P><SPAN>Notes:</SPAN></P><P><SPAN /></P><P><SPAN>When used with the strptime() function, the %p directive only affects the output hour field if the %I directive is used to parse the hour.</SPAN></P><P><SPAN>The range really is 0 to 61; this accounts for leap seconds and the (very rare) double leap seconds.</SPAN></P><P><SPAN>When used with the strptime() function, %U and %W are only used in calculations when the day of the week and the year are specified.</SPAN></P><P><SPAN>Taken from: http://strftime.org/</SPAN></P></DIV></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">String</td>
</tr>
</tbody>
</table>