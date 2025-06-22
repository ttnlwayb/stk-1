import calc_up
import calc_down


win_s = [40, 60, 80, 100, 120]
power_sum_points = [4000, 6000, 8000, 10000, 12000]
start_diff_points = [6, 8, 10, 12]
#win_s = [60]
#power_sum_points = [8000]
#start_diff_points = [10]
for window in win_s:
    for power_sum_point in power_sum_points:
        for start_diff_point in start_diff_points:
            print(f"{window} {power_sum_point} {start_diff_point}", end=" ")
            calc_down.run(window = window, power_sum_point = power_sum_point, start_diff_point = start_diff_point)
            