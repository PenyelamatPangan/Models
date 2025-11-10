import csv
import random
import numpy as np

# --- Configuration ---
NUM_ROWS = 100000
FRESH_ROWS = NUM_ROWS // 2
BAD_ROWS = NUM_ROWS - FRESH_ROWS
OUTPUT_FILENAME = 'food_freshness_dataset.csv'
HEADER = ['C2H5OH_PPM', 'NH3_PPM', 'CH4_PPM', 'MQ_Analog_Value', 'Output']

# --- Sensor Constraints ---
C2H5OH_RANGE = (10.1, 499.9)
NH3_RANGE = (1.1, 499.9)
CH4_RANGE = (100.1, 1999.9)
MQ_ANALOG_RANGE = (50, 950)

def generate_fresh_row():
    """
    Generates a 'Fresh' (Output=1) data row.
    Rules: C2H5OH <= 80 AND NH3 <= 80 AND MQ_Analog <= 400
    """
    
    # 1. Generate C2H5OH (Ethanol) within the 'Fresh' constraint
    # (Range: 10.1 to 80.0)
    c2h5oh = np.random.uniform(C2H5OH_RANGE[0], 80.0)
    
    # 2. Generate NH3 (Ammonia) within the 'Fresh' constraint
    # (Range: 1.1 to 80.0)
    nh3 = np.random.uniform(NH3_RANGE[0], 80.0)
    
    # 3. Generate CH4 (Methane) - generally lower for fresh
    ch4 = np.random.uniform(CH4_RANGE[0], 500.0)
    
    # 4. Generate correlated MQ_Analog_Value
    # We map the C2H5OH range (10-80) to the MQ_Analog 'Fresh' range (50-400)
    # (80-10) = 70. (400-50) = 350. Multiplier is 5.
    mq_base = 50 + (c2h5oh - 10) * 5
    # Add Gaussian noise and clip to the allowed 'Fresh' range (50-400)
    mq_analog = int(np.clip(np.random.normal(loc=mq_base, scale=25), 50, 400))

    return [f"{c2h5oh:.2f}", f"{nh3:.2f}", f"{ch4:.2f}", mq_analog, 1]

def generate_bad_row():
    """
    Generates a 'Bad' (Output=0) data row.
    Rule: (C2H5OH > 100) OR (NH3 > 100) OR (MQ_Analog > 600)
    We create 3 types of "bad" data to satisfy these rules + noise.
    """
    
    rand_type = np.random.rand()
    
    # Type 1 (60% of bad data): High Ethanol (Fermentation)
    # This satisfies the (C2H5OH > 100) rule and the strong correlation rule.
    if rand_type < 0.60:
        # Bias high: 200 to 499.9
        c2h5oh = np.random.uniform(200.0, C2H5OH_RANGE[1])
        # Keep NH3 low to isolate the cause
        nh3 = np.random.uniform(NH3_RANGE[0], 100.0)
        # Full range for CH4
        ch4 = np.random.uniform(CH4_RANGE[0], CH4_RANGE[1])
        
        # Correlate MQ_Analog to high C2H5OH
        # Map C2H5OH (200-500) to MQ_Analog (450-950)
        # (500-200) = 300. (950-450) = 500. Multiplier is ~1.67
        mq_base = 450 + (c2h5oh - 200) * (500 / 300)
        # Add noise and clip to the 'Bad' range (451-950)
        mq_analog = int(np.clip(np.random.normal(loc=mq_base, scale=30), 451, 950))

    # Type 2 (30% of bad data): High Ammonia (Decomposition)
    # This satisfies the (NH3 > 100) rule.
    elif rand_type < 0.90:
        # Keep C2H5OH low to isolate the cause
        c2h5oh = np.random.uniform(C2H5OH_RANGE[0], 100.0)
        # Bias NH3 high: 150 to 499.9
        nh3 = np.random.uniform(150.0, NH3_RANGE[1])
        # Full range for CH4
        ch4 = np.random.uniform(CH4_RANGE[0], CH4_RANGE[1])
        
        # MQ_Analog remains correlated to the *low* C2H5OH
        # This results in a low MQ reading, but the row is still
        # classified as 'Bad' due to high NH3.
        mq_base = 50 + (c2h5oh - 10) * 5
        mq_analog = int(np.clip(np.random.normal(loc=mq_base, scale=25), 50, 450))

    # Type 3 (10% of bad data): High MQ Noise (5% of total dataset)
    # This satisfies the (MQ_Analog > 600) rule and the noise requirement.
    else:
        # Keep C2H5OH and NH3 low
        c2h5oh = np.random.uniform(C2H5OH_RANGE[0], 100.0)
        nh3 = np.random.uniform(NH3_RANGE[0], 100.0)
        # Full range for CH4
        ch4 = np.random.uniform(CH4_RANGE[0], CH4_RANGE[1])
        
        # Force a high MQ reading (e.g., "Lighter gas" false positive)
        # This triggers the (MQ_Analog > 600) rule.
        mq_analog = np.random.randint(601, 950)

    return [f"{c2h5oh:.2f}", f"{nh3:.2f}", f"{ch4:.2f}", mq_analog, 0]

def main():
    """
    Main function to generate data and write to CSV.
    """
    print(f"Generating {NUM_ROWS} rows of synthetic data...")
    data = []
    
    # 1. Generate Fresh Rows
    for _ in range(FRESH_ROWS):
        data.append(generate_fresh_row())
        
    # 2. Generate Bad Rows
    for _ in range(BAD_ROWS):
        data.append(generate_bad_row())
        
    # 3. Shuffle the dataset
    random.shuffle(data)
    
    # 4. Write to CSV file
    print(f"Writing data to {OUTPUT_FILENAME}...")
    try:
        with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
            writer.writerows(data)
        print("Done.")
        print(f"Successfully generated {OUTPUT_FILENAME} with {len(data)} rows.")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    # You may need to install numpy: pip install numpy
    main()