import sys
sys.path.append('libraries/in_house')
if sys.platform == "linux" or sys.platform == "linux2":
	# linux
	pass
elif sys.platform == "darwin" or sys.platform == "win32":
	# OS X or # Windows...
	import nakama_mocker
	GPIO = nakama_mocker.Fake_GPIO()
elif sys.platform == "RASP_PI":
	import RPi.GPIO as GPIO
import nakama_utils
import hydroponic_db
import nakama_store

class switches:
	def __init__(self, prog_id):
		self.program_id = prog_id
		if not hydroponic_db.table_exists('main_pump_state'):
			self.create_main_pump_state_table()
		if not hydroponic_db.table_exists('growlights_state'):
			self.create_growlights_state_table()
		# main water pump
		self.main_pump_relay_pin = nakama_store.MAIN_PUMP_RELAY_PIN

		# main lights
		self.growlights_relay_pin = nakama_store.GROWLIGHTS_RELAY_PIN

		# nutrient pumps
		self.pump_1_relay_pin = nakama_store.PUMP_1_RELAY_PIN
		self.pump_2_relay_pin = nakama_store.PUMP_2_RELAY_PIN
		self.pump_3_relay_pin = nakama_store.PUMP_3_RELAY_PIN
		self.pump_4_relay_pin = nakama_store.PUMP_4_RELAY_PIN

		nakama_utils.update_instance_startup_state(self.program_id, 'growlights', nakama_store.PENDING)
		nakama_utils.update_instance_startup_state(self.program_id, 'main_pump', nakama_store.PENDING)
		nakama_utils.update_instance_startup_state(self.program_id, 'nutrient_pumps', nakama_store.PENDING)

		self.setup_growlights()
		if nakama_utils.get_instance_startup_state(self.program_id, 'water_flow_sensor') == nakama_store.SUCCESS and not nakama_utils.emergency_stop_pump(self.program_id):
			self.setup_main_pump()
		else:
			head_mess = "FAILED TO SETUP MAIN PUMP. MISSING DEPENDENCY "
			water_flow_mess = "program_state.water_flow_sensor_state: '{}' | ".format(nakama_utils.get_instance_startup_state(self.program_id, 'water_flow_sensor'))
			water_level_mess = "nakama_utils.emergency_stop_pump(): '" + str(nakama_utils.emergency_stop_pump(self.program_id)) + "' "
			mess = head_mess + water_flow_mess + water_level_mess
			nakama_utils.update_instance_startup_state(self.program_id, 'main_pump', nakama_store.FAILED)
			nakama_utils.log_warning('switches.init', mess, True)
		self.setup_nutrient_pumps()

	def setup_growlights(self):
		try:
			nakama_utils.log_info("SETTING UP GROW LIGHTS RELAY")
			GPIO.setup(self.growlights_relay_pin, GPIO.OUT)
			nakama_utils.log_info('GROW LIGHTS RELAY READY')
			GPIO.output(self.growlights_relay_pin, GPIO.HIGH)
			nakama_utils.log_info('GROW LIGHTS POWER RELAY OFF')
			nakama_utils.update_instance_startup_state(self.program_id, 'growlights', nakama_store.SUCCESS)
		except Exception  as e:
			nakama_utils.update_instance_startup_state(self.program_id, 'growlights', nakama_store.FAILED)
			mess = "COULDN'T SETUP LIGHT SWITCH -- " + str(e)
			nakama_utils.log_error('switches.setup_growlights', mess)
	
	def setup_main_pump(self):
		try:
			nakama_utils.log_info('SETTING UP MAIN PUMP RELAY')
			GPIO.setup(self.main_pump_relay_pin, GPIO.OUT)
			nakama_utils.log_info('MAIN PUMP RELAY READY')
			GPIO.output(self.main_pump_relay_pin, GPIO.HIGH)
			nakama_utils.log_info('MAIN PUMP POWER RELAY OFF')
			nakama_utils.update_instance_startup_state(self.program_id, 'main_pump', nakama_store.SUCCESS)
		except Exception  as e:
			nakama_utils.update_instance_startup_state(self.program_id, 'main_pump', nakama_store.FAILED)
			mess = "COULDN'T MAIN PUMP SWITCH -- " + str(e)
			nakama_utils.log_error('switches.setup_main_pump', mess)
	
	def setup_nutrient_pumps(self):
		try:
			nakama_utils.log_info('SETTING UP PUMP 1 POWER RELAY')
			GPIO.setup(self.pump_1_relay_pin, GPIO.OUT)
			nakama_utils.log_info('PUMP 1 POWER RELAY OFF')
			GPIO.output(self.pump_1_relay_pin, GPIO.HIGH)
			nakama_utils.log_info('SETTING UP PUMP 2 POWER RELAY')
			GPIO.setup(self.pump_2_relay_pin, GPIO.OUT)
			nakama_utils.log_info('PUMP 2 POWER RELAY OFF')
			GPIO.output(self.pump_2_relay_pin, GPIO.HIGH)
			nakama_utils.log_info('SETTING UP PUMP 3 POWER RELAY')
			GPIO.setup(self.pump_3_relay_pin, GPIO.OUT)
			nakama_utils.log_info('PUMP 3 POWER RELAY OFF')
			GPIO.output(self.pump_3_relay_pin, GPIO.HIGH)
			nakama_utils.log_info('SETTING UP PUMP 4 POWER RELAY')
			GPIO.setup(self.pump_4_relay_pin, GPIO.OUT)
			nakama_utils.log_info('PUMP 4 POWER RELAY OFF')
			GPIO.output(self.pump_4_relay_pin, GPIO.HIGH)
			nakama_utils.update_instance_startup_state(self.program_id, 'nutrient_pumps', nakama_store.SUCCESS)
		except Exception  as e:
			nakama_utils.update_instance_startup_state(self.program_id, 'nutrient_pumps', nakama_store.FAILED)
			mess = "COULDN'T SETUP NUTRIENT PUMPS SWITCH -- '{}'".format(e)
			nakama_utils.log_error('switches.nutrient_pumps_setup', mess)

	def switch_main_pump(self, state):
		if state and nakama_utils.get_instance_startup_state(self.program_id, 'water_flow_sensor') == nakama_store.SUCCESS and not nakama_utils.emergency_stop_pump(self.program_id) and nakama_utils.get_instance_startup_state(self.program_id, 'main_pump') == nakama_store.SUCCESS:
			try:
				st = GPIO.LOW
				GPIO.output(self.main_pump_relay_pin, st)
				nakama_utils.log_info("MAIN PUMP POWER RELAY 'ON'")
			except Exception  as e:
				mess = "COULDN'T SWITCH 'ON' MAIN PUMP -- {}".format(e)
				nakama_utils.log_error('switches.switch_main_pump', mess)
		if not state:
			try:
				st = GPIO.HIGH
				GPIO.output(self.main_pump_relay_pin, st)
				nakama_utils.log_info("MAIN PUMP POWER RELAY 'OFF'")
			except Exception  as e:
				mess = "COULDN'T SWITCH 'OFF' MAIN PUMP -- {}".format(e)
				nakama_utils.log_error('switches.switch_main_pump', mess)
		else:
			if nakama_utils.get_instance_startup_state(self.program_id, 'water_flow_sensor') != nakama_store.SUCCESS:
				nakama_utils.log_warning('switches.switch_main_pump', "FAILED TO SWITCH MAIN PUMP - program_state.water_flow_sensor_state: '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'water_flow_sensor')), True)
			if nakama_utils.emergency_stop_pump(self.program_id):
				nakama_utils.log_warning('switches.switch_main_pump', "FAILED TO SWITCH MAIN PUMP - nakama_utils.emergency_stop_pump(): '{}'".format(nakama_utils.emergency_stop_pump(self.program_id)), True)
			if nakama_utils.get_instance_startup_state(self.program_id, 'main_pump') != nakama_store.SUCCESS:
				nakama_utils.log_warning('switches.switch_main_pump', "FAILED TO SWITCH MAIN PUMP - self.main_pump_state: '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'main_pump')), True)

	def switch_growlights(self, state):
		try:
			st = GPIO.LOW if state else GPIO.HIGH
			GPIO.output(self.growlights_relay_pin, st)
			nakama_utils.log_info('GROWLIGHTS POWER RELAY ' + ("ON" if state else "OFF"))
		except Exception  as e:
			mess = "COULDN'T SWITCH " + ("ON" if state else "OFF") + " GROWLIGHTS -- " + str(e)
			nakama_utils.log_error('switches.switch_growlights', mess)

	def switch_nutrient_pump_1(self, state):
		try:
			st = GPIO.LOW if state else GPIO.HIGH
			GPIO.output(self.pump_1_relay_pin, st)
			nakama_utils.log_info('NUTRIENT PUMP 1 POWER RELAY ' + ("ON" if state else "OFF"))
		except Exception  as e:
			mess = "COULDN'T SWITCH " + ("ON" if state else "OFF") + " NUTRIENT PUMP 1 -- " + str(e)
			nakama_utils.log_error('switches.switch_nutrient_pump_1', mess)

	def switch_nutrient_pump_2(self, state):
		try:
			st = GPIO.LOW if state else GPIO.HIGH
			GPIO.output(self.pump_2_relay_pin, st)
			nakama_utils.log_info('NUTRIENT PUMP 2 POWER RELAY ' + ("ON" if state else "OFF"))
		except Exception  as e:
			mess = "COULDN'T SWITCH " + ("ON" if state else "OFF") + " NUTRIENT PUMP 2 -- " + str(e)
			nakama_utils.log_error('switches.switch_nutrient_pump_2', mess)

	def switch_nutrient_pump_3(self, state):
		try:
			st = GPIO.LOW if state else GPIO.HIGH
			GPIO.output(self.pump_3_relay_pin, st)
			nakama_utils.log_info('NUTRIENT PUMP 3 POWER RELAY ' + ("ON" if state else "OFF"))
		except Exception  as e:
			mess = "COULDN'T SWITCH " + ("ON" if state else "OFF") + " NUTRIENT PUMP 3 -- " + str(e)
			nakama_utils.log_error('switches.switch_nutrient_pump_3', mess)

	def switch_nutrient_pump_4(self, state):
		try:
			st = GPIO.LOW if state else GPIO.HIGH
			GPIO.output(self.pump_4_relay_pin, st)
			nakama_utils.log_info('NUTRIENT PUMP 4 POWER RELAY ' + ("ON" if state else "OFF"))
		except Exception  as e:
			mess = "COULDN'T SWITCH " + ("ON" if state else "OFF") + " NUTRIENT PUMP 4 -- " + str(e)
			nakama_utils.log_error('switches.switch_nutrient_pump_4', mess)

	def create_main_pump_state_table(self):
		hydroponic_db.create_table("CREATE TABLE main_pump_state ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  state_date DATETIME NOT NULL,"
			"  state_value BOOLEAN NOT NULL"
			") ENGINE='InnoDB'")

	def create_growlights_state_table(self):
		hydroponic_db.create_table("CREATE TABLE growlights_state ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  state_date DATETIME NOT NULL,"
			"  state_value BOOLEAN NOT NULL"
			") ENGINE='InnoDB'")
