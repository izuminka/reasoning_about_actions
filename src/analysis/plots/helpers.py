import matplotlib.pyplot as plt
import numpy as np

NAME_KEY = 'name'
DATA_KEY = 'data'
ERROR_KEY = 'error'


def plt_n_bars(categories, groups):
    plt.figure(figsize=(10, 5))
    bar_width = 0.3

    mult_factor = bar_width * len(groups) * 1.1

    ind = np.arange(len(categories)) * mult_factor  # the x locations for the groups
    num_groups = len(groups)
    total_width = num_groups * bar_width
    offset = total_width / 2 - bar_width / 2  # to center the group of bars

    for i, group in enumerate(groups):
        data = [0 if x is None else x for x in group[DATA_KEY]]
        if ERROR_KEY in group:
            plt.bar(ind + i * bar_width, data, width=bar_width, label=group[NAME_KEY], yerr=group[ERROR_KEY][i], capsize=5)
        else:
            plt.bar(ind + i * bar_width, data, width=bar_width, label=group[NAME_KEY])

    # Set the x-axis labels in the middle of the groups of bars
    plt.xticks(ind + offset, categories, rotation=30)
    plt.legend()



# #
# # Example usage
# categories = ['Category 1', 'Category 2', 'Category 3']
# group1 = {NAME_KEY: 'Group 1', DATA_KEY: [20, 35, 30]}
# group2 = {NAME_KEY: 'Group 2', DATA_KEY: [23, 30, 28]}
# group3 = {NAME_KEY: 'Group 3', DATA_KEY: [25, 27, None]}
#
# plt_n_bars(categories, [group1, group2, group3])
# plt.show()
