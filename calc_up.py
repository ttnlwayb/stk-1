import os
import pandas as pd
import math
import numpy as np

folder_path = './hist'  # ← 改成你的 CSV 資料夾路徑
def calc(df, window=60, power_sum_point=4000):
    close_diff = df['Close'].diff().fillna(0)
    power = close_diff * df['Volume']
    power_sum_rolling = power.rolling(window=window).sum()
    power_cumsum = power.cumsum()
    power_sum = power_sum_rolling.fillna(power_cumsum)
    power_sum_min = power_sum.rolling(window=window).min().fillna(power_sum.cummin())
    power_sum_max = power_sum.rolling(window=window).max().fillna(power_sum.cummax())
    power_sum_min_diff = power_sum - power_sum_min
    power_sum_max_diff = power_sum_max - power_sum
    close_diff_3k = close_diff.rolling(window=3).sum()
    df['Close_diff'] = close_diff
    df['Power_sum'] = power_sum
    df['Power_sum_min_diff'] = power_sum_min_diff
    df['Power_sum_max_diff'] = power_sum_max_diff
    df['3k_diff_sum'] = close_diff_3k
    df['3k_diff_sum_power'] = close_diff_3k - np.floor(power_sum / power_sum_point)
    df['3k_diff_sum_power_shift'] = df['3k_diff_sum_power'].shift(1).fillna(0)
count = 0
def calc_profit(df, power_sum_point=4000, start_diff_point=6):
    global count
    state = 0
    profits = []
    stop_profit = 25
    move_profit_point = 1.58
    stop_loss = 15
    target_price = 0
    wait = 0
    wait_default = 3
    max_zero_idx = df.index[df['Power_sum_max_diff'] == 0].tolist()
    for _, row in df.iterrows():
        if wait > 0:
            wait -= 1
            continue
        if state == 0:
            power_ratio = row['Power_sum'] / (power_sum_point * start_diff_point)
            start_diff = 6 - math.floor(power_ratio)
            cond1 = row['Power_sum'] > 0
            cond2 = row['Power_sum_max_diff'] <= 30000
            cond3 = row['3k_diff_sum_power_shift'] <= -30
            cond4 = (row['Close'] - row['Low']) >= start_diff
            if np.array([cond1, cond2, cond3, cond4]).all():
                prior_max_idx = [i for i in max_zero_idx if i <= _]
                if prior_max_idx:
                    max_idx = prior_max_idx[-1]
                    if _ - max_idx > 30:
                        continue
                count += 1
                if start_diff < 0:
                    start_diff = 0
                entry_price = row['Low'] + start_diff
                if start_diff < 1:
                    entry_price = row['Open']
                    if (row['High'] - row['Open']) >= stop_profit:
                        profits.append(stop_profit)
                        wait = wait_default
                        continue
                state = 1
                target_price = entry_price
                profits.append(entry_price)
        elif state == 1:
            entry_price = profits[-1]
            target_diff = target_price - entry_price
            loss_threshold = -(stop_loss - math.floor(target_diff * move_profit_point))
            # 判斷是否停損
            if (row['Low'] - entry_price) <= loss_threshold:
                final_loss = min(loss_threshold, stop_profit)
                profits[-1] = final_loss
                state = 0
                wait = wait_default
                continue
            target_price = max(target_price, row['High'])
            # 判斷是否停利
            if (target_price - entry_price) >= stop_profit:
                profits[-1] = stop_profit
                state = 0
                wait = wait_default
    # 避免極大異常值
    if profits and profits[-1] > 10000:
        profits.pop()
        count -= 1
    return np.sum(profits)

def run(window = 60, power_sum_point = 4000, start_diff_point = 6):
    global count
    res = 0
    count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and '_calc' not in filename:
            if 'Daily_2025_04'not in filename:
                continue
            #if '0845to1345' in filename:
            #    continue
            # print(f"{filename}: ")
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            calc(df, window = window, power_sum_point=power_sum_point)
            res += calc_profit(df, power_sum_point=power_sum_point, start_diff_point = start_diff_point)
            base_name = os.path.splitext(filename)[0]
            df.to_csv(os.path.join(folder_path, f"{base_name}_calc.csv"), index=False)
    #print(f"res {res}")
    #print(f"count {count}")
    #print(f"avg {res / count}")
    print(f"{res} {count} {res / count}")