import csv
import random
import numpy as np

# --- Configuration ---
NUM_ROWS = 100000
FRESH_ROWS = NUM_ROWS // 2
BAD_ROWS = NUM_ROWS - FRESH_ROWS
OUTPUT_FILENAME = 'food_freshness_dataset.csv'
HEADER = [
    'MQ135_Analog',         # MQ135 NH3 Sensor (0-15 ppm range)
    'MQ3_Analog',           # CO2 Sensor (500-1200 ppm range)
    'MiCS5524_Analog',      # MiCS-5524 CH4 Methane Sensor (200-600 ppm range)
    'Output',               # 1=Fresh, 0=Bad
    'RSL_Hours'             # Remaining Shelf Life in hours (0-168)
]

# --- Sensor Constraints (PPM readings) ---
# Updated based on actual gas concentration thresholds

# MQ135 NH3 (Ammonia) Sensor
# Detects: NH3 from protein decomposition
# Safe: 0-3 ppm, Going bad: 3-6 ppm, Spoiled: 6+ ppm
MQ135_NH3_FRESH_RANGE = (0.0, 3.0)      # Safe zone
MQ135_NH3_BAD_RANGE = (6.0, 15.0)       # Spoiled zone

# CO2 (Carbon Dioxide) Sensor
# Detects: CO2 from respiration and decomposition
# Safe: 500-700 ppm, Going bad: 800-900 ppm, Spoiled: 900+ ppm
CO2_FRESH_RANGE = (500, 700)            # Safe zone
CO2_BAD_RANGE = (900, 1200)             # Spoiled zone

# MiCS-5524 CH4 (Methane) Sensor
# Detects: CH4 from anaerobic decomposition
# Safe: 200-300 ppm, Going bad: 300-400 ppm, Spoiled: 400+ ppm
MICS5524_CH4_FRESH_RANGE = (200, 300)   # Safe zone
MICS5524_CH4_BAD_RANGE = (400, 600)     # Spoiled zone

def generate_fresh_row():
    """
    Generates a 'Fresh' (Output=1) data row.
    Fresh food characteristics:
    - Low NH3 (0-3 ppm) - minimal protein decomposition
    - Normal CO2 (500-700 ppm) - normal respiration
    - Low CH4 (200-300 ppm) - no anaerobic decomposition
    - RSL: 24-168 hours (1-7 days remaining)
    
    RSL Correlation: Lower gas concentrations = longer shelf life
    """
    
    # MQ135 NH3 Sensor - Fresh food has minimal ammonia
    # Safe zone: 0-3 ppm (protein decomposition minimal)
    nh3_base = np.random.uniform(MQ135_NH3_FRESH_RANGE[0], MQ135_NH3_FRESH_RANGE[1])
    nh3_ppm = np.clip(np.random.normal(loc=nh3_base, scale=0.3), 
                      MQ135_NH3_FRESH_RANGE[0], MQ135_NH3_FRESH_RANGE[1])
    
    # CO2 Sensor - Fresh food has normal CO2 levels
    # Safe zone: 500-700 ppm (normal respiration)
    co2_base = np.random.uniform(CO2_FRESH_RANGE[0], CO2_FRESH_RANGE[1])
    co2_ppm = np.clip(np.random.normal(loc=co2_base, scale=20), 
                      CO2_FRESH_RANGE[0], CO2_FRESH_RANGE[1])
    
    # MiCS-5524 CH4 Sensor - Fresh food has low methane
    # Safe zone: 200-300 ppm (no anaerobic decomposition)
    ch4_base = np.random.uniform(MICS5524_CH4_FRESH_RANGE[0], MICS5524_CH4_FRESH_RANGE[1])
    ch4_ppm = np.clip(np.random.normal(loc=ch4_base, scale=10), 
                      MICS5524_CH4_FRESH_RANGE[0], MICS5524_CH4_FRESH_RANGE[1])

    # Calculate RSL (Remaining Shelf Life) based on gas concentrations
    # Lower gas values = fresher food = longer shelf life
    # Normalize sensor values to 0-1 range within fresh range
    nh3_norm = (nh3_ppm - MQ135_NH3_FRESH_RANGE[0]) / (MQ135_NH3_FRESH_RANGE[1] - MQ135_NH3_FRESH_RANGE[0])
    co2_norm = (co2_ppm - CO2_FRESH_RANGE[0]) / (CO2_FRESH_RANGE[1] - CO2_FRESH_RANGE[0])
    ch4_norm = (ch4_ppm - MICS5524_CH4_FRESH_RANGE[0]) / (MICS5524_CH4_FRESH_RANGE[1] - MICS5524_CH4_FRESH_RANGE[0])
    
    # Average normalized value (0 = very fresh, 1 = at threshold)
    avg_freshness = (nh3_norm + co2_norm + ch4_norm) / 3.0
    
    # Map to RSL: 0 freshness = 168 hours (7 days), 1 freshness = 24 hours (1 day)
    # Inverse relationship: lower sensor values = higher RSL
    base_rsl = 168 - (avg_freshness * (168 - 24))
    
    # Add some randomness (±12 hours)
    rsl_hours = int(np.clip(base_rsl + np.random.uniform(-12, 12), 24, 168))

    return [
        round(nh3_ppm, 2),
        int(co2_ppm),
        int(ch4_ppm),
        1,  # Fresh
        rsl_hours
    ]

def generate_bad_row():
    """
    Generates a 'Bad' (Output=0) data row.
    Bad/Spoiled food characteristics:
    - High NH3 (6+ ppm) - protein decomposition
    - High CO2 (900+ ppm) - excessive respiration/decomposition
    - High CH4 (400+ ppm) - anaerobic decomposition
    - RSL: 0-23 hours (less than 1 day remaining)
    
    We create 3 types of spoilage patterns:
    1. Protein decomposition-dominant (40%) - Very high NH3
    2. Anaerobic decomposition-dominant (40%) - Very high CH4 + elevated CO2
    3. Advanced spoilage (20%) - All gases very high
    
    RSL Correlation: Higher gas concentrations = shorter shelf life
    """
    
    rand_type = np.random.rand()
    
    # Type 1 (40% of bad data): Protein Decomposition-Dominant
    # Primary indicator: High NH3 from protein breakdown
    if rand_type < 0.40:
        # Very high NH3 - protein breakdown produces ammonia
        nh3_base = np.random.uniform(8.0, MQ135_NH3_BAD_RANGE[1])
        nh3_ppm = np.clip(np.random.normal(loc=nh3_base, scale=0.8), 
                          6.5, MQ135_NH3_BAD_RANGE[1])
        
        # Elevated CO2 - decomposition produces CO2
        co2_base = np.random.uniform(900, 1000)
        co2_ppm = np.clip(np.random.normal(loc=co2_base, scale=25), 
                          850, 1050)
        
        # Moderate CH4 - some anaerobic activity
        ch4_base = np.random.uniform(350, 450)
        ch4_ppm = np.clip(np.random.normal(loc=ch4_base, scale=15), 
                          300, 500)

    # Type 2 (40% of bad data): Anaerobic Decomposition-Dominant
    # Primary indicator: High CH4 from anaerobic decomposition
    elif rand_type < 0.80:
        # Very high CH4 - anaerobic bacteria produce methane
        ch4_base = np.random.uniform(450, MICS5524_CH4_BAD_RANGE[1])
        ch4_ppm = np.clip(np.random.normal(loc=ch4_base, scale=20), 
                          400, MICS5524_CH4_BAD_RANGE[1])
        
        # High CO2 - anaerobic decomposition produces CO2
        co2_base = np.random.uniform(950, 1150)
        co2_ppm = np.clip(np.random.normal(loc=co2_base, scale=30), 
                          900, 1200)
        
        # Moderate NH3 - some protein breakdown
        nh3_base = np.random.uniform(6.0, 10.0)
        nh3_ppm = np.clip(np.random.normal(loc=nh3_base, scale=0.6), 
                          5.5, 11.0)

    # Type 3 (20% of bad data): Advanced/Severe Spoilage
    # All gases show very high readings - food is severely spoiled
    else:
        # Very high NH3 - severe protein decomposition
        nh3_base = np.random.uniform(10.0, MQ135_NH3_BAD_RANGE[1])
        nh3_ppm = np.clip(np.random.normal(loc=nh3_base, scale=1.0), 
                          9.0, MQ135_NH3_BAD_RANGE[1])
        
        # Very high CO2 - maximum decomposition activity
        co2_base = np.random.uniform(1000, CO2_BAD_RANGE[1])
        co2_ppm = np.clip(np.random.normal(loc=co2_base, scale=35), 
                          950, CO2_BAD_RANGE[1])
        
        # Very high CH4 - maximum anaerobic activity
        ch4_base = np.random.uniform(500, MICS5524_CH4_BAD_RANGE[1])
        ch4_ppm = np.clip(np.random.normal(loc=ch4_base, scale=25), 
                          450, MICS5524_CH4_BAD_RANGE[1])

    # Calculate RSL (Remaining Shelf Life) for bad food
    # Higher gas values = more spoiled = shorter shelf life
    # Normalize gas values to 0-1 range within bad range
    nh3_norm = (nh3_ppm - MQ135_NH3_BAD_RANGE[0]) / (MQ135_NH3_BAD_RANGE[1] - MQ135_NH3_BAD_RANGE[0])
    co2_norm = (co2_ppm - CO2_BAD_RANGE[0]) / (CO2_BAD_RANGE[1] - CO2_BAD_RANGE[0])
    ch4_norm = (ch4_ppm - MICS5524_CH4_BAD_RANGE[0]) / (MICS5524_CH4_BAD_RANGE[1] - MICS5524_CH4_BAD_RANGE[0])
    
    # Average normalized value (0 = just crossed threshold, 1 = completely spoiled)
    avg_spoilage = (nh3_norm + co2_norm + ch4_norm) / 3.0
    
    # Map to RSL: 0 spoilage = 23 hours, 1 spoilage = 0 hours
    # Inverse relationship: higher sensor values = lower RSL
    base_rsl = 23 - (avg_spoilage * 23)
    
    # Add some randomness (±3 hours)
    rsl_hours = int(np.clip(base_rsl + np.random.uniform(-3, 3), 0, 23))

    return [
        round(nh3_ppm, 2),
        int(co2_ppm),
        int(ch4_ppm),
        0,  # Bad/Spoiled
        rsl_hours
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