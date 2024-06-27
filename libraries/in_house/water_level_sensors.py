# water_level_sensors.py

import nakama_utils
import threading
import time
import RPi.GPIO as GPIO
import hydroponic_db
import nakama_store

class water_level_sensors:

	def __init__(self,  prog_id):
		self.program_id = prog_id
		if not hydroponic_db.table_exists('bottom_water_level_state'):
			self.create_bottom_water_level_state_table()
		if not hydroponic_db.table_exists('top_water_level_state'):
			self.create_top_water_level_state_table()
		nakama_utils.set_emergency_stop_water_level_loops(False, self.program_id)
		nakama_utils.set_emergency_stop_pump(False, self.program_id)
		nakama_utils.set_emergency_stop_capacity(False, self.program_id)
		self.water_level_bottom_pin = nakama_store.WATER_LEVEL_BOTTOM_PIN
		self.water_level_top_pin = nakama_store.WATER_LEVEL_TOP_PIN
		nakama_utils.log_info("SETTING UP BOTTOM LEVEL SENSOR", True)
		GPIO.setup(self.water_level_bottom_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		nakama_utils.log_info("SETTING UP TOP LEVEL SENSOR", True)
		GPIO.setup(self.water_level_top_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		nakama_utils.log_info("STARTING BOTTOM LEVEL SENSOR", True)
		self.start_bottom_water_level_monitor()
		nakama_utils.log_info("STARTING TOP LEVEL SENSOR", True)
		self.start_top_water_level_monitor()

	def bottom_water_level_read(self):
		try:
			if(GPIO.input(self.water_level_bottom_pin) == 1):
				return False
			else:
				return True
		except Exception  as e:
			mess = "COULDN'T READ BOTTOM WATER LEVEL " + str(e)
			nakama_utils.log_error('water_level_sensors.bottom_water_level_read', mess)

	def top_water_level_read(self):
		try:
			if(GPIO.input(self.water_level_top_pin) == 1):
				return False
			else:
				return True
		except Exception  as e:
			mess = "COULDN'T READ TOP WATER LEVEL " + str(e)
			nakama_utils.log_error('water_level_sensors.top_water_level_read', mess)

	def bottom_water_level_loop(self):
		try:
			while not nakama_utils.emergency_stop_water_level_loops(self.program_id):
				if(GPIO.input(self.water_level_bottom_pin) != 1):
					# nakama_utils.log_info("BOTTOM SENSOR ON")
					time.sleep(1)
				else:
					nakama_utils.set_emergency_stop_pump(True, self.program_id)
					nakama_utils.log_warning("water_level_sensors.bottom_water_level_loop", "BOTTOM SENSOR OFF, CALLED MAIN PUMP EMERGENCY STOP", True)
				time.sleep(4)
			else:
				nakama_utils.log_info("<<<bottom_water_level_loop is finished>>>")
		except Exception  as e:
			mess = "COULDN'T START BOTTOM WATER LEVEL LOOP " + str(e)
			nakama_utils.log_error('water_level_sensors.bottom_water_level_loop', mess)

	def top_water_level_loop(self):
		try:
			while not nakama_utils.emergency_stop_water_level_loops(self.program_id):
				if(GPIO.input(self.water_level_top_pin) == 1):
					# nakama_utils.log_info("TOP SENSOR OFF")
					time.sleep(1)
				else:
					nakama_utils.set_emergency_stop_capacity(True, self.program_id)
					nakama_utils.log_warning("water_level_sensors.top_water_level_loop", "TOP SENSOR ON, CALLED MAX CAPACITY EMERGENCY STOP", True)
				time.sleep(4)
			else:
				nakama_utils.log_info("<<<top_water_level_loop is finished>>>")
		except Exception  as e:
			mess = "COULDN'T START TOP WATER LEVEL LOOP " + str(e)
			nakama_utils.log_error('water_level_sensors.top_water_level_loop', mess)

	def start_bottom_water_level_monitor(self):
		self.bottom_water_level_monitor = threading.Thread(name='bottom_water_level_loop', target=self.bottom_water_level_loop)
		self.bottom_water_level_monitor.start()
		nakama_utils.log_info("STARTED BOTTOM WATER LEVEL MONITOR LOOP", True)

	def start_top_water_level_monitor(self):
		self.top_water_level_monitor = threading.Thread(name='top_water_level_loop', target=self.top_water_level_loop)
		self.top_water_level_monitor.start()
		nakama_utils.log_info("STARTED TOP WATER LEVEL MONITOR LOOP", True)

	def get_top_water_level_monitor(self):
		return self.top_water_level_monitor

	def get_bottom_water_level_monitor(self):
		return self.bottom_water_level_monitor

	def create_bottom_water_level_state_table(self):
		hydroponic_db.create_table("CREATE TABLE bottom_water_level_state ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  state_date DATETIME NOT NULL,"
			"  state_value BOOLEAN NOT NULL"
			") ENGINE='InnoDB'")

	def create_top_water_level_state_table(self):
		hydroponic_db.create_table("CREATE TABLE top_water_level_state ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  state_date DATETIME NOT NULL,"
			"  state_value BOOLEAN NOT NULL"
			") ENGINE='InnoDB'")