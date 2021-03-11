from ehyd_tools.design_rainfall import (ehyd_design_rainfall_ascii_reader, get_ehyd_file, get_max_calculation_method,
                                        get_rainfall_height, )

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if __name__ == '__main__':
    df = ehyd_design_rainfall_ascii_reader(get_ehyd_file(grid_point_number=5214))
    rain_height = get_max_calculation_method(df)

    fig, (ax1, ax2) = plt.subplots(2, sharex=True)  # type: plt.Figure, (plt.Axes, plt.Axes)

    duration_max = 120
    return_periods = [1, 2, 3, 5, 10, 20, 50, 100][::-1]

    rain_height.columns.name = 'Wiederkehr-\nperiode\nin Jahre'
    ax = rain_height.loc[:duration_max, return_periods].plot(ax=ax1)
    ax.set_xlabel('Dauerstufe in min')
    ax.set_ylabel('Bemessungsregenhöhe in mm')

    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., title='Wiederkehr-\nperiode\nin Jahre')

    # rain_flow_rate = rain_height.div(rain_height.index.to_series(), axis=0) * 1000 / 60
    durations = np.arange(5, duration_max, 1)
    rain_flow_rate = pd.DataFrame(index=durations)
    for tn in rain_height:
        # get_rainfall_height(rain_height, tn, durations)

        rain_flow_rate[tn] = np.interp(durations, rain_height.index.values, rain_height[tn]) / durations * 1000 / 60

    ax = rain_flow_rate.loc[:duration_max, return_periods].plot(ax=ax2)
    ax.set_xlabel('Dauerstufe in min')
    ax.set_ylabel('Bemessungsregenspende in L/(s.ha)')

    ax.legend().remove()

    fig.set_size_inches(7, 7)
    fig.tight_layout()
    # fig.show()
    fig.savefig('5214_design_rainfall_plot2.png')
