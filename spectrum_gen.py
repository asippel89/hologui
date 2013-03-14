#!/usr/bin/python

#spectrum_gen.py

#######   Holometer Spectrum Generator   #######
# 
# General-purpose script for generating arrays 
# representing the power spectrum of noisy
# holographic noise
#
################################################


import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

     # Define necessary constants
T_p = 5.3910632e-44
c = 2.999792e8

#energy of the photons in watts
E_lambda = 1.9864e-25/1.064e-6 

#shot_noise_variance over 1second
P_1W_var_1s = ((E_lambda/1)**.5 / (2 * np.pi) * 1.064e-6)**2 
#shot_noise_variance over 1second
P_2kW_var_1s = ((E_lambda/2000)**.5 / (2 * np.pi) * 1.064e-6)**2 

total_holographic_var = 4 * c * T_p * 40 / np.pi 
            # shouldn't this be 4 * T_p * L**2 / pi, where L is 40?

class HoloData(object):

    def __init__(self, timedelta, int_time=.05, fsamp=100e6, NFFT=2**12, 
                     noise_level=P_2kW_var_1s):
        self.now = dt.datetime.now()
        self.timedelta = timedelta
        self.int_time = int_time
        self.fsamp = fsamp
        self.NFFT = NFFT
        self.noise_level = noise_level
        self.max_freq = self.fsamp/2 # Nyquist Freq
        self.num_points = self.NFFT/2 + 1
        self.num_coadded = self.timedelta * self.fsamp
        self.tuple_list = [(0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0), (3,1), \
                               (3,2), (3,3)]
        self.data_dict = {}
        self.gen_data()
        self.run_information = dict([('window_function', 'Hanning'), \
                                         ('ADC_settings', {'f_samp': self.fsamp,\
                                                               'gain': 10}), \
                                         ('channel_info', {'1': 'test', \
                                                               '2': 'blah'}),\
                                         ('yunits',
                                        'Length Deviation [$m/\sqrt{\mathrm{Hz}}$]'),
                                         ('xunits', 'Frequency [MHz]'), \
                                         ('NFFT', self.NFFT)])

    def gen_data(self):
        for i in range(len(self.tuple_list)):
            if self.tuple_list[i][0] == self.tuple_list[i][1]:
                self.data_dict[self.tuple_list[i]] = self.gen_spec(1)
            else:
                if self.timedelta < 1:
                    self.data_dict[self.tuple_list[i]] = self.gen_spec(1)
                else:
                    self.data_dict[self.tuple_list[i]] = self.gen_spec(self.int_time)

    def gen_spec(self, int_time):
        # Define frequency component for arrays
        f = np.linspace(1, self.max_freq, self.num_points)
        
        noise = np.random.normal(0, 1/2**.5, len(f)) + \
            1j*np.random.normal(0, 1/2**.5, len(f))
        spec = holo_PSD(f) + self.noise_level * noise / int_time
        return spec

    def get_time(self):
        return self.now

    def get_data(self):
        return self.data_dict

    def get_run_info(self):
        return self.run_information
    
    def get_num_coadded(self):
        return self.num_coadded

@np.vectorize
def holo_PSD(freq, L = 40):
    T_p = 5.3910632e-44
    c = 2.999792e8
    freq_c = c / (4*np.pi*L)
    if freq > .4:
        ans = ((4 * c**2 *T_p) / (np.pi**3 * 4 * freq**2)) \
            * (1 - np.cos(freq/freq_c))
        return ans
    elif  max_freq >= 0:
        return (8 * (L**2) *T_p)/np.pi
    else:
        return 0

    
