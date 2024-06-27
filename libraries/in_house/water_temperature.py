# water_temperature.py
import os
import nakama_utils
import hydroponic_db
import nakama_store

class water_temperature:

	def __init__(self, prog_id):
		self.program_id = prog_id
		if not hydroponic_db.table_exists('water_temperature_readings'):
			self.create_water_temperature_readings_table()
		self.last_c_readings = []
		self.last_f_readings = []
		nakama_utils.update_instance_startup_state(self.program_id, 'water_temperature', nakama_store.PENDING)
		nakama_utils.log_info("Testing water_temperature sensor")
		self.read(self.sensor())
		if nakama_utils.get_instance_startup_state(self.program_id, 'water_temperature') == nakama_store.SUCCESS:
			nakama_utils.log_info("Success testing water_temperature sensor")
		else:
			nakama_utils.log_info("Failed testing water_temperature, state: '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'water_temperature')))

	def sensor(self):
		ds18b20 = []
		for i in os.listdir('/sys/bus/w1/devices'):
			if i != 'w1_bus_master1':
				ds18b20.append(i)
				nakama_utils.log_info("ADDED ds18b20 ADDRESS: " + i)
		return ds18b20

	def read(self, ds18b20):
		tfile = False
		try:
			for address in ds18b20:
				try:
					location = '/sys/bus/w1/devices/' + address + '/w1_slave'
					tfile = nakama_utils.open_retry(location, 'r')
				except Exception as e:
					nakama_utils.log_warning('water_temperature.read', "'{}' NOT WORKING, TRYING NEXT".format(address), False)
		finally:
			if tfile:
				nakama_utils.log_info("SUCCESS, READING: " + address)
				text = tfile.read()
				tfile.close()
				secondline = text.split("\n")[1]
				temperaturedata = secondline.split(" ")[9]
				temperature = float(temperaturedata[2:])
				celsius = temperature / 1000
				farenheit = (celsius * 1.8) + 32
				nakama_utils.update_instance_startup_state(self.program_id, 'water_temperature', nakama_store.SUCCESS)
				self.last_c_readings.append(celsius)
				self.last_f_readings.append(farenheit)
				if len(self.last_c_readings) > 20:
					self.last_c_readings = self.last_c_readings[-20:]
				if len(self.last_f_readings) > 20:
					self.last_f_readings = self.last_f_readings[-20:]
				self.last_reading_time = nakama_utils.now()
				return celsius, farenheit
			else:
				nakama_utils.log_warning('water_temperature.read', 'FAILED TO FIND WATER TEMPERATURE SENSOR, SENT FAKE VALUES 25c, 76f', True)
				nakama_utils.update_instance_startup_state(self.program_id, 'water_temperature', nakama_store.FAILED)
				self.last_c_readings.append('fake')
				self.last_f_readings.append('fake')
				if len(self.last_c_readings) > 20:
					self.last_c_readings = self.last_c_readings[-20:]
				if len(self.last_f_readings) > 20:
					self.last_f_readings = self.last_f_readings[-20:]
				self.last_reading_time = nakama_utils.now()
				return 25, 76

	def read_celsius(self):
		return self.read(self.sensor())[0]

	def read_farenheit(self):
		return self.read(self.sensor())[1]

	def read_rounded_celsius(self):
		return round(self.read_celsius(), 1)

	def read_rounded_farenheit(self):
		return round(self.read_farenheit(), 1)

	def read_last_celsius(self):
		if len(self.last_c_readings) > 0:
			return self.last_c_readings[-1]
		else:
			return None

	def read_last_farenheit(self):
		if len(self.last_f_readings) > 0:
			return self.last_f_readings[-1]
		else:
			return None

	def read_last_rounded_celsius(self):
		if len(self.last_c_readings) > 0:
			if self.last_c_readings[-1] != 'fake':
				return round(self.last_c_readings[-1], 1)
			else:
				return self.last_c_readings[-1]
		else:
			return None

	def read_last_rounded_farenheit(self):
		if len(self.last_f_readings) > 0:
			if self.last_f_readings[-1] != 'fake':
				return round(self.last_f_readings[-1], 1)
			else:
				return self.last_f_readings[-1]
		else:
			return None

	def read_last_readings(self):
		return self.last_c_readings, self.last_f_reading

	def read_last_reading_time(self):
		if hasattr(self, 'last_reading_time'):
			return self.last_reading_time
		else:
			return None

	def create_water_temperature_readings_table(self):
		hydroponic_db.create_table("CREATE TABLE water_temperature_readings ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  reading_date DATETIME NOT NULL,"
			"  reading_value float(10,8) NOT NULL"
			") ENGINE='InnoDB'")