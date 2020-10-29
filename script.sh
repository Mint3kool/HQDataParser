#!/bin/bash

# This script is designed to calculate the average, min, and max timestamps
# This script also calculates the 90th percentile average time
#   We define the 90th percentile average by
#   - sorting data by time taken
#   - removing the top 10% of slowest logs
#   - recomputing the average with the remaining data
#
# Usage
# file_name: the file containing the logs
# start_timestamp: the earliest timestamp you want to start from
# end_timestamp: the latest timestamp you want to include
#
# Example commands
# ./script.sh <file_name> <start_timestamp> <end_timestamp>
# ./script.sh <file_name> "2020-10-19 14:41:19.000" "2020-10-19 14:41:20.827"

input_file=$1
start_date=$2
end_date=$3

function drop() {
  local prev=$1
  local ms_time=$2

  if ((prev - ms_time > 30000)); then
    drop=$(echo "$line" | grep -oP "id=[^,]*")
    echo $drop
  fi
}

function percentile_index_calculator() {
  local percentile_value=$1
  local count=$2

  local percentile_index=$(echo "scale=3;($percentile_value/100)*$count" | bc )
  local percentile_index_rounded=$(echo "$percentile_index" | awk '{print ($0-int($0)<0.499)?int($0):int($0)+1}')
  echo $percentile_index_rounded
}

if [[ -z ${input_file} ]];
  then 
    echo "no input file"
    exit
  else
    echo "input file is: $input_file"
fi

if [[ -z ${start_date} ]];
  then 
    echo "no start date, defaulting to start of file"
    start_date="1111-01-01 1:01:01.001"
  else
    echo "start date is: $start_date"
fi

if [[ -z ${end_date} ]];
  then 
    echo "no end date, defaulting to end of file"
    end_date="9999-12-31 23:59:59.999"
  else 
    echo "end date is: $end_date"
fi

echo "-----------------------------------------------"
echo "#Debug prints here"

min_time=9223372036854775807
max_time=0
count=0
sum=0
prev=0
produce_times=()
ms_times=()
max_id=""
percentile_value=90

echo "#Reading file"

while IFS= read -r line
do
  #converting input string to an array 'arr' delimited by whitespace
  read -ra arr <<<"$line"

  #getting the produce and consume timestamps
  consume_ts="${arr[0]} ${arr[1]}"
  end_raw="${arr[10]} ${arr[11]}"
  no_end="${end_raw%?}"           #Removing trailing )
  produce_ts="${no_end:3}"    #Removing "ts=" prefix

  if [[ $consume_ts > $start_date && $consume_ts < $end_date || $consume_ts == "$start_date" || $consume_ts == "$end_date" ]];
  then
    consume_ms=$(($(date -d "$consume_ts" +%s%N)/1000000))
    produce_ms=$(($(date -d "$produce_ts" +%s%N)/1000000))
    ((ms_time=consume_ms - produce_ms))

    drop $prev $ms_time

    prev=$ms_time

    ms_times+=("$ms_time")
    produce_times+=("$produce_ms")

    ((count=count + 1))
    ((sum=sum + ms_time))

    if ((ms_time < min_time)); then
      min_time=$ms_time
    fi

    if ((ms_time > max_time)); then
      max_time=$ms_time
      max_id=$(echo "$line" | grep -oP "id=[^,]*")
    fi
  fi
done < "$input_file"

IFS=$'\n' ms_times_sorted=($(sort <<<"${ms_times[*]}")); unset IFS
IFS=$'\n' produce_times_sorted=($(sort <<<"${produce_times[*]}")); unset IFS

echo "#Calculating Percentile Values"

percentile_index=$(percentile_index_calculator $percentile_value $count)

percentile_sum=0
for (( time=0; time<=$percentile_index - 1; time++ )) 
do
  ((percentile_sum=percentile_sum + ms_times_sorted[time]))
done

produce_time_diff=()
for (( index=1; index<=${#produce_times_sorted[@]}-1; index++)) 
do
  ((diff=produce_times_sorted[index] - produce_times_sorted[index-1]))
  diff_seconds=$(echo "scale=5;$diff/1000000000" | bc )
  produce_time_diff+=("$diff_seconds")
done

echo ${ms_times[@]} > ms_times.txt
echo ${produce_time_diff[@]} > produce_time_diff.txt

echo "-----------------------------------------------"

echo "Results:"
echo "Records Processed: $count"

avg_time_secs="$(echo "scale=6;($sum/$count)/1000" | bc -q)"
min_time_secs="$(echo "scale=6;$min_time/1000" | bc -q)"
max_time_secs="$(echo "scale=6;$max_time/1000" | bc -q)"
percentile_average="$(echo "scale=6;($percentile_sum/$percentile_index)/1000" | bc -q)"

echo "Average time: $avg_time_secs"
echo "Minimum time: $min_time_secs"
echo "Maximum time: $max_time_secs"
echo "Maximum time id: $max_id"
echo "${percentile_value%.*}th percentile time: $percentile_average"

