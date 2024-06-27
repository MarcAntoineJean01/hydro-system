# nakama_store.py

# nutrient pumps pins
MICRO_STEPS_PINS = (14, 15, 18)
DIRECTION = 20
STEP = 21

# switches and relays pins
MAIN_PUMP_RELAY_PIN = 16
GROWLIGHTS_RELAY_PIN = 12
PUMP_1_RELAY_PIN = 26
PUMP_2_RELAY_PIN = 19
PUMP_3_RELAY_PIN = 13
PUMP_4_RELAY_PIN = 6

# GPIO PINS
WATER_FLOW_PIN = 22
WATER_LEVEL_BOTTOM_PIN = 17
WATER_LEVEL_TOP_PIN = 27

# states
PENDING = 'pending'
SUCCESS = 'success'
FAILED = 'failed'

# target values
TARGET_PH = (5.5, 6.5)

# first roots THEN first true leaves THEN start growing
PHASE_1_VALUES = {
	"EC": (0.9, 1.2),
	"NUTRIENT_A": (9, 13), # range of ml per 10L of water
	"NUTRIENT_B": (9, 13) # range of ml per 10L of water
}

# start flowering phase
PHASE_2_VALUES = {
	"EC": (1.2, 1.7),
	"NUTRIENT_A": (13, 18), # range of ml per 10L of water
	"NUTRIENT_B": (13, 18) # range of ml per 10L of water
}

# mid flowering phase
PHASE_3_VALUES = {
	"EC": (1.7, 1.9),
	"NUTRIENT_A": (18, 19), # range of ml per 10L of water
	"NUTRIENT_B": (18, 19) # range of ml per 10L of water
}

# last flowering phase, seeding
PHASE_4_VALUES = {
	"EC": (1.2, 1.5),
	"NUTRIENT_A": (13, 16), # range of ml per 10L of water
	"NUTRIENT_B": (13, 16) # range of ml per 10L of water
}

PROGRAMS = {
	"test": ['read_values'],
	"water_baseline_test": ['run_growlights', 'create_water_batch', 'create_baseline'],
	"water_check": ['run_main_pump', 'read_values'],
	"water_batch_setup": ['run_main_pump', 'create_water_batch', 'create_baseline'],
	"phase_1": ['run_main_pump', 'run_growlights', 'read_values'],
	"phase_2": ['run_main_pump', 'run_growlights', 'read_values'],
	"phase_3": ['run_main_pump', 'run_growlights', 'read_values'],
	"phase_4": ['run_main_pump', 'run_growlights', 'read_values']
}