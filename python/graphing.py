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
