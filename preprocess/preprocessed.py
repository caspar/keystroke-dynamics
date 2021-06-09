import sys, re, csv
#import pandas as pd
from tqdm import tqdm

def transform(userID, trial_number, sample_number, line, pwd_length):
    """
    Transform time stamp sequence to features: Hold time, Up-Down time, Down-Down time
    """
    keys = line.split(",")[::3]
    stroke_types = line.split(",")[1::3]
    times = [float(t) for t in line.split(",")[2::3]]

    result = [userID, trial_number, sample_number]

    up_indices = [i for i, u in enumerate(stroke_types) if u == "UP"]
    down_indices = [i for i, u in enumerate(stroke_types) if u == "DOWN"]

    # Hold time
    for k in range(pwd_length):
        down_time = times[ down_indices[k] ]
        up_time = times[ up_indices[k] ]
        hold_time = up_time - down_time
        result.append(hold_time)
        
    # Up-Down time
    for k in range(pwd_length - 1):
        k_pre_up_time = times[ up_indices[k] ]
        k_next_down_time = times[ down_indices[k+1] ]
        up_down_time = k_next_down_time - k_pre_up_time
        result.append(up_down_time)

    # Down-Down time
    for k in range(pwd_length - 2):
        k_pre_down_time = times[ down_indices[k] ]
        k_next_down_time = times[ down_indices[k+1] ]
        down_down_time = k_next_down_time - k_pre_down_time
        result.append(down_down_time)
    
    return result

def generate_raw(file_path, pwd_length, userID, trial_number):
   
    raw = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.replace(' ', "").replace('\'', "").replace('\"', "").replace('(', "").replace(')', "").replace('\n', '')

        test_len = len(line.split(",")[1::3])
        if test_len != pwd_length * 2:
            #assert len(stroke_types) == pwd_length * 2, f"The total keystroke number is {len(stroke_types)}, which should be {pwd_length * 2}."
            continue

        which_trial = (i)//trial_number + 1
        which_sample = trial_number if (i+1) % trial_number == 0 else (i+1) % trial_number

        result = transform(userID, which_trial, which_sample, line, pwd_length)
        #print(result)
        raw.append(result)

    with open(f"raw-data{userID}.csv","w+") as my_csv:
        csvWriter = csv.writer(my_csv,delimiter=',')
        csvWriter.writerows(raw)
    
    #pd.DataFrame(raw).to_csv(f"{userID}.csv", header=None, index=False)

def main(argv):

    file_path, pwd_length, userID, trial_number = argv
    generate_raw(file_path, int(pwd_length), int(userID), int(trial_number))

if __name__ == '__main__':
    main(sys.argv[1:])
