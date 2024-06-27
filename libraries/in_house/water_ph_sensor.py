# water_ph_sensor.py

import sys
# sys.path is a list of absolute path strings
import os
sys.path.append(os.path.dirname(__file__) + '/../DFRobot_sensors')
import nakama_utils
import hydroponic_db
import nakama_store
import time

from DFRobot_PH import DFRobot_PH

class water_ph_sensor:

	def __init__(self, ads1115, water_temperature, prog_id):
		self.program_id = prog_id
		if not hydroponic_db.table_exists('water_ph_readings'):
			self.create_water_ph_readings_table()
		self.last_ph_readings = []
		if nakama_utils.get_instance_startup_state(self.program_id, 'i2c_instance') == nakama_store.SUCCESS and nakama_utils.get_instance_startup_state(self.program_id, 'ads1115_instance') == nakama_store.SUCCESS and nakama_utils.get_instance_startup_state(self.program_id, 'water_temperature') == nakama_store.SUCCESS:
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ph_sensor', nakama_store.PENDING)
			self.ads1115 = ads1115
			self.water_temperature = water_temperature
			self.setup()
		else:
			head_mess = "FAILED TO START WATER PH SENSOR. MISSING DEPENDENCY "
			i2c_mess = "i2c_state: '{}' - ".format(nakama_utils.get_instance_startup_state(self.program_id, 'i2c_instance'))
			ads1115_mess = "ads1115_state: '{}' - ".format(nakama_utils.get_instance_startup_state(self.program_id, 'ads1115_instance'))
			water_temp_mess = "water_temperature_state: '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'water_temperature'))
			mess = head_mess + i2c_mess + ads1115_mess + water_temp_mess
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ph_sensor', nakama_store.FAILED)
			nakama_utils.log_warning('water_ph_sensor.init', mess, True)

	def reset(self):
		self.ph.reset()

	def begin(self):
		self.ph.begin()

	def setup(self):
		try:
			self.ph = DFRobot_PH()
			# self.reset()
			self.begin()
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ph_sensor', nakama_store.SUCCESS)
		except Exception  as e:
			mess = "COULDN'T SETUP PH SENSOR  -- " + str(e)
			nakama_utils.log_error('water_ph_sensor.setup', mess)
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ph_sensor', nakama_store.FAILED)
		finally:
			mess = "WATER PH SENSOR SETUP COMPLETE: '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'water_ph_sensor'))
			nakama_utils.log_info(mess)

	def calibration(self):
		#Read your temperature sensor to execute temperature compensation
		temperature = self.water_temperature.read_celsius()
		#Get the Digital Value of Analog of selected channel
		self.ads1115.setGain()
		adc0 = self.ads1115.readVoltage(0)
		nakama_utils.log_info("A0:%dmV "%(adc0['r']))
		#Calibrate the calibration data
		self.ph.calibration(adc0['r'])

	def calibration7(self):
		try:
			#Read your temperature sensor to execute temperature compensation
			temperature = self.water_temperature.read_celsius()
			#Get the Digital Value of Analog of selected channel
			self.ads1115.setGain()
			adc0 = self.ads1115.readVoltage(0)
			voltage = adc0['r']
			nakama_utils.log_info("A0:%dmV "%(voltage))
			#Calibrate the calibration data
			nakama_utils.log_info(">>>Buffer Solution:7.0")
			f=open('phdata.txt','r+', encoding='utf-8')
			flist=f.readlines()
			flist[0]='neutralVoltage='+ str(voltage) + '\n'
			f=open('phdata.txt','w+', encoding='utf-8')
			f.writelines(flist)
			f.close()
			nakama_utils.log_info(">>>PH:7.0 Calibration completed,Please enter Ctrl+C exit calibration in 5 seconds")
			time.sleep(5.0)
		except Exception as e:
			nakama_utils.log_error('water_ph_sensor.calibration7', e)
			raise Exception(">>>Buffer Solution Error Try Again<<<")

	def calibration4(self):
		try:
			#Read your temperature sensor to execute temperature compensation
			temperature = self.water_temperature.read_celsius()
			#Get the Digital Value of Analog of selected channel
			self.ads1115.setGain()
			adc0 = self.ads1115.readVoltage(0)
			voltage = adc0['r']
			nakama_utils.log_info("A0:%dmV "%(voltage))
			#Calibrate the calibration data
			nakama_utils.log_info(">>>Buffer Solution:4.0")
			f=open('phdata.txt','r+', encoding='utf-8')
			flist=f.readlines()
			flist[1]='acidVoltage='+ str(voltage) + '\n'
			f=open('phdata.txt','w+', encoding='utf-8')
			f.writelines(flist)
			f.close()
			nakama_utils.log_info(">>>PH:4.0 Calibration completed,Please enter Ctrl+C exit calibration in 5 seconds")
			time.sleep(5.0)
		except Exception as e:
			nakama_utils.log_error('water_ph_sensor.calibration4', e)
			raise Exception(">>>Buffer Solution Error Try Again<<<")

	def read(self):
		#Read your temperature sensor to execute temperature compensation
		temperature = self.water_temperature.read_celsius()
		#Get the Digital Value of Analog of selected channel
		self.ads1115.setGain()
		adc0 = self.ads1115.readVoltage(0)
		#Convert voltage to PH with temperature compensation
		PH = self.ph.read_PH(adc0['r'],temperature)
		# nakama_utils.log_info("Temperature:%.1f ^C PH:%.2f" %(temperature,PH))
		self.last_ph_readings.append(PH)
		if len(self.last_ph_readings) > 20:
			self.last_ph_readings = self.last_ph_readings[-20:]
		self.last_reading_time = nakama_utils.now()
		return PH

	def read_last_reading_time(self):
		if hasattr(self, 'last_reading_time'):
			return self.last_reading_time
		else:
			return None

	def read_last_ph(self):
		if len(self.last_ph_readings) > 0:
			return round(self.last_ph_readings[-1], 3)
		else:
			return None

	def read_last_readings(self):
		return self.last_ph_readings

	def create_water_ph_readings_table(self):
		hydroponic_db.create_table("CREATE TABLE water_ph_readings ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  reading_date DATETIME NOT NULL,"
			"  reading_value float(10,8) NOT NULL"
			") ENGINE='InnoDB'")