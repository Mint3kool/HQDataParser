import sys
import operator
import numpy as np
import time
import os
from datetime import datetime

from functions import RowProcessor

def main():
    inputpath=None
    start_time="1000-01-01 1:01:01.001"
    end_time="9999-12-31 23:59:59.999"
    system_start_time = time.time()

    try:
        inputpath = sys.argv[1]
        print("Input file: " + inputpath)
    except:
        print ("No valid input path, exiting.")
        quit()

    try:
        start_time = sys.argv[2]
        print("Start Timestamp: " + start_time)
    except:
        print ("No start time, defaulting to start of file")

    try:
        end_time = sys.argv[3]
        print("End Timestamp: " + end_time)
    except:
        print ("No end time, defaulting to end of file")

    rp = RowProcessor()
    rp.start_timestamp = start_time
    rp.end_timestamp = end_time

    results = None
    with open(inputpath, 'r') as logfile:
        results = rp.split_csv(logfile)

    if results.size == 0:
        print("No records found within the expected timeframe")
        system_end_time = time.time()
        system_time_diff = system_end_time - system_start_time
        print("Total Processing Time: " + str(system_time_diff))
        quit()

    for r in results:
        r[3] = rp.time_diff(r[1], r[0])

    average_time = results[:, 3].mean()
    min_time = results[:, 3].min()
    max_index, max_time = max(enumerate(results[:, 3]), key=operator.itemgetter(1))
    num_under_sec = np.count_nonzero(results[:,3] < 1)
    inputfile = os.path.basename(inputpath)
    input_trimmed = os.path.splitext(inputfile)[0] + '.csv'
    output_path = "results/result_" + input_trimmed
    np.savetxt(output_path, results, fmt='%s, %s, %s, %.6s')
    sorted_diff_time = results[results[:, 3].argsort()]
    result_shape = sorted_diff_time.shape
    records_processed = result_shape[0]
    percent_under_min = (num_under_sec/records_processed) * 100

    time_percentile = 90
    index = round(result_shape[0] * time_percentile/100)
    average_time_percent = sorted_diff_time[:index, 3].mean()

    print("Results")
    print("--------------------------------------")
    print("Records Processed: " + str(records_processed))
    system_end_time = time.time()
    system_time_diff = system_end_time - system_start_time
    print("Total Processing Time: " + str(system_time_diff))
    print("Average Time: " + str(average_time))
    print("% Records <1s: " + str(round(percent_under_min, 2)) + "%")
    print("Minimum Time: " + str(min_time))
    print("Maximum Time: " + str(max_time))
    print("Maximum Time Index: " + results[max_index][2]) 
    print(str(time_percentile) + "th percentile time: " + str(average_time_percent))
    print()
    print("Results are saved in: " + output_path)

if __name__ == "__main__":
    main();
