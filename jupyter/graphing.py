# Boilerplate code for real-time graphs
# For Jupyter
%matplotlib notebook

def create_plot(*labels, history=100):
    """ Generates an interactive plot """
    import matplotlib.pyplot as plt
    import time

    # Create x-axis, data for history
    num_axes = len(labels)
    axes_data = [[] for _ in range(num_axes)]
    xs = list(range(history+1))

    # Hardcoded dimensions for axes 1 to 4
    PLOT_CONFIG = {
        1: [{"figsize":(6,4)}, {"shape":(1,1), "loc":[(0,0)], "colspan":[1]}],
        2: [{"figsize":(9,4)}, {"shape":(1,2), "loc":[(0,0),(0,1)], "colspan":[1,1]}],
        3: [{"figsize":(9,8)}, {"shape":(2,2), "loc":[(0,0),(0,1),(1,0)], "colspan":[1,1,2]}],
        4: [{"figsize":(9,8)}, {"shape":(2,2), "loc":[(0,0),(0,1),(1,0),(1,1)], "colspan":[1,1,1,1]}],
    }
    fig_config, ax_configs = PLOT_CONFIG[num_axes]
    fig = plt.figure(**fig_config)
    axs = []
    flags_yprecision = []
    for i in range(num_axes):
        shape, loc, colspan = ax_configs["shape"], ax_configs["loc"][i], ax_configs["colspan"][i]

        # Modify plot
        ax = plt.subplot2grid(shape, loc, colspan=colspan)
        ax.set_xlim([0,history])
        ax.grid()
        axs.append(ax)

        # Meta-settings
        flags_yprecision.append(True)
        ax.set_ylabel(labels[i])

    def get_global_max(data): return get_global_f(max, data)
    def get_global_min(data): return get_global_f(min, data)
    def get_global_f(f, data):
        if hasattr(data[0], "__len__"): # nested recursive search
            data = [get_global_f(f, lst) for lst in data]
        return f([v for v in data if v is not None])

    def catch_interrupt(f):
        # Wrap plotter with try-except to hide interrupt error message
        def helper(*ax_values, sleep=None):
            try:
                return f(*ax_values, sleep=sleep)
            except KeyboardInterrupt:
                pass
        return helper

    @catch_interrupt
    def plotter(*ax_values, sleep=None):
        # format: plotter([v1,v2],[v3]) for two axes
        if len(ax_values) != num_axes:
            # Special coercion for single axis
            if num_axes == 1:
                ax_values = [ax_values]
            else:
                raise ValueError(
                    "Wrong number of axes - expected {}, provided {}".format(num_axes, len(ax_values)) + \
                    "\n  Check if number of axes is correct, i.e. create_plot('label1', 'label2') for two axes."
                )

        for j in range(num_axes):
            ax = axs[j]
            data = axes_data[j]
            values = ax_values[j]
            flag_yprecision = flags_yprecision[j]

            # Specially coerce single value into list
            if not hasattr(values, "__len__"):
                values = [values]

            # Initialize for first call
            if not data:
                init_ys = [None]*(history+1)
                for i in range(len(values)):
                    ys = deque(init_ys, maxlen=(history+1))
                    data.append(ys)
                    ax.plot(xs, ys)

            # Append new values
            assert len(values) == len(data)
            for i in range(len(values)):
                data[i].append(values[i])
                line = ax.lines[i]
                line.set_ydata(data[i])

            global_min, global_max = get_global_min(data), get_global_max(data)

            # Dynamically set y float format
            if global_max - global_min < 100:
                if not flag_yprecision:
                    ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
                    flags_yprecision[j] = True
            else:
                if flag_yprecision:
                    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
                    flags_yprecision[j] = False

            # Dynamically set y range
            if global_min == global_max:
                global_max += 1
            if flag_yprecision:
                ax.set_ylim([global_min-0.01, global_max+0.01])
            else:
                ax.set_ylim([0.99*global_min, 1.01*global_max])

        # Draw
        plt.tight_layout()
        fig.canvas.draw()

        # Sleep (in seconds)
        if sleep:
            time.sleep(sleep)

    return plotter
