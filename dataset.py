import csv
import random
import numpy as np

# --- Configuration ---
NUM_ROWS = 100000
FRESH_ROWS = NUM_ROWS // 2
BAD_ROWS = NUM_ROWS - FRESH_ROWS
OUTPUT_FILENAME = 'food_freshness_dataset.csv'
HEADER = [
    'MQ135_Analog',         # MQ135 Air Quality Sensor (0-1023)
    'MQ3_Analog',           # MQ3 Alcohol Sensor (0-1023)
    'MiCS5524_Analog',      # Fermion MiCS-5524 Gas Sensor (0-1023)
    'Output'                # 1=Fresh, 0=Bad
]

# --- Sensor Constraints (Analog readings from 10-bit ADC) ---
# All sensors output analog values that are read by Arduino's ADC (0-1023)

# MQ135 Air Quality Sensor
# Detects: NH3, NOx, alcohol, benzene, smoke, CO2
# Fresh air: 100-300, Polluted/Spoiled: 400-1023
MQ135_FRESH_RANGE = (100, 350)
MQ135_BAD_RANGE = (400, 1023)

# MQ3 Alcohol Sensor
# Detects: Alcohol, ethanol vapor
# Low alcohol (fresh): 100-350, High alcohol (fermentation): 400-1023
MQ3_FRESH_RANGE = (100, 350)
MQ3_BAD_RANGE = (400, 1023)

# Fermion MiCS-5524 MEMS Gas Sensor
# Detects: CO, CH4, C2H5OH, H2, NH3 (multi-gas)
# Clean air: 100-300, High gas concentration (spoiled): 400-1023
MICS5524_FRESH_RANGE = (100, 350)
MICS5524_BAD_RANGE = (400, 1023)

def generate_fresh_row():
    """
    Generates a 'Fresh' (Output=1) data row.
    Fresh food characteristics:
    - Low gas concentration on all sensors
    - MQ135: Clean air, low NH3/pollutants
    - MQ3: Low alcohol vapor
    - MiCS-5524: Low multi-gas concentration
    """
    
    # MQ135 Air Quality Sensor - Fresh food produces clean readings
    # Low values indicate good air quality, minimal spoilage gases
    mq135_base = np.random.uniform(MQ135_FRESH_RANGE[0], MQ135_FRESH_RANGE[1])
    mq135_analog = int(np.clip(np.random.normal(loc=mq135_base, scale=20), 
                               MQ135_FRESH_RANGE[0], MQ135_FRESH_RANGE[1]))
    
    # MQ3 Alcohol Sensor - Fresh food has minimal alcohol/fermentation
    mq3_base = np.random.uniform(MQ3_FRESH_RANGE[0], MQ3_FRESH_RANGE[1])
    mq3_analog = int(np.clip(np.random.normal(loc=mq3_base, scale=20), 
                             MQ3_FRESH_RANGE[0], MQ3_FRESH_RANGE[1]))
    
    # Fermion MiCS-5524 MEMS Gas Sensor - Low multi-gas detection
    mics5524_base = np.random.uniform(MICS5524_FRESH_RANGE[0], MICS5524_FRESH_RANGE[1])
    mics5524_analog = int(np.clip(np.random.normal(loc=mics5524_base, scale=20), 
                                  MICS5524_FRESH_RANGE[0], MICS5524_FRESH_RANGE[1]))

    return [
        mq135_analog,
        mq3_analog,
        mics5524_analog,
        1  # Fresh
    ]

def generate_bad_row():
    """
    Generates a 'Bad' (Output=0) data row.
    Bad/Spoiled food characteristics:
    - High gas concentration on all sensors
    - MQ135: High NH3, pollutants from decomposition
    - MQ3: High alcohol from fermentation
    - MiCS-5524: High multi-gas from spoilage
    
    We create 3 types of spoilage patterns:
    1. Fermentation-dominant (60%) - Very high MQ3 + elevated others
    2. Decomposition-dominant (30%) - Very high MQ135 + elevated others
    3. Advanced spoilage (10%) - All sensors very high
    """
    
    rand_type = np.random.rand()
    
    # Type 1 (60% of bad data): Fermentation-Dominant Spoilage
    # Primary indicator: High alcohol (MQ3)
    if rand_type < 0.60:
        # Very high MQ3 - fermentation produces lots of alcohol vapor
        mq3_base = np.random.uniform(600, MQ3_BAD_RANGE[1])
        mq3_analog = int(np.clip(np.random.normal(loc=mq3_base, scale=30), 
                                 550, MQ3_BAD_RANGE[1]))
        
        # Moderate to high MQ135 - some decomposition byproducts
        mq135_base = np.random.uniform(450, 750)
        mq135_analog = int(np.clip(np.random.normal(loc=mq135_base, scale=30), 
                                   MQ135_BAD_RANGE[0], 800))
        
        # Moderate to high MiCS-5524 - detects various fermentation gases
        mics5524_base = np.random.uniform(500, 800)
        mics5524_analog = int(np.clip(np.random.normal(loc=mics5524_base, scale=30), 
                                      450, 850))

    # Type 2 (30% of bad data): Decomposition-Dominant Spoilage
    # Primary indicator: High ammonia/pollutants (MQ135)
    elif rand_type < 0.90:
        # Very high MQ135 - protein breakdown produces NH3
        mq135_base = np.random.uniform(700, MQ135_BAD_RANGE[1])
        mq135_analog = int(np.clip(np.random.normal(loc=mq135_base, scale=40), 
                                   650, MQ135_BAD_RANGE[1]))
        
        # Moderate MQ3 - some fermentation occurs alongside decomposition
        mq3_base = np.random.uniform(400, 700)
        mq3_analog = int(np.clip(np.random.normal(loc=mq3_base, scale=35), 
                                 MQ3_BAD_RANGE[0], 750))
        
        # High MiCS-5524 - detects H2, CO, CH4 from decomposition
        mics5524_base = np.random.uniform(600, 900)
        mics5524_analog = int(np.clip(np.random.normal(loc=mics5524_base, scale=35), 
                                      550, 950))

    # Type 3 (10% of bad data): Advanced/Severe Spoilage
    # All sensors show very high readings - food is severely spoiled
    else:
        # Very high MQ135 - severe decomposition
        mq135_base = np.random.uniform(800, MQ135_BAD_RANGE[1])
        mq135_analog = int(np.clip(np.random.normal(loc=mq135_base, scale=40), 
                                   750, MQ135_BAD_RANGE[1]))
        
        # Very high MQ3 - severe fermentation
        mq3_base = np.random.uniform(750, MQ3_BAD_RANGE[1])
        mq3_analog = int(np.clip(np.random.normal(loc=mq3_base, scale=40), 
                                 700, MQ3_BAD_RANGE[1]))
        
        # Very high MiCS-5524 - maximum gas concentration
        mics5524_base = np.random.uniform(800, MICS5524_BAD_RANGE[1])
        mics5524_analog = int(np.clip(np.random.normal(loc=mics5524_base, scale=40), 
                                      750, MICS5524_BAD_RANGE[1]))

    return [
        mq135_analog,
        mq3_analog,
        mics5524_analog,
        0  # Bad/Spoiled
    ]

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