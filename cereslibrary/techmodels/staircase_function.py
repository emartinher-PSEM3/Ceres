
# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate
from scipy.optimize import curve_fit
from matplotlib.ticker import LinearLocator, FormatStrFormatter



filter_max_capacity = 1300

filter_flow=10

n_aux=filter_flow/filter_max_capacity

#sum(1/(1+e^(-100*((n_auxiliar[units_i[3]]+1)-n))) for n in collect(1:100))

a = np.sum((1/(1+np.exp(-1000*((n_aux+1)-np.arange(1,1000,1))))))

print("a =", a)

y=[]
for n_aux in np.arange(1,10,0.001):
    a = np.sum((1/(1+np.exp(-1000*((n_aux+1)-np.arange(1,1000,1))))))
    y.append(a)

plt.plot(np.arange(1,10,0.001), y)

