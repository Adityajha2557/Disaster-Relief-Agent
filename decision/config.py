
# DRRAA Simulation Configuration
# All values below are illustrative assumptions.

# Resource requirement per person per day
DAILY_REQUIREMENTS = {
    "food": 0.5,       # kg per person
    "water": 3.0,      # litres per person
    "medicine": 0.05   # kg per person
}

# Duration of relief supply
RELIEF_DAYS = 1

# Conversion of dataset inventory units into kg
# Water: 1 litre is approximated as 1 kg.
# These conversions are simulation assumptions.
UNIT_WEIGHT_KG = {
    "food": 1.0,
    "water": 1.0,
    "medicine": 0.1
}

# Initial inventory generated for each relief camp
# These are assumed simulation stock levels, not dataset values.
CAMP_INITIAL_STOCK_KG = {
    "food": 10000,
    "water": 20000,
    "medicine": 2000
}

# One vehicle can carry at most its recorded capacity.
VEHICLE_CAPACITY_BUFFER = 1.0
