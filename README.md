# Description
This script is used for finding differences in timestamps after logs have moved through a target system.

## Running the Script
1. From the top level directory, run
```
python parse/main.py results/<inputfile> <start_ts> <end_ts>
```
2. Example input
```
python parse/main.py combined_output.txt "2020-10-03 14:59:00.000" "2020-11-03 14:59:00.000"
```
## Running the tests
1. Navigate to top level directory
2. Run
```
python -m unittest discover
```
