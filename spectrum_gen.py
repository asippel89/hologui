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

    
def gen_spec(timedelta = 1, max_freq = 25e6, num_points = 2**12):
    # Define frequency component for arrays
    f = np.linspace(1, max_freq, num_points)
    
    noise = np.random.normal(0, 1/2**.5, len(f)) + \
        1j*np.random.normal(0, 1/2**.5, len(f))
    spec = abs(holo_PSD(f) + P_2kW_var_1s * noise / timedelta)**.5
    return spec

@np.vectorize
def holo_PSD(max_freq, L = 40):
    T_p = 5.3910632e-44
    c = 2.999792e8
    freq_c = c / (4*np.pi*L)
    if max_freq > .4:
        ans = ((4 * c**2 *T_p) / (np.pi**3 * 4 * max_freq**2)) \
            * (1 - np.cos(max_freq/freq_c))
        return ans
    elif  max_freq >= 0:
        return (8 * (L**2) *T_p)/np.pi
    else:
        return 0

if __name__ == '__main__':
    
    data = gen_spec(1e6)
    print data
    print len(data)
    x = np.linspace(1, 25e6, 2**15)/1e6
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.semilogy(x, data)
    plt.show()
