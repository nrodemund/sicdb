# Introduction

data_float_h contains raw data, in a stream of floats. To unpack this data there are several possibilities.

## Use RooDataServer

Refer to our online documentation on how to install and configure RooDataServer https://www.sicdb.com/Documentation/Get_Started

Create a query with and add the field to export. Most aggregate fields have a "DetailConfiguration", which allows to export raw data.

Example for getting raw MAP of heart surgery patients:

- Create a Query, add the field HeartSurgeryDataAvailable, and set filter to "Yes"
- Add Signals->Generic Signals->SignalAvg, and configure the filter to "BloodPressureArterialMAP"
- You may set the offset to Between with values 0 and d2 to select the first 48 hours
- Press Export->CSV and check the "Export raw data" and "Export minute values"

## Use unpack.py

Put data_float_h into the same folder and run unpack.py with python.

The data is serialized for a good reason, expect this to run for a long time and create a massive csv file.