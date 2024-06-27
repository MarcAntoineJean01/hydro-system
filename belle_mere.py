import sys
sys.path.append('libraries/in_house')
if sys.platform == "linux" or sys.platform == "linux2":
	# linux
	pass
elif sys.platform == "darwin" or sys.platform == "win32":
	# OS X or # Windows...
	import nakama_mocker
	GPIO = nakama_mocker.Fake_GPIO()
	ads1115_instance = nakama_mocker.Fake_ads1115_instance(1)
	i2c_instance = nakama_mocker.Fake_i2c_instance(1)
	lcd_screen = nakama_mocker.Fake_lcd_screen(i2c_instance, 1)
	water_flow_sensor = nakama_mocker.Fake_water_flow_sensor(1)
	water_level_sensors = nakama_mocker.Fake_water_level_sensors(1)
	water_temperature = nakama_mocker.Fake_water_temperature(1)
	water_ec_sensor = nakama_mocker.Fake_water_ec_sensor(ads1115_instance, 11, 1)
	water_ph_sensor = nakama_mocker.Fake_water_ph_sensor(ads1115_instance, 11, 1)
elif sys.platform == "RASP_PI":
	import RPi.GPIO as GPIO
	import ads1115_instance
	import i2c_instance
	import lcd_screen
	import water_ec_sensor
	import water_flow_sensor
	import water_level_sensors
	import water_ph_sensor
	import water_temperature
import nutrient_pumps_drivers
import switches
import nakama_utils
import time
import logging
import hydroponic_db
import nakama_store
import threading

class belle_mere:
	def __init__(self):
		if not hydroponic_db.db_exists(nakama_utils.get_locker_value("DATABASE")):
			self.create_hydro_database()
		if not hydroponic_db.table_exists('program_state'):
			self.create_program_state_table()
		if not hydroponic_db.table_exists('system_monitoring'):
			self.create_system_monitoring_table()
		if not hydroponic_db.table_exists('water_batch_baseline'):
			self.create_water_batch_baseline_table()
		if not hydroponic_db.table_exists('water_batch'):
			self.create_water_batch_table()
		self.instance_ready = False
		self.force_exit = False
		self.pump_running = False
		self.force_pause_pump = False
		self.growlights_running = False
		self.program_id = self.make_new_program_id()

	def main_setup(self):
		try:
			# must be run at the beggining of any program
			logging.basicConfig()
			logging.getLogger().setLevel(logging.INFO)
			GPIO.setmode(GPIO.BCM)
			self.ads1115_instance = ads1115_instance.ads1115_instance(self.program_id)
			self.i2c_instance = i2c_instance.i2c_instance(self.program_id)
			self.lcd_screen = lcd_screen.lcd_screen(self.i2c_instance, self.program_id)
			self.water_flow_sensor = water_flow_sensor.water_flow_sensor(self.program_id)
			self.water_level_sensors = water_level_sensors.water_level_sensors(self.program_id)
			self.switches = switches.switches(self.program_id)
			self.nutrient_pumps_drivers = nutrient_pumps_drivers.nutrient_pumps_drivers(self.switches, self.program_id)
			self.water_temperature = water_temperature.water_temperature(self.program_id)
			self.water_ec_sensor = water_ec_sensor.water_ec_sensor(self.ads1115_instance, self.water_temperature, self.program_id)
			self.water_ph_sensor = water_ph_sensor.water_ph_sensor(self.ads1115_instance, self.water_temperature, self.program_id)
			self.instance_ready = True
		except Exception as e:
			nakama_utils.log_error('belle_mere', e)
			nakama_utils.set_emergency_stop_water_level_loops(True, self.program_id)
			t = time.localtime()
			current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
			hydroponic_db.update_table("UPDATE program_state SET end_date = STR_TO_DATE('{}', '%d/%m/%Y-%T'), has_failed = TRUE WHERE id = {}".format(current_time, self.program_id))
			nakama_utils.log_warning("END OF PROGRAM", "Calling GPIO.cleanup()", True)
			GPIO.cleanup()
		finally:
			nakama_utils.log_info("END OF MAIN SETUP", True)

	def start_program(self, prog):
		try:
			sql = "UPDATE program_state SET program_name = '{}' WHERE id = {}".format(prog, self.program_id)
			nakama_utils.log_info("START OF PROGRAM '{}'".format(prog), True)
			hydroponic_db.update_table(sql)
			if prog in nakama_store.PROGRAMS.keys():
				for phase in nakama_store.PROGRAMS[prog]:
					self.run_program_phase(phase)
			else:
				raise Exception("belle_mere.start_program, Unknown program '{}'".format(prog))
		except Exception as e:
			nakama_utils.log_error('belle_mere.start_program', str(e))
			hydroponic_db.update_table("UPDATE program_state SET has_failed = TRUE WHERE id = {}".format(self.program_id))
		finally:
			nakama_utils.log_info("END OF PROGRAM '{}' BELLE MERE DONE".format(prog), True)
			nakama_utils.set_emergency_stop_water_level_loops(True, self.program_id)
			t = time.localtime()
			current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
			hydroponic_db.update_table("UPDATE program_state SET end_date = STR_TO_DATE('{}', '%d/%m/%Y-%T') WHERE id = {}".format(current_time, self.program_id))

	def run_program_phase(self, phase):
		nakama_utils.log_info("START OF PROGRAM-PHASE '{}'".format(phase), True)
		hydroponic_db.update_table("UPDATE program_state SET current_phase = '{}' WHERE id = {}".format(phase, self.program_id))
		try:
			if phase == 'run_main_pump':
				self.run_main_pump()
			elif phase == 'run_growlights':
				self.run_growlights()
			elif phase == 'create_water_batch':
				self.water_batch_id = self.create_water_batch_and_get_id()
			elif phase == 'create_baseline':
				nakama_utils.log_info("Starting baseline process for water batch with id: '{}'".format(self.water_batch_id))
				self.establish_water_baseline(self.water_batch_id)
				while (len(self.ec_readings) < 10 and len(self.ph_readings) < 10) and not self.force_exit:
					time.sleep(20)
				time.sleep(5)
			elif phase == 'read_values':
				while not self.force_exit:
					time.sleep(60)
					self.water_ec_sensor.read()
					self.water_ph_sensor.read()
			else:
				nakama_utils.log_warning('belle_mere.run_program', "program name phase not recognized: '{}'".format(phase), True)
		finally:
			nakama_utils.log_info("END OF PROGRAM-PHASE '{}'".format(phase))

	def run_calibration(self, prog):
		nakama_utils.log_info("START OF CALIBRATION '{}'".format(prog), True)
		try:
			if prog == 'calibrate_ph4':
				self.water_ph_sensor.calibration4()
			elif prog == 'calibrate_ph7':
				self.water_ph_sensor.calibration7()
			elif prog == 'calibrate_ec1413':
				self.water_ec_sensor.calibration1413()
			elif prog == 'calibrate_ec1288':
				self.water_ec_sensor.calibration1288()
			else:
				nakama_utils.log_warning('belle_mere.run_calibration', "calibration program name not recognized: '{}'".format(prog), True)
		finally:
			nakama_utils.log_info("END OF CALIBRATION '{}'".format(prog), True)

	def create_hydro_database(self):
		hydroponic_db.create_db("CREATE DATABASE IF NOT EXISTS {};".format(nakama_utils.get_locker_value("DATABASE")))

	def create_program_state_table(self):
		hydroponic_db.create_table("CREATE TABLE program_state ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  start_date DATETIME NOT NULL,"
			"  end_date DATETIME DEFAULT NULL,"
			"  program_name varchar(20) DEFAULT NULL,"
			"  current_phase varchar(20) DEFAULT NULL,"
			"  has_failed BOOLEAN DEFAULT FALSE,"
			"  ads1115_instance_state varchar(20) NOT NULL,"
			"  i2c_instance_state varchar(20) NOT NULL,"
			"  growlights_state varchar(20) NOT NULL,"
			"  main_pump_state varchar(20) NOT NULL,"
			"  nutrient_pumps_state varchar(20) NOT NULL,"
			"  water_ec_sensor_state varchar(20) NOT NULL,"
			"  water_flow_sensor_state varchar(20) NOT NULL,"
			"  water_ph_sensor_state varchar(20) NOT NULL,"
			"  water_temperature_state varchar(20) NOT NULL"
			") ENGINE='InnoDB'")

	def create_system_monitoring_table(self):
		hydroponic_db.create_table("CREATE TABLE system_monitoring ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  program_id int(10) NOT NULL,"
			"  last_update DATETIME NOT NULL,"
			"  emergency_stop_water_level_loops BOOLEAN NOT NULL,"
			"  emergency_stop_pump BOOLEAN NOT NULL,"
			"  emergency_stop_capacity BOOLEAN NOT NULL"
			") ENGINE='InnoDB'")

	def create_water_batch_baseline_table(self):
		hydroponic_db.create_table("CREATE TABLE water_batch_baseline ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  batch_id int(10) NOT NULL,"
			"  date DATETIME NOT NULL,"
			"  avarage_ec float(10,8) NOT NULL,"
			"  avarage_ph float(10,8) NOT NULL"
			") ENGINE='InnoDB'")

	def create_water_batch_table(self):
		hydroponic_db.create_table("CREATE TABLE water_batch ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  current_phase tinyint(2) DEFAULT NULL,"
			"  water_litres float(5,2) DEFAULT 25,"
			"  nutrient_a_milliliters int(10) DEFAULT 0,"
			"  nutrient_b_milliliters int(10) DEFAULT 0"
			") ENGINE='InnoDB'")

	def make_new_program_id(self):
		t = time.localtime()
		current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
		columns = ('(start_date,'
			'ads1115_instance_state,'
			'i2c_instance_state,'
			'growlights_state,'
			'main_pump_state,'
			'nutrient_pumps_state,'
			'water_ec_sensor_state,'
			'water_flow_sensor_state,'
			'water_ph_sensor_state,'
			'water_temperature_state)')

		values = "(STR_TO_DATE('{}', '%d/%m/%Y-%T'), '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
			current_time,
			nakama_store.PENDING,
			nakama_store.PENDING,
			nakama_store.PENDING,
			nakama_store.PENDING,
			nakama_store.PENDING,
			nakama_store.PENDING,
			nakama_store.PENDING,
			nakama_store.PENDING,
			nakama_store.PENDING)
		sql = "INSERT INTO program_state {} VALUES {};".format(columns,  values)
		program_id = hydroponic_db.insert_and_get_id(sql)

		hydroponic_db.update_table("INSERT INTO system_monitoring VALUES(DEFAULT, {}, STR_TO_DATE('{}', '%d/%m/%Y-%T'), False, False, False)".format(program_id, current_time))
		return program_id

	def create_water_batch_and_get_id(self):
		# create a new water batch instance, must be done with 25L of fresh water with no tutrients in it.
		new_batch_id = hydroponic_db.insert_and_get_id("INSERT INTO water_batch VALUES (DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)")
		if new_batch_id:
			nakama_utils.log_info('Succesfully created new water batch with id: "{}"'.format(new_batch_id))
			return new_batch_id

	def establish_water_baseline(self, batch_id):
		# 10 minutes run to get initial values. must be done with 22L of fresh water with no tutrients in it.
		# this will take the avarage from a series of PH and EC readings to establish the baseline for the water.
		try:
			t = time.localtime()
			current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
			def baseline_loop():
				try:
					self.ec_readings = []
					self.ph_readings = []
					while len(self.ec_readings) < 10 and len(self.ph_readings) < 10 and not self.force_exit:
						ec_reading = self.water_ec_sensor.read()
						ph_reading = self.water_ph_sensor.read()
						self.ec_readings.append(ec_reading)
						self.ph_readings.append(ph_reading)
						time.sleep(60)
					else:
						if nakama_utils.avarage_value(self.ec_readings, 10) and nakama_utils.avarage_value(self.ph_readings, 10):
							columns = ('(batch_id,'
								'date,'
								'avarage_ec,'
								'avarage_ph)')

							values = "('{}', STR_TO_DATE('{}', '%d/%m/%Y-%T'), '{}', '{}')".format(
								batch_id,
								current_time,
								nakama_utils.avarage_value(self.ec_readings, 10),
								nakama_utils.avarage_value(self.ph_readings, 10))
							sql = "INSERT INTO water_batch_baseline {} VALUES {};".format(columns,  values)
							hydroponic_db.update_table(sql)
							nakama_utils.log_info("SUCCESFULLY ESTABLISH NEW WATER BASELINE - Avarage PH: '{}', Avarage EC: '{}', Batch ID: '{}'".format(nakama_utils.avarage_value(self.ph_readings, 10),
								nakama_utils.avarage_value(self.ec_readings, 10),
								batch_id))
						else:
							nakama_utils.log_warning('belle_mere.establish_water_baseline', "BROKEN VALUES EC: {} - PH: {}".format(self.ec_readings, self.ph_readings), True)
				except Exception as e:
					mess = "BASELINE LOOP FAILED -- '{}'".format(e)
					nakama_utils.log_error('belle_mere.establish_water_baseline', mess)
					raise Exception(mess)

			self.baseline_monitor = threading.Thread(name='baseline_loop', target=baseline_loop)
			self.baseline_monitor.start()
		except Exception as e:
			mess = "BASELINE CREATION FAILED -- '{}'".format(e)
			nakama_utils.log_error('belle_mere.establish_water_baseline', mess)

	def run_water_check(self):
		# 10 minutes run to get initial values of a new water batch.
		# this will take the avarage from a series of PH and EC readings.
		try:
			def water_check_loop():
				try:
					self.ec_readings = []
					self.ph_readings = []
					while len(self.ec_readings) < 10 and len(self.ph_readings) < 10 and not self.force_exit:
						ec_reading = self.water_ec_sensor.read()
						ph_reading = self.water_ph_sensor.read()
						self.ec_readings.append(ec_reading)
						self.ph_readings.append(ph_reading)
						time.sleep(60)
					else:
						av_ec = nakama_utils.avarage_value(self.ec_readings, 10)
						av_ph = nakama_utils.avarage_value(self.ph_readings, 10)
						nakama_utils.log_info("SUCCESFULLY CHECKED WATER - Avarage PH: '{}', Avarage EC: '{}', Batch ID: '{}'".format(av_ph,
							av_ec,
							batch_id))
				except Exception as e:
					mess = "WATER CHECK LOOP FAILED -- '{}'".format(e)
					nakama_utils.log_error('belle_mere.run_water_check', mess)
					raise Exception(mess)

			self.water_check_monitor = threading.Thread(name='water_check_loop', target=water_check_loop)
			self.water_check_monitor.start()
		except Exception as e:
			mess = "BASELINE CREATION FAILED -- '{}'".format(e)
			nakama_utils.log_error('belle_mere.run_water_check', mess)

	def run_main_pump(self):
		try:
			self.switches.switch_main_pump(True)
			self.pump_running = True
			def main_pump_loop():
				try:
					self.water_flow_sensor.read()
					time.sleep(40)
					self.water_flow_sensor.read()
					while self.pump_running and not self.force_exit and not self.force_pause_pump:
						if self.water_flow_sensor.read() > 0.4 and not nakama_utils.emergency_stop_pump(self.program_id) and self.water_level_sensors.get_bottom_water_level_monitor().is_alive():
							time.sleep(5)
						else:
							self.pump_running = False
							if self.water_flow_sensor.read() < 0.4:
								nakama_utils.log_warning('belle_mere.main_pump_loop', "LOW WATER FLOW DETECTED, STOPPED MAIN PUMP. Water-flow: '{}'".format(self.water_flow_sensor.read()), True)
							if nakama_utils.emergency_stop_pump(self.program_id):
								nakama_utils.log_warning('belle_mere.main_pump_loop', "EMERGENCY STOP MAIN PUMP DETECTED - nakama_utils.emergency_stop_pump(): '{}'".format(nakama_utils.emergency_stop_pump(self.program_id)), True)
							if not self.water_level_sensors.get_bottom_water_level_monitor().is_alive():
								nakama_utils.log_warning('belle_mere.main_pump_loop', "NO WATER LEVEL MONITOR RUNNING, STOPPED MAIN PUMP - bottom_water_level_monitor().is_alive(): '{}'".format(self.water_level_sensors.get_bottom_water_level_monitor().is_alive()), True)
					if self.force_pause_pump:
						nakama_utils.log_info('Pause main pump')
						self.force_pause_pump = False
					else:
						nakama_utils.log_info('Emergency Stop main pump')
				except Exception as e:
					mess = "MAIN PUMP LOOP FAILED -- '{}'".format(e)
					nakama_utils.log_error('belle_mere.main_pump_loop', mess)
					raise Exception(mess)
				finally:
					self.switches.switch_main_pump(False)
					self.pump_running = False
					nakama_utils.log_info('MAIN PUMP END OF RUN', True)

			self.main_pump_monitor = threading.Thread(name='main_pump_loop', target=main_pump_loop)
			self.main_pump_monitor.start()
		except Exception as e:
			mess = "MAIN PUMP FAILED, TURNING OFF -- '{}'".format(e)
			nakama_utils.log_error('belle_mere.run_main_pump', mess)
			self.switches.switch_main_pump(False)
			self.pump_running = False
		finally:
			nakama_utils.log_info('MAIN PUMP SART OF RUN', True)

	def pause_pump(self):
		try:
			self.force_pause_pump = True
		except Exception as e:
			mess = "MAIN PUMP PAUSE FAILED -- '{}'".format(e)
			nakama_utils.log_error('belle_mere.main_pump_loop', mess)
			self.switches.switch_main_pump(False)
			self.pump_running = False
			raise Exception(mess)

	def run_growlights(self):
		try:
			def growlights_loop():
				if nakama_utils.get_instance_startup_state(self.program_id, 'growlights') == nakama_store.SUCCESS:
					try:
						self.growlights_running = True
						minutes = 0
						while not self.force_exit:
							if not self.growlights_running:
								if minutes == 0:
									nakama_utils.push_to_mobile('daily pic', 'end of light', 'pic')
									self.switches.switch_growlights(False)
									self.growlights_running = False
									minutes += 1
								elif minutes > 0 and minutes < 360:
									minutes += 1
								elif minutes >= 360:
									self.growlights_running = True
									minutes = 0
								time.sleep(60)
							else:
								if minutes == 0:
									self.switches.switch_growlights(True)
									self.growlights_running = True
									nakama_utils.push_to_mobile('daily pic', 'start of light', 'pic')
									minutes += 1
								elif minutes > 0 and minutes < 1080:
									minutes += 1
								elif minutes >= 1080:
									self.growlights_running = False
									minutes = 0
								time.sleep(60)
						else:
							nakama_utils.log_info('Stopping growlights loop')
					except Exception as e:
						mess = "GROWLIGHTS LOOP FAILED -- '{}'".format(e)
						nakama_utils.log_error('belle_mere.growlights_loop', mess)
						self.switches.switch_growlights(False)
						raise Exception(mess)
				else:
					raise Exception("COULD NOT START GROWLIGHTS -- Growlights state = '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'growlights')))

			self.growlights_monitor = threading.Thread(name='growlights_loop', target=growlights_loop)
			self.growlights_monitor.start()
		except Exception as e:
			mess = "GROWLIGHTS FAILED, TURNING OFF -- '{}'".format(e)
			nakama_utils.log_error('belle_mere.run_growlights', mess)
			self.switches.switch_growlights(False)
		finally:
			nakama_utils.log_info('GROWLIGHTS START OF RUN')
