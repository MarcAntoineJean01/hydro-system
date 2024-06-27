# water_ec_sensor.py

import sys
# sys.path is a list of absolute path strings
import os
sys.path.append(os.path.dirname(__file__) + '/../DFRobot_sensors')
import nakama_utils
import hydroponic_db
import nakama_store
import time

from DFRobot_EC import DFRobot_EC

class water_ec_sensor:

	def __init__(self, ads1115, water_temperature, prog_id):
		self.program_id = prog_id
		if not hydroponic_db.table_exists('water_ec_readings'):
			self.create_water_ec_readings_table()
		self.last_ec_readings = []
		if nakama_utils.get_instance_startup_state(self.program_id, 'i2c_instance') == nakama_store.SUCCESS and nakama_utils.get_instance_startup_state(self.program_id, 'ads1115_instance') == nakama_store.SUCCESS and nakama_utils.get_instance_startup_state(self.program_id, 'water_temperature') == nakama_store.SUCCESS:
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ec_sensor', nakama_store.PENDING)
			self.ads1115 = ads1115
			self.water_temperature = water_temperature
			self.setup()
		else:
			head_mess = "FAILED TO START WATER EC SENSOR. MISSING DEPENDENCY "
			i2c_mess = "i2c_state: '{}' - ".format(nakama_utils.get_instance_startup_state(self.program_id, 'i2c_instance'))
			ads1115_mess = "ads1115_state: '{}' - ".format(nakama_utils.get_instance_startup_state(self.program_id, 'ads1115_instance'))
			water_temp_mess = "water_temperature_state: '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'water_temperature'))
			mess = head_mess + i2c_mess + ads1115_mess + water_temp_mess
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ec_sensor', nakama_store.FAILED)
			nakama_utils.log_warning('water_ec_sensor.init', mess, True)

	def reset(self):
		self.ec.reset()

	def begin(self):
		self.ec.begin()

	def setup(self):
		try:
			self.ec = DFRobot_EC()
			# self.reset()
			self.begin()
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ec_sensor', nakama_store.SUCCESS)
		except Exception  as e:
			mess = "COULDN'T SETUP EC SENSOR  -- " + str(e)
			nakama_utils.log_error('water_ec_sensor.setup', mess)
			nakama_utils.update_instance_startup_state(self.program_id, 'water_ec_sensor', nakama_store.FAILED)
		finally:
			mess = "WATER EC SENSOR SETUP COMPLETE: '{}'".format(nakama_utils.get_instance_startup_state(self.program_id, 'water_ec_sensor'))
			nakama_utils.log_info(mess)

	def calibration(self):
		#Read your temperature sensor to execute temperature compensation
		temperature = self.water_temperature.read_celsius()
		#Get the Digital Value of Analog of selected channel
		self.ads1115.setGain()
		adc1 = self.ads1115.readVoltage(1)
		nakama_utils.log_info("A0:%dmV "%(adc1['r']))
		#Calibrate the calibration data
		self.ec.calibration(adc1['r'],temperature)

	def calibration1413(self):
		try:
			#Read your temperature sensor to execute temperature compensation
			temperature = self.water_temperature.read_celsius()
			#Get the Digital Value of Analog of selected channel
			self.ads1115.setGain()
			adc1 = self.ads1115.readVoltage(1)
			voltage = adc1['r']
			nakama_utils.log_info("A0:%dmV "%(voltage))
			#Calibrate the calibration data
			rawEC = 1000*voltage/820.0/200.0
			compECsolution = 1.413*(1.0+0.0185*(temperature-25.0))
			KValueTemp = 820.0*200.0*compECsolution/1000.0/voltage
			round(KValueTemp,2)
			nakama_utils.log_info(">>>Buffer Solution:1.413us/cm")
			f=open('ecdata.txt','r+', encoding='utf-8')
			flist=f.readlines()
			flist[0]='kvalueLow='+ str(KValueTemp) + '\n'
			f=open('ecdata.txt','w+', encoding='utf-8')
			f.writelines(flist)
			f.close()
			nakama_utils.log_info(">>>EC:1.413us/cm Calibration completed,Please enter Ctrl+C exit calibration in 5 seconds")
			time.sleep(5.0)
		except Exception as e:
			nakama_utils.log_error('water_ec_sensor.calibration1413', e)
			raise Exception(">>>Buffer Solution Error Try Again<<<")

	def calibration1288(self):
		try:
			#Read your temperature sensor to execute temperature compensation
			temperature = self.water_temperature.read_celsius()
			#Get the Digital Value of Analog of selected channel
			self.ads1115.setGain()
			adc1 = self.ads1115.readVoltage(1)
			voltage = adc1['r']
			nakama_utils.log_info("A0:%dmV "%(voltage))
			#Calibrate the calibration data
			rawEC = 1000*voltage/820.0/200.0
			compECsolution = 12.88*(1.0+0.0185*(temperature-25.0))
			KValueTemp = 820.0*200.0*compECsolution/1000.0/voltage
			nakama_utils.log_info(">>>Buffer Solution:12.88ms/cm")
			f=open('ecdata.txt','r+', encoding='utf-8')
			flist=f.readlines()
			flist[1]='kvalueHigh='+ str(KValueTemp) + '\n'
			f=open('ecdata.txt','w+', encoding='utf-8')
			f.writelines(flist)
			f.close()
			nakama_utils.log_info(">>>EC:12.88ms/cm Calibration completed,Please enter Ctrl+C exit calibration in 5 seconds")
			time.sleep(5.0)
		except Exception as e:
			nakama_utils.log_error('water_ec_sensor.calibration1288', e)
			raise Exception(">>>Buffer Solution Error Try Again<<<")

	def read(self):
		#Read your temperature sensor to execute temperature compensation
		temperature = self.water_temperature.read_celsius()
		#Get the Digital Value of Analog of selected channel
		adc1 = self.ads1115.get_instance().readVoltage(1)
		#Convert voltage to EC with temperature compensation
		EC = self.ec.readEC(adc1['r'],temperature)
		# nakama_utils.log_info("Temperature:%.1f ^C EC:%.2f" %(temperature,EC))
		self.last_ec_readings.append(EC)
		if len(self.last_ec_readings) > 20:
			self.last_ec_readings = self.last_ec_readings[-20:]
		self.last_reading_time = nakama_utils.now()
		return EC

	def read_last_reading_time(self):
		if hasattr(self, 'last_reading_time'):
			return self.last_reading_time
		else:
			return None

	def read_last_ec(self):
		if len(self.last_ec_readings) > 0:
			return round(self.last_ec_readings[-1], 3)
		else:
			return None

	def read_last_readings(self):
		return self.last_ec_readings

	def create_water_ec_readings_table(self):
		hydroponic_db.create_table("CREATE TABLE water_ec_readings ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  reading_date DATETIME NOT NULL,"
			"  reading_value float(10,8) NOT NULL"
			") ENGINE='InnoDB'")