import sys, re
import pandas as pd
from tqdm import tqdm

def transform(userID, trial_number, sample_number, time_stamps):
    """
    Transform time stamp sequence to features: Hold time, Up-Down time, Down-Down time
    """

    result = [userID, trial_number, sample_number]

    # Hold time
    for i in range(0, len(time_stamps), 2):
        down_time = time_stamps[i]
        up_time = time_stamps[i+1]
        hold_time = up_time - down_time
        result.append(hold_time)

    # Up-Down time
    for i in range(1, len(time_stamps)-1, 2):
        k_pre_up_time = time_stamps[i]
        k_next_down_time = time_stamps[i+1]
        up_down_time = k_next_down_time - k_pre_up_time
        result.append(hold_time)

    # Down-Down time
    for i in range(0, len(time_stamps)-2, 2):
        k_pre_down_time = time_stamps[i]
        k_next_down_time = time_stamps[i+2]
        down_down_time = k_next_down_time - k_pre_down_time
        result.append(hold_time)
    
    return result

def generate_raw(file_path, userID, trial_number):
   
    raw = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        split = line.split(",")[2::3]
    
        time_stamps = []
        for t in split:
            time_stamps.append( float(t.replace(' ', "").replace('\"', "").replace(')', "")) )
        #print(time_stamps)

        which_trial = (i+1)//trial_number + 1
        which_sample = 10 if (i+1) % trial_number == 0 else (i+1) % trial_number

        result = transform(userID, which_trial, which_sample, time_stamps)
        #print(result)
        raw.append(result)

    pd.DataFrame(raw).to_csv(f"{userID}.csv", header=None, index=False)

def main(argv):

    file_path, userID, trial_number = argv
    generate_raw(file_path, int(userID), int(trial_number))

if __name__ == '__main__':
    main(sys.argv[1:])
