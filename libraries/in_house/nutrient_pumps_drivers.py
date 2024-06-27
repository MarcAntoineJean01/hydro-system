# nutrient_pumps_drivers.py
import sys
sys.path.append('libraries/in_house')
if sys.platform == "linux" or sys.platform == "linux2":
	# linux
	pass
elif sys.platform == "darwin" or sys.platform == "win32":
	# OS X or # Windows...
	import nakama_mocker
	RpiMotorLib = nakama_mocker.Fake_RpiMotorLib()
elif sys.platform == "RASP_PI":
	from RpiMotorLib import RpiMotorLib
import nakama_utils
import hydroponic_db
import nakama_store

class nutrient_pumps_drivers:

	def __init__(self, switches, prog_id):
		self.program_id = prog_id
		if not hydroponic_db.table_exists('nutrients_input_tracking'):
			self.create_nutrients_input_tracking_table()
		if nakama_utils.get_instance_startup_state(self.program_id, 'nutrient_pumps') == nakama_store.SUCCESS:
			# need to set up for micro-stepping.
			self.switches = switches
			self.micro_steps_pins = nakama_store.MICRO_STEPS_PINS
			self.direction = nakama_store.DIRECTION
			self.step = nakama_store.STEP
			self.pump_motor = RpiMotorLib.A4988Nema(self.direction, self.step, self.micro_steps_pins, "A4988")
		else:
			head_mess = "FAILED TO START NUTRIENT PUMP DRIVERS. MISSING DEPENDENCY "
			switches_mess = "nutrient_pumps_state: '{}' ".format(nakama_utils.get_instance_startup_state(self.program_id, 'nutrient_pumps'))
			mess = head_mess + switches_mess
			nakama_utils.log_warning('nutrient_pumps_drivers.init', mess, True)

	def run_1(self):
		try:
			self.switches.switch_nutrient_pump_1(True)
			self.pump_motor.motor_go(False, "1/16" , 3200, .0009, False, .5)
			nakama_utils.log_info('DONE RUNNING PUMP 1')
			self.switches.switch_nutrient_pump_1(False)
		except Exception  as e:
			mess = "COULDN'T RUN NUTRIENT PUMP 1 -- {}".format(e)
			nakama_utils.log_error('nutrient_pumps_drivers.run_1', mess)

	def run_2(self):
		try:
			self.switches.switch_nutrient_pump_2(True)
			self.pump_motor.motor_go(False, "1/16" , 3200, .00075, False, .5)
			nakama_utils.log_info('DONE RUNNING PUMP 2')
			self.switches.switch_nutrient_pump_2(False)
		except Exception  as e:
			mess = "COULDN'T RUN NUTRIENT PUMP 2 -- {}".format(e)
			nakama_utils.log_error('nutrient_pumps_drivers.run_2', mess)

	def run_3(self):
		try:
			self.switches.switch_nutrient_pump_3(True)
			self.pump_motor.motor_go(False, "1/16" , 3200, .00075, False, .5)
			nakama_utils.log_info('DONE RUNNING PUMP 3')
			self.switches.switch_nutrient_pump_3(False)
		except Exception  as e:
			mess = "COULDN'T RUN NUTRIENT PUMP 3 -- {}".format(e)
			nakama_utils.log_error('nutrient_pumps_drivers.run_3', mess)


	def run_4(self):
		try:
			self.switches.switch_nutrient_pump_4(True)
			self.pump_motor.motor_go(False, "1/16" , 3200, .00075, False, .5)
			nakama_utils.log_info('DONE RUNNING PUMP 4')
			self.switches.switch_nutrient_pump_4(False)
		except Exception  as e:
			mess = "COULDN'T RUN NUTRIENT PUMP 4 -- {}".format(e)
			nakama_utils.log_error('nutrient_pumps_drivers.run_4', mess)

	def create_nutrients_input_tracking_table(self):
		hydroponic_db.create_table("CREATE TABLE nutrients_input_tracking ("
			"  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
			"  batch_id int(10) DEFAULT NULL,"
			"  pump tinyint(1) NOT NULL,"
			"  input_date DATETIME NOT NULL,"
			"  nutrient_dosage int(10) NOT NULL,"
			"  nutrient_name varchar(50) NOT NULL"
			") ENGINE='InnoDB'")
