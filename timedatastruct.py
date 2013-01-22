#!/usr/bin/python

#timedatastruct.py

import numpy as np
import datetime as dt

class TimeData(object):
    """Base class for time data"""
    def __init__(self):
        # self.initial_set = timedataobject
        # self.current_data = self.initial_set
        self.current_data =  0
        pass

    def get_current_data(self):
        return self.current_data

    def add_more_data(self, more_data):
        if self.current_data == 0:
            self.current_data = more_data
        else:
            self.current_data += more_data

    def get_time_delta(self):
        time_delta = self.current_data[-1][0] - self.current_data[0][0]
        return time_delta

class ExampleData(object):
    def __init__(self, num_points):
        self.data_list = []
        self.num_points = num_points
        
    def random_stream(self, frame_size = 2**16):
        points_remaining = self.num_points
        while points_remaining > 0:
            if points_remaining < frame_size:
                subframe_size = points_remaining
            else:
                subframe_size = frame_size
                
            dataframe = np.random.normal(0, 1, frame_size)
            time = dt.datetime.now()
            frame = [time, dataframe]
            if points_remaining == self.num_points:
                print frame
            yield frame        
            points_remaining -= subframe_size
        return

    def collect_stream(self):
        for frame in self.random_stream():
            self.data_list.append(frame)
        return self.data_list

class TimeFrame(object):
    

if __name__ == '__main__':

    # test1 = ExampleData(1000000)
    # data = test1.collect_stream()
    # instance = TimeData(data)
    # result = instance.get_current_data()
    # print result
    # print len(result)
    # print "time delta = ", instance.get_time_delta()

    # newdatainstance = ExampleData(10000000)
    # newdata = newdatainstance.collect_stream()
    # instance.add_more_data(newdata)
    # print "now result = ", instance.get_current_data()
    # print "now len = ", len(instance.get_current_data())
    # print "now time delta = ", instance.get_time_delta()
    instance = TimeData()
    dataframegen = ExampleData(10000000)
    for frame in dataframegen.random_stream():
        instance.add_more_data(frame)
    #print instance.get_current_data()
    print instance.get_current_data()[-1][0]
    print instance.get_current_data()[0][0]
    #print "timedelta = ", instance.get_time_delta()
