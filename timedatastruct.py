#!/usr/bin/python

#timedatastruct.py
from threading import RLock
import threading
import numpy as np
import datetime as dt
import time
import bisect
import spectrum_gen as sgen
import matplotlib.pyplot as plt

class TimeData(object):
    """General class for dealing with time data in a thread-safe way"""
    def __init__(self):
        self.data_object_list = []
        self.time_list = []
        self.run_information = None
        self.mutex = RLock()
        pass

    def add_data_object(self, data_object):
        with self.mutex:
            if len(self.data_object_list) == 0:
                self.data_object_list.append(data_object)
                self.time_list.append(data_object.get_time())
            else:
                #find where to insert data using the time_list
                ins_point = bisect.bisect_left(self.time_list, data_object.get_time())
                self.data_object_list.insert(ins_point, data_object)
                self.time_list.insert(ins_point, data_object.get_time())
        return

    def get_current_data(self):
        with self.mutex:
            return self.data_object_list[-1].get_data()

    def get_current_time(self):
        with self.mutex:
            return self.data_object_list[-1].get_time()

    def get_current_run_info(self):
        with self.mutex:
            return self.data_object_list[-1].get_run_info()

    def get_time_delta(self):
        with self.mutex:
            time_delta = self.data_object_list[-1].get_time() \
                - self.data_object_list[0].get_time()
        return time_delta

    def retrieve_data_interval(self, start, end):
        """Method to retrieve an interval of data, returns the spliced list"""
        start_ins_point = bisect.bisect_left(self.time_list, start)
        end_ins_point = bisect.bisect_left(self.time_list, end)
        return self.data_object_list[start_ins_point:end_ins_point]

    def create_interval_avg(self, indexed_list):
        """This method is specific to certain types of data"""
        running_avg = []
        for index, element in enumerate(indexed_list):
            data_array = element.get_data()
            rms = np.sum(data_array)
            #Do other stuff here
            
class HoloData(object):

    def __init__(self, timedelta):
        self.now = dt.datetime.now()
        self.timedelta = timedelta
        self.tuple_list = [(0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0), (3,1), \
                               (3,2), (3,3)]
        self.data_dict = {}
        self.gen_data()
        self.run_information = dict([('window_function', 'Hanning'), \
                                         ('ADC_settings', dict([('f_samp', 1e6), \
                                                                ('gain', 10)])), \
                                         ('channel_info', dict([('1', 'test'), \
                                                                    ('2', 'blah')])), \
                                         ('yunits', 'V^2/root(Hz)')])

    def gen_data(self):
        for i in range(len(self.tuple_list)):
            if self.tuple_list[i][0] == self.tuple_list[i][1]:
                self.data_dict[self.tuple_list[i]] = sgen.gen_spec(1)
            else:
                if self.timedelta < 1:
                    self.data_dict[self.tuple_list[i]] = sgen.gen_spec(1)
                else:
                    self.data_dict[self.tuple_list[i]] = sgen.gen_spec(self.timedelta)

    def get_time(self):
        return self.now

    def get_data(self):
        return self.data_dict

    def get_run_info(self):
        return self.run_information

class StreamDataTest(object):
    
    def __init__(self, window, report_data_method):
        self.keep_going = True
        self.time_start = time.time()
        self.window = window
        self.report_data = report_data_method
        self.fake_time = 100

    def _run_stream(self):
        while self.keep_going:
            now = time.time()
            delta = now - self.time_start
            data = HoloData(10*delta**2)
            self.report_data(data)
            self.fake_time += 100
            time.sleep(.5)

    def run_stream_in_background(self):
        thread = threading.Thread(target=self._run_stream)
        thread.start()
            
class ExampleData(object):

    def __init__(self):
        self.time = time.time()
        self.gen_data()

    def gen_data(self):
        num_points = 2**20
        self.data = np.random.normal(0, 1, num_points)

    def get_time(self):
        return self.time

    def get_data(self):
        return self.data

def ExampleDataTest():
    early_data_object = ExampleData()
    time.sleep(5)
    test = TimeData()
    for i in range(1, 11):
        data_object = ExampleData()
        test.add_data_object(data_object)
        print ""
        print "Iteration: ", i
        print "\tTime Stamp:", test.get_current_time()
        print "\tData Array:", test.get_current_data()
        if i < 10:
            time.sleep(1)
    print ""
    print "TimeDelta = ", test.get_time_delta()
    print "time_list", test.time_list
    test.add_data_object(early_data_object)
    print "TimeDelta after adding old data: ", test.get_time_delta()

def HoloDataTest():
    early_data_object = HoloData()
    time.sleep(1)
    test = TimeData()
    start = time.time()
    for i in range(1, 11):
        now = time.time()
        delta = dt.timedelta(now - start).seconds
        data_object = HoloData(delta)
        test.add_data_object(data_object)
        print ""
        print "Iteration: ", i
        print "\tTime Stamp:", test.get_current_time()
        data = test.get_current_data()
        print "\tData:", data
    print ""
    print "TimeDelta = ", test.get_time_delta()
    print "time_list before adding old: ", test.time_list
    test.add_data_object(early_data_object)
    print "Timedelta after adding old data: ", test.get_time_delta()
    print "time_list after adding old: ", test.time_list
    
if __name__ == '__main__':

    #ExampleDataTest()
    HoloDataTest()
    


