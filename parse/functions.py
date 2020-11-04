import csv
import sys
import constants
import re
import numpy as np
from datetime import datetime

class RowProcessor(object):
    @property
    def start_timestamp(self):
        return self.__start_timestamp

    @start_timestamp.setter
    def start_timestamp(self, inputtime="1111-01-01 1:01:01.001"):
        self.__start_timestamp = datetime.strptime(inputtime, "%Y-%m-%d %H:%M:%S.%f")

    @property
    def end_timestamp(self):
        return self.__end_timestamp

    @end_timestamp.setter
    def end_timestamp(self, inputtime="9999-12-31 23:59:59.999"):
        self.__end_timestamp = datetime.strptime(inputtime, "%Y-%m-%d %H:%M:%S.%f")

    def time_diff(self, early, late):
        earlyTime = datetime.strptime(early.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], "%Y-%m-%d %H:%M:%S.%f")
        lateTime = datetime.strptime(late.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], "%Y-%m-%d %H:%M:%S.%f")

        print(earlyTime)#.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        print(lateTime)#.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        dateTimeDelta = lateTime - earlyTime
        seconds = dateTimeDelta.seconds;
        microseconds = dateTimeDelta.microseconds;
        return seconds + microseconds/1000000

    def split_input_line(self, inputString):
        requestData = re.findall(r'(?<=RequestData).*', inputString)
        no_par = requestData[0][requestData[0].find("(")+1:requestData[0].find(")")]
        raw_produce_ts = re.findall(r'(?<=ts=).*', no_par)
        raw_id = no_par.split(",")[:1]
        input_id = re.findall(r'(?<=id=).*',raw_id[0])[0]
        produce_ts = raw_produce_ts[0].replace("T", " ")
        first_two = inputString.split(" ")[:2]
        consume_ts = ' '.join(first_two)

        return [consume_ts, produce_ts, input_id, None]

    def get_timestamps(self, inputString):
        timestamps = self.split_input_line(inputString)
        consume_time = datetime.strptime(timestamps[0], "%Y-%m-%d %H:%M:%S.%f")
        if (consume_time >=self.start_timestamp and consume_time <= self.end_timestamp):
            return timestamps
        else:
            return None

    def split_csv(self, logfile):
        resultList = []
        result = np.empty((0, 4))
        lines = logfile.readlines()
        for line in lines:
            timestamps = self.get_timestamps(line)
            if timestamps != None:
                resultList.append(timestamps)
        result = np.array([i for i in resultList])
        return result
