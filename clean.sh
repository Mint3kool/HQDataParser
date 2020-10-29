#!/bin/bash

# This script is used for cleaning the input file. 
# We need timestamps to be in the format "yyyy-mm-dd hh:mm:ss.zz..." for the script to work

input_file=$1

if [[ -z ${input_file} ]];
  then 
    echo "no input file"
    exit
  else
    echo "input file is: $input_file"
fi

while IFS= read -r line
do
  clean_line="${line/T/ }"
  echo "$clean_line" >> "clean_$input_file"
done < "$input_file"
