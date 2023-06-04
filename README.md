Welcome to SICdb, a dataset and database environment with data collected from over 27,000 intensive care admissions.

The documentation about SICdb is found under https://www.sicdb.com/Documentation


# Quick Database start: 

We provide a software solution, which helps you build up an indexed database, view and select the data you need and export into various file formats, including csv, xlsx and sqlite3.

1) Download this repository
2) Download all files from physionet to folder Data  (So cases.csv.gz is in the same folder like docker-compose.yml)
3) Install software "docker" (www.docker.com)
4) Use commandline to navigate in the data folder folder, then run "docker compose up"
5) On Windows (Docker Desktop) the container is now listed at "containers", it is called "roodataenv".
6) After running, open http://localhost:5075" in browser

Please note: On Windows, using docker desktop, it is recommended to use the docker desktop application to start RooDataEnv again. 

If have any difficulties at step 4 there is a full explanation on https://www.sicdb.com/Documentation/QuickStart