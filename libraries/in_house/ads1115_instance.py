# ads1115_instance.py

import sys
# sys.path is a list of absolute path strings
import os
sys.path.append('{}/../DFRobot_sensors'.format(os.path.dirname(__file__)))
from DFRobot_ADS1115 import ADS1115
import nakama_utils
import nakama_store

# analog to digital converter (PH & EC)
ads1115 = ADS1115()
ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

class ads1115_instance:

	def __init__(self, prog_id):
		self.program_id = prog_id
		try:
			nakama_utils.update_instance_startup_state(self.program_id, 'ads1115_instance', nakama_store.PENDING)
			self.ads1115 = ADS1115()
			self.ads1115.setAddr_ADS1115(0x48)
			self.ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
			nakama_utils.update_instance_startup_state(self.program_id, 'ads1115_instance', nakama_store.SUCCESS)
		except Exception  as e:
			nakama_utils.update_instance_startup_state(self.program_id, 'ads1115_instance', nakama_store.FAILED)
			mess = "COULDN'T SETUP ADS1115 -- '{}'".format(e)
			nakama_utils.log_error('ads1115_instance.init', mess)

	def get_instance(self):
		return self.ads1115

	def setGain(self):
		self.ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)

	def readVoltage(self, value):
		return self.ads1115.readVoltage(value)