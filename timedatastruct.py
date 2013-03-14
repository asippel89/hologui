#!/usr/bin/python

#timedatastruct.py
from threading import RLock
import threading
import numpy as np
import datetime as dt
import time
import bisect
import spectrum_gen as sgen

class TimeData(object):
    """General class for dealing with time data in a thread-safe way"""
    def __init__(self):
        self.data_object_list = []
        self.time_list = []
        # data_object_list and time_list must be kept in sync, do not modify to one
        # without modifying the other
        self.running_avg = None
        self.num_coadded = None
        self.run_information = None
        self.mutex = RLock()

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
                self.calculate_running_avg()
                # print 'Data object list length:', len(self.data_object_list)
        return

    def retrieve_data_interval(self, start, end):
        """Method to retrieve an interval of data, returns the spliced list"""
        with self.mutex:
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

    def calculate_running_avg(self):
        if self.num_coadded is None:
            self.num_coadded = self.data_object_list[-1].get_num_coadded()
        if self.running_avg is None:
            self.running_avg = self.data_object_list[-1].get_data()
        else:
            new_num_coadded = self.data_object_list[-1].get_num_coadded()
            current_data_dict = self.data_object_list[-1].get_data()
            for key in self.running_avg.keys():
                self.running_avg[key] = (current_data_dict[key] + 
                    self.num_coadded*self.running_avg[key])/new_num_coadded
                self.num_coadded = new_num_coadded
        return self.running_avg

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

    def get_current_running_avg(self):
        return self.running_avg

class StreamDataTest(object):
    
    def __init__(self, report_data_method, update_int=.5, noise_level='Default', \
                     NFFT='Default', fsamp='Default', int_time='Default'):
        self.keep_going = True
        self.update_int = update_int
        self.options_dict = dict([('noise_level', noise_level), ('NFFT', NFFT), \
                                     ('fsamp', fsamp), ('int_time', int_time)])
        self.supply_args = False
        self.time_start = time.time()
        self.report_data = report_data_method
        self.frame_num = 0

    def _check_defaults(self):
        '''
        Need to check if they are default, this class does not have knowledge
        of what those defaults are
        '''
        for value in self.options_dict.values():
             if value != 'Default':
                 self.supply_args = True
        return

    def _run_stream(self):
        while self.keep_going:
            now = time.time()
            delta = now - self.time_start
            # May need to divide num_coadded by 2 because of Welch overlap
            if self.supply_args:
                data = sgen.HoloData(delta, **self.options_dict)
            else:
                data = sgen.HoloData(delta)
            self.report_data(data)
            self.frame_num += 1
            time.sleep(self.update_int)

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
    


