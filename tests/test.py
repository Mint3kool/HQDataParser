import unittest

from parse.functions import *

class FunctionTests(unittest.TestCase):
    def setUp(self):
        self.rp = RowProcessor()

    def test_time_diff(self):
        base_time = "2020-10-19 13:00:00.000"
        no_diff = self.rp.time_diff(base_time, base_time);
        self.assertEqual(0, no_diff)

        new_time = "2020-10-19 13:00:01.123"
        diff = self.rp.time_diff(base_time, new_time);
        self.assertEqual(1.123, diff);

    def test_extract_split_input_line_new(self):
        input1 = "2020-11-02 09:55:03.385 [XFL] [Camel (camel-1) thread #83 - JmsConsumer[pubsub.in::electrique.in]] DEBUG d.perf - RequestData(id=2bea495a-f5d2-4a9a-a768-ababc2be2ef7, message=Message 2, ts=2020-11-02T09:55:03.353187)"
        expected_result = ["2020-11-02 09:55:03.385", "2020-11-02 09:55:03.353187", "2bea495a-f5d2-4a9a-a768-ababc2be2ef7", None]
        result = self.rp.split_input_line(input1)
        self.assertListEqual(result, expected_result)

    #@unittest.skip("demonstrating skipping")
    def test_extract_split_input_line_old(self):
        input2 = "2020-10-19 14:41:19.928 [XFL] [https-jsse-nio-8443-exec-4] DEBUG d.perf - RequestData(id=6393b292-1bae-4aff-b77c-2394ed27c89b, message=Message 1, ts=2020-10-19T14:41:19.719807)"
        expected_result = ["2020-10-19 14:41:19.928","2020-10-19 14:41:19.719807", "6393b292-1bae-4aff-b77c-2394ed27c89b", None]
        result = self.rp.split_input_line(input2)
        self.assertListEqual(result, expected_result)

    def test_get_timestamps_valid(self):
        inputString = "2020-10-19 14:41:19.928 [XFL] [https-jsse-nio-8443-exec-4] DEBUG d.perf - RequestData(id=6393b292-1bae-aff-b77c-2394ed27c89b, message=Message 1, ts=2020-10-19T14:41:19.719807)"

        early_time = "2020-10-19 13:41:19.928"
        same_time = "2020-10-19 14:41:19.928"
        late_time = "2020-10-19 15:41:19.928"

        expected_result = ["2020-10-19 14:41:19.928", "2020-10-19 14:41:19.719807", "6393b292-1bae-aff-b77c-2394ed27c89b", None]
        self.rp.start_timestamp = early_time
        self.rp.end_timestamp = same_time
        result_early = self.rp.get_timestamps(inputString)
        self.assertListEqual(expected_result, result_early)

        self.rp.end_timestamp = late_time
        result_whole = self.rp.get_timestamps(inputString)
        self.assertListEqual(expected_result, result_whole)

        self.rp.start_timestamp = same_time
        result_late = self.rp.get_timestamps(inputString)
        self.assertListEqual(expected_result, result_late)
        
        self.rp.end_timestamp = same_time
        result_same = self.rp.get_timestamps(inputString)
        self.assertListEqual(expected_result, result_same)

    def test_get_timestamps_invalid(self):
        inputString = "2020-10-19 14:41:19.928 [XFL] [https-jsse-nio-8443-exec-4] DEBUG d.perf - RequestData(id=6393b292-1bae-aff-b77c-2394ed27c89b, message=Message 1, ts=2020-10-19T14:41:19.719807)"

        early_time1 = "2020-10-19 13:41:19.928"
        early_time2 = "2020-10-19 14:40:19.928"
        late_time1 = "2020-10-19 14:42:19.928"
        late_time2 = "2020-10-19 15:41:19.928"

        expected_result = None
        self.rp.start_timestamp = early_time1
        self.rp.end_timestamp = early_time2
        result_early = self.rp.get_timestamps(inputString)
        self.assertEqual(None, result_early)

        self.rp.start_timestamp = late_time1
        self.rp.end_timestamp = late_time2
        result_late = self.rp.get_timestamps(inputString)
        self.assertEqual(None, result_late)

