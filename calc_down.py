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
def calc_profit(df, power_sum_point=4000, start_diff_point = 6, start_diff_point_2 = 6):
    global count
    # 0, 1
    state = 0
    profits = []
    stop_profit = 25
    move_profit_point = 1.47
    stop_loss = 15
    target_price = 0
    wait = 0
    wait_default = 3
    min_zero_idx = df.index[df['Power_sum_min_diff'] == 0].tolist()
    for _, row in df.iterrows():
        if wait > 0:
            wait -= 1
            continue
        if state == 0:
            if _ < 4:
                continue
            pre_row = df.iloc[ _ - 1]
            second_row = df.iloc[ _ - 2]
            third_row = df.iloc[ _ - 3]
            pwer_sum = row['Power_sum']
            pwer_sum_abs = abs(pwer_sum)
            power_sum_wei = np.floor(pwer_sum / 100000)
            _3k_change = pre_row['High'] - third_row['Low'] - power_sum_wei
            _2k_change = row['High'] - second_row['Low'] - power_sum_wei
            power_ratio = pwer_sum_abs / (power_sum_point * start_diff_point)
            start_diff = start_diff_point_2 - math.floor(power_ratio)
            start_diff2 = 20
            cond1 = row['Power_sum'] < 0
            cond2 = row['Power_sum_min_diff'] <= 30000
            cond3 = row['3k_diff_sum_power_shift'] >= 30
            cond3 = _3k_change >= 30
            cond32 = _2k_change >= 20
            cond4 = (row['High'] -  row['Close']) >= start_diff
            cond42 = (row['High'] - row['Close']) >= start_diff2
            if np.array([cond1, cond2, cond3, cond4]).all():
                prior_min_idx = [i for i in min_zero_idx if i <= _]
                if prior_min_idx:
                    min_idx = prior_min_idx[-1]
                    if _ - min_idx > 30:
                        continue
                count += 1
                if start_diff < 0:
                   start_diff = 0
                entry_price = row['High'] - start_diff
                if start_diff < 1:
                    entry_price =  row['Open']
                    target_price = row['Low']
                    if row['Open'] - row['Low'] >= stop_profit:
                        profits.append(stop_profit)
                        wait = wait_default
                        continue
                state = 1
                target_price = entry_price
                profits.append(entry_price)
            elif np.array([cond1, cond2, cond32, cond42]).all():
                prior_min_idx = [i for i in min_zero_idx if i <= _]
                if prior_min_idx:
                    min_idx = prior_min_idx[-1]
                    if _ - min_idx > 30:
                        continue
                count += 1
                entry_price = row['High'] - start_diff2
                state = 1
                target_price = entry_price
                profits.append(entry_price)
        elif state == 1:
            entry_price = profits[-1]
            target_diff = entry_price - target_price
            loss_threshold = -(stop_loss - math.floor(target_diff * move_profit_point))
            # 判斷是否停損
            if entry_price - row['High'] <= loss_threshold:
                final_loss = min([loss_threshold, stop_profit])
                profits[-1] = final_loss
                state = 0
                wait = wait_default
                continue
            target_price = min([target_price, row['Low'] ])
            # 判斷是否停利
            if entry_price - row['Low'] >= stop_profit:
                state = 2
                continue
                #profits[-1] = stop_profit
                #state = 0
                #wait = wait_default
        elif state == 2:
            diff = 4
            if row['High'] - target_price >= diff:
                profits[-1] = entry_price - target_price - diff
                state = 0
                wait = wait_default
            target_price = min([target_price, row['Low'] ])
    if profits and profits[-1] > 10000:
        profits.pop()
        count -= 1
    # print(f"{profits}")
    all_sum = np.array(profits).sum()
    return all_sum
def run(window = 60, power_sum_point = 4000, start_diff_point = 6, start_diff_point_2 = 6):
    global count
    res = 0
    count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and '_calc' not in filename:
            if 'Daily_2025_06'not in filename:
                continue
            #if '0845to1345' in filename:
            #    continue
            # print(f"{filename}: ")
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            calc(df, window = window, power_sum_point=power_sum_point)
            res += calc_profit(df, 
                power_sum_point=power_sum_point, 
                start_diff_point = start_diff_point, 
                start_diff_point_2 = start_diff_point_2)
            #base_name = os.path.splitext(filename)[0]
            #df.to_csv(os.path.join(folder_path, f"{base_name}_calc.csv"), index=False)
    #print(f"res {res}")
    #print(f"count {count}")
    #print(f"avg {res / count}")
    print(f"{res} {count} {res / count}")