Welcome to SICdb, a dataset and database environment with data collected from over 27,000 intensive care admissions.

The documentation about SICdb is found under https://www.sicdb.com/Documentation


# Quick raw data start:

The files are gzip compressed RFC4180 csv files.

All tables have encoded fields, an integer between 1 and 10000. These fields all relate to d_references.ReferenceGlobalID, where d_references.ReferenceValue is the value of this field.

Refer to Documentation.pdf for more information.


# Quick Database start: 

We provide a software solution, which helps you build up an indexed database, view and select the data you need and export into various file formats, including csv, xlsx and sqlite3.

1) Download https://github.com/nrodemund/sicdb/tree/main/Data 
2) Download all files from physionet and put all files together in the same directory like docker-compose.yml. (So cases.csv.gz is in the same folder like docker-compose.yml)
3) Install software "docker" (www.docker.com)
4) Use commandline to navigate in this folder, then run "docker compose up"
5) On Windows (Docker Desktop) the container is now listed at "containers", it is called "roodataenv".
6) After running, open http://localhost:5000" in browser

Please note: On Windows, using docker desktop, it is recommended to use the docker desktop application to start RooDataEnv again. 

If have any difficulties at step 4 there is a full explanation on https://www.sicdb.com/Documentation/QuickStart