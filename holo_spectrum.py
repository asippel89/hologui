
import numpy as np
import matplotlib.pylab as pyl

def gen_iter(colors):
    if not np.iterable(colors):
        def __iter_colors():
            while True:
                yield None
        iter_colors = __iter_colors()
    else:
        iter_colors = iter(colors)
    return iter_colors
        
def iterdict(**kwargs):
    D = {}
    for name, item_iter in kwargs.iteritems():
        val = item_iter.next()
        if val is not None:
            D[name] = val
    return D


T_p = 5.3910632e-44
c = 2.999792e8

total_holographic_var = 4 * c * T_p * 40 / np.pi # shouldn't this be 4 * T_p * L**2 / pi, where L is 40?

@np.vectorize
def holo_PSD(freq, L = 40):
    freq_c = c / (4 * np.pi * L)
    if freq > .4:
        return ((4 * c**2 *T_p) / (np.pi**3 * 4 * freq**2)) * (1 - np.cos(freq/freq_c))
    elif freq >= 0:
        return (8 * (L**2) *T_p)/np.pi
    else:
        return 0

F_nyquist = 15e6
f = np.linspace(1,F_nyquist,10000)

def plot_holo_spectrum():
    F_nyquist = 20e6
    f = np.linspace(1,F_nyquist,10000)

    fig = pyl.figure()
    #ax = fig.add_subplot(2,1,2)
    ax = fig.add_subplot(1,1,1)
    ax.plot(f/1e6, holo_PSD(f)**.5)
    ax.set_ylim(holo_PSD(0)**.5/100, 1.2*holo_PSD(0)**.5)
    ax.set_title("dL cross Linear Spectral Density")
    ax.set_xlabel("Frequency [MHz]")
    ax.set_ylabel("Length deviation [$m/\sqrt{\mathrm{Hz}}$]")
    ax.grid()

    fig.set_dpi(100)

def plot_holo_correlation():
    F_nyquist = 15e6
    f = np.linspace(1,F_nyquist,10000)

    Acorr = np.fft.rfft(np.concatenate([holo_PSD(f), holo_PSD(f[::-1])])) * F_nyquist / len(f)
    T_inc = 1 / (2*f[-1])
    t = np.arange(len(Acorr)) * T_inc
    #ax = fig.add_subplot(2,1,1)
    fig = pyl.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(t * 1e6, Acorr**.5)
    ax.axvline(2*40/c * 1e6, 0, 1, ls='--', color=(0,0,0,.7))
    ax.set_xlim(0, 2*2*40/c * 1e6)
    ax.set_title("dL cross correlation")
    ax.set_xlabel("Time [$\mu s$]")
    ax.set_ylabel("Length deviation [$m$]")
    ax.grid()

def plot_holo_spectrum_noisy(noise_level_mrhz = 0,
                                int_times = [], 
                                colors = None,
                             labels = None,
                             ax = None,
                                ):
    if not ax:
        fig = pyl.figure()
        #ax = fig.add_subplot(2,1,2)
        ax = fig.add_subplot(1,1,1)
    
    F_nyquist = 25e6
    f = np.linspace(1, F_nyquist,2**15)

    colors = gen_iter(colors)
    labels = gen_iter(labels)
    for T_i in int_times:
        noise = np.random.normal(0, 1/2**.5, len(f)) + 1j*np.random.normal(0, 1/2**.5, len(f))
        ax.semilogy(f/1e6, 
                    abs(holo_PSD(f) + noise_level_mrhz**2 * noise / T_i)**.5,
                    **iterdict(color = colors,
                               label = labels,
                              )
                   )

    ax.semilogy(f/1e6, holo_PSD(f)**.5, color=(1,0,0), label="holographic prediction")
    ax.set_ylim(holo_PSD(0)**.5/100, 2*holo_PSD(0)**.5 + 2*noise_level_mrhz)

    ax.axhline(noise_level_mrhz, 0, 1, color = (1,1,0), label='Shot noise')
    ax.set_title("dL cross Linear Spectral Density")
    ax.set_xlabel("Frequency [MHz]")
    ax.set_ylabel("Length deviation [$m/\sqrt{\mathrm{Hz}}$]")
    ax.legend()
    ax.grid()
    return

def plot_holo_correlation_noisy(noise_level_mrhz = 0, 
                                int_times = [], 
                                colors = None,
                                labels = None,
                                ax = None
                               ):
    if not ax:
        fig = pyl.figure()
        #ax = fig.add_subplot(2,1,2)
        ax = fig.add_subplot(1,1,1)
    
    F_nyquist = 25e6
    N = 2**15
    f = np.linspace(1, F_nyquist,2**15)
    T_inc = 1 / (2*f[-1])
    t = np.arange(N) * T_inc

    ax.set_xlim(0, 2*2*40/c * 1e6)
    ax.set_ylim(0, 2 * total_holographic_var**.5)
    
    colors = gen_iter(colors)
    labels = gen_iter(labels)
    for T_i in int_times:
        noise = np.random.normal(0, 1/2**.5, len(f)) + 1j*np.random.normal(0, 1/2**.5, len(f))
        CSD = holo_PSD(f) + noise_level_mrhz**2 * noise / T_i
        Acorr = (np.fft.rfft(np.concatenate([CSD, CSD[::-1]])) * F_nyquist / len(f))[:N]
        ax.plot(t * 1e6, 
                abs(Acorr)**.5, 
                **iterdict(color = colors,
                           label = labels,
                          )
               )

    PSD = holo_PSD(f)
    Acorr = (np.fft.rfft(np.concatenate([PSD, PSD[::-1]])) * F_nyquist / len(f) )[:N]
    ax.plot(t * 1e6, abs(Acorr)**2, color=(1,0,0), label="holographic prediction")
    ax.axvline(2*40/c * 1e6, 0, 1, ls='--', color=(0,0,0,.7))

    ##ax.axhline(noise_level_mrhz, 0, 1)
    ax.legend()
    ax.grid()
    ax.set_title("dL cross correlation")
    ax.set_xlabel("Time [$\mu s$]")
    ax.set_ylabel("Length deviation [$m$]")
    return

E_lambda = 1.9864e-25/1.064e-6 #energy of the photons in watts
P_1W_var_1s = ((E_lambda/1)**.5 / (2 * np.pi) * 1.064e-6)**2 #shot_noise_variance over 1second
P_2kW_var_1s = ((E_lambda/2000)**.5 / (2 * np.pi) * 1.064e-6)**2 #shot_noise_variance over 1second


def plot_spectral_noisy(fname = 'spectral_noisy.png'):
    fig = pyl.figure()
    ax = fig.add_subplot(1,1,1)
    plot_holo_spectrum_noisy(P_2kW_var_1s**.5, 
                                [ 
                                 1e2,
                                 1e4,
                                 1e5,
                                 1e6,
                                ],
                                colors = [
                                          (0,.5,0,.5),
                                          (0,.5,.5,.6),
                                          (0,0,1,.8),
                                          (1,0,1,.8),
                                         ],
                                labels = [
                                          "$1*10^2$s (~2min)",
                                          "$1*10^4$s (2.7h)",
                                          "$1*10^5$s (~1day)",
                                          "$1*10^6$s (10days)",
                                         ],
                                ax = ax
                               )

    if fname:
        fig.set_dpi(100)
    return fig


def plot_correlation_noisy(fname = 'correlation_noisy.png'):
    fig = pyl.figure()
    ax = fig.add_subplot(1,1,1)
    plot_holo_correlation_noisy(P_2kW_var_1s**.5, 
                             [ 
                              1e2,
                              1e4,
                              1e5,
                              1e6,
                             ],
                             colors = [
                                       (0,.5,0,.5),
                                       (0,.5,.5,.6),
                                       (0,0,1,.8),
                                       (1,0,1,.8),
                                      ],
                             labels = [
                                       "$1*10^2$s (~2min)",
                                       "$1*10^4$s (2.7h)",
                                       "$1*10^5$s (~1day)",
                                       "$1*10^6$s (10days)",
                                      ],
                             ax = ax
                            )

    return fig




if __name__ == '__main__':
    plot = plot_spectral_noisy()
    pyl.show()
    
