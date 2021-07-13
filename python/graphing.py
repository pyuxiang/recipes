### GRAPH PLOTTING CONFIG ###
# Interpolation methods
from numpy import interp as lininterp
try:
    from scipy import interpolate
    def cubicinterp(new_xs, old_xs, old_ys):
        spfn = interpolate.splrep(old_xs, old_ys)
        return list(map(lambda x: interpolate.splev(x, spfn), new_xs))
except ModuleNotFoundError:
    print("Warning: cubicinterp not available, scipy dependency.")

# Graphing methods
import matplotlib
matplotlib.rcParams["toolbar"] = "None" # hide nav toolbars
import matplotlib.pyplot as plt
plt.rcParams.update({'axes.titlesize': 'x-large',
                     'axes.labelsize': 'x-large'})


### Curve fitting ###

from scipy.optimize import curve_fit
import numpy as np

def _cool_exp(t, T1, T0, tau):
    return T0 + (T1-T0)*np.exp(-t/tau)

def test():
    with open("20210712_cool_data.dat") as f:
        data = f.read()
        data = [[float(d) for d in row.split(" ")] for row in data.split("\n") if row != ""]

    xs, ys = list(zip(*data))
    popt, pcov = curve_fit(_cool_exp, xs, ys)
    fit = list(zip(popt, np.sqrt(np.diag(pcov))))
    for param, param_err in fit:
        print(param, "+/-", param_err)
