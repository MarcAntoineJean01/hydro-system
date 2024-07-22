# water_flow_sensor.py

import nakama_utils
import RPi.GPIO as GPIO
import time, sys
import hydroponic_db
import nakama_store

water_flow_count = 0
start_counter = 1
class water_flow_sensor:

	def __init__(self, prog_id):
		self.program_id = prog_id
		if not hydroponic_db.table_exists('water_flow_readings'):
			self.create_water_flow_readings_table()
		self.water_flow_pin = nakama_store.WATER_FLOW_PIN
		self.last_flow_readings = []
		try:
			nakama_utils.update_instance_startup_state(self.program_id, 'water_flow_sensor', nakama_store.PENDING)
			nakama_utils.log_info("SETTING UP WATER FLOW SENSOR", True)
			GPIO.setup(self.water_flow_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
			global start_counter
			global water_flow_count

			def countPulse(channel):
				global water_flow_count
				if start_counter == 1:
					water_flow_count = water_flow_count+1

			GPIO.add_event_detect(self.water_flow_pin, GPIO.FALLING, callback=countPulse)
			nakama_utils.log_info("WATER FLOW SENSOR READY", True)
			nakama_utils.update_instance_startup_state(self.program_id, 'water_flow_sensor', nakama_store.SUCCESS)
		except Exception  as e:
			mess = "COULDN'T SETUP WATER FLOW SENSOR  -- " + str(e)
			nakama_utils.log_error('water_flow_sensor.init', mess)
			nakama_utils.update_instance_startup_state(self.program_id, 'water_flow_sensor', nakama_store.FAILED)

	def read_flow(self, count, start_counter):
		try:
			start_counter = 1
			time.sleep(0.5)
			start_counter = 0
			flow = (count / 7.5) # Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
			# nakama_utils.log_info("The flow is: %.3f Liter/min" % (flow))
			count = 0
			time.sleep(1)
			return flow
		except Exception  as e:
			mess = "COULDN'T READ WATER FLOW  -- " + str(e)
			nakama_utils.log_error('water_flow_sensor.read_flow', mess)

	def read(self):
		fl = self.read_flow(water_flow_count, start_counter)
		self.last_flow_readings.append(fl)
		if len(self.last_flow_readings) > 20:
			self.last_flow_readings = self.last_flow_readings[-20:]
		self.last_reading_time = nakama_utils.now()
		return fl

	def read_last_reading_time(self):
		if hasattr(self, 'last_reading_time'):
			return self.last_reading_time
		else:
			return None

	def read_last_flow(self):
		if len(self.last_flow_readings) > 0:
			return round(self.last_flow_readings[-1], 3)
		else:
			return None

	def read_last_readings(self):
		return self.last_flow_readings

	def create_water_flow_readings_table(self):
		hydroponic_db.create_table("CREATE TABLE water_flow_readings ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  reading_date DATETIME NOT NULL,"
			"  reading_value float(10,8) NOT NULL"
			") ENGINE='InnoDB'")