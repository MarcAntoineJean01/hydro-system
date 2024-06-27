try:
	import sys
	import json
	from guizero import App, PushButton, Waffle, TitleBox, Text, Window, Box, TextBox
	import subprocess
	import pathlib
	import shlex
	import nakama_dependency_list
	import os
except Exception  as e:
	print(e)
	print("something went wrong with dependecies, check out the README file")
	sys.exit()
import time
class UI_Shell:

	def __init__(self):
		try:
			self.app = App(title="My app", width=800, height=480)
			self.app.full_screen = True if sys.platform == "RASP_PI" else False
			self.welcome_screen()

			self.app.display()
		except Exception  as e:
			print(e)
			print("something went wrong with UI_Shell.__init__()")
			sys.exit()

#SCREENS
	def welcome_screen(self):
		self.title_box = TitleBox(self.app, text="Welcome", layout="auto", height='fill', width='fill')

		welcome_text = "Hello and welcome! press the start button to start up app, first we're going to make sure everything is set up to run smoothly!"
		self.welcome_text = Text(self.title_box, text=welcome_text)
		self.main_app_button = PushButton(self.title_box, self.check_screen, text='Start')
		self.exit_button = PushButton(self.title_box, self.exit_app, text='Exit')

	def check_screen(self):
		self.title_box.destroy()

		self.title_box = TitleBox(self.app, text="Start-up", layout="auto", height='fill', width='fill')
		self.packages_state_text = Text(self.title_box, text='Checking packages: WORKING', color='red', size=14)
		self.libraries_state_text = Text(self.title_box, text='Checking libraries: WAITING', color='yellow', size=14)
		self.app.update()

		self.check_packages()
		self.packages_state_text.value='Checking packages: DONE'
		self.packages_state_text.text_color='green'

		self.libraries_state_text.value='Checking libraries: WORKING'
		self.libraries_state_text.text_color='red'
		self.app.update()

		self.check_libraries()
		self.libraries_state_text.value='Checking libraries: DONE'
		self.libraries_state_text.text_color='green'
		self.app.update()


#METHODS
	def exit_app(self):
		sys.exit()

	def check_packages(self):
		time.sleep(2)
		try:
			all_good = True
			print("checking packages")
			data = subprocess.check_output(["pip", "list", "--format", "json"])
			parsed_results = json.loads(data)

			for pack in nakama_dependency_list.packages:
				if any(installed["name"] == pack[0] for installed in parsed_results): 
					print(f"done checking {pack[0]}")
				else:
					all_good = False
					print(f"couldn't find package {pack[0]}, attempting install.")
					cmd = f"pip install {pack[0]}"
					open_process = subprocess.Popen(shlex.split(cmd))
					open_process.wait()
					print(f"done installing {pack[0]}")

			if all_good:
				print("done checking packages")
			else:
				new_data = subprocess.check_output(["pip", "list", "--format", "json"])
				new_parsed_results = json.loads(new_data)

				for pack in nakama_dependency_list.packages:
					if any(installed["name"] == pack[0] for installed in new_parsed_results): 
						print(f"done checking {pack[0]}")
					else:
						raise Exception(f"package {pack[0]} still missing, aborting install.")
				print("done checking packages")
		except Exception as e:
			print(e)
			print("something wrong while checking packages, call for help!")

	def check_libraries(self):
		print("checking libraries")
		try:
			for lib in nakama_dependency_list.libraries:
				os.path.isdir(f"libraries/{lib}")
			time.sleep(2)
		except Exception as e:
			print(e)
			print("something wrong while checking libraries, call for help!")
		print("done checking libraries")




# try:
# 	import sys
# 	sys.path.append('libraries/in_house')
# 	import subprocess as sp
# 	import pathlib
# 	import shlex
# 	import json
# 	from guizero import App, PushButton, Waffle, TitleBox, Text, Window, Box, TextBox
# 	if sys.platform == "linux" or sys.platform == "linux2":
# 		# linux
# 		pass
# 	elif sys.platform == "darwin" or sys.platform == "win32":
# 		# OS X or # Windows...
# 		import nakama_mocker
# 		GPIO = nakama_mocker.Fake_GPIO()
# 	elif sys.platform == "RASP_PI":
# 		import RPi.GPIO as GPIO
# 	import nakama_utils
# 	import belle_mere
# 	import re
# 	import time
# 	import hydroponic_db
# 	import threading
# 	import nakama_store
# except Exception  as e:
# 	print(e)
# 	print("something wrong with dependecies, run nakama_setup.py")
# 	sys.exit()

# class UI:

# 	def __init__(self):
# #################### INSTANCE NOT READY ##############################
# 		GPIO.cleanup()
# 		# INSTANCE
# 		self.belle_mere = belle_mere.belle_mere()
# 		# APP
# 		self.app = App(title="My app", width=800, height=480)
# 		self.welcome_screen(False)

# 		self.app.display()

# 	def welcome_screen(self, dest=True):
# 		if dest:
# 			self.title_box.destroy()
# 		self.title_box = TitleBox(self.app, text="Welcome", layout="auto", height='fill', width='fill')

# 		self.app.full_screen = True if sys.platform == "RASP_PI" else False

# 		# SYSTEM
# 		self.welcome_box = TitleBox(self.title_box, text="Welcome", height=360, width="fill", border=5, align='left')
# 		self.main_app_button = PushButton(self.welcome_box, self.main_app_screen, text='Start', height=4, width="fill")
# 		self.settings_button = PushButton(self.welcome_box, self.settings_screen, text='Settings', height=4, width="fill")
# 		self.exit_button = PushButton(self.welcome_box, self.exit_app, text='Exit', height=2, width=40)

# 	def settings_screen(self):
# 		self.title_box.destroy()

# 		self.title_box = TitleBox(self.app, text="Settings", layout="auto", height='fill', width='fill')
# 		self.DB_USER_box = TitleBox(self.title_box, text="db user", layout="grid", height='fill', width='fill')
# 		self.update_DB_USER_input_box = TextBox(self.DB_USER_box, text=self.get_current_param('DB_USER'),  width=40, grid=[1, 0])
# 		self.update_DB_USER_button = PushButton(self.DB_USER_box, lambda: self.update_locker('DB_USER', self.update_DB_USER_input_box.value), text='Update DB_USER', height=2, width=40, grid=[0,0])
# 		self.DB_PASSWORD_box = TitleBox(self.title_box, text="db password", layout="grid", height='fill', width='fill')
# 		self.update_DB_PASSWORD_input_box = TextBox(self.DB_PASSWORD_box, text=self.get_current_param('DB_PASSWORD'), width=40, hide_text=True, grid=[1, 0])
# 		self.update_DB_PASSWORD_button = PushButton(self.DB_PASSWORD_box, lambda: self.update_locker('DB_PASSWORD', self.update_DB_PASSWORD_input_box.value), text='Update DB_PASSWORD', height=2, width=40, grid=[0,0])
# 		self.DB_HOST_box = TitleBox(self.title_box, text="db host", layout="grid", height='fill', width='fill')
# 		self.update_DB_HOST_input_box = TextBox(self.DB_HOST_box, text=self.get_current_param('DB_HOST'), width=40, grid=[1, 0])
# 		self.update_DB_HOST_button = PushButton(self.DB_HOST_box, lambda: self.update_locker('DB_HOST', self.update_DB_HOST_input_box.value), text='Update DB_HOST', height=2, width=40, grid=[0,0])
# 		self.DB_PORT_box = TitleBox(self.title_box, text="db port", layout="grid", height='fill', width='fill')
# 		self.update_DB_PORT_input_box = TextBox(self.DB_PORT_box, text=self.get_current_param('DB_PORT'), width=40, grid=[1, 0])
# 		self.update_DB_PORT_button = PushButton(self.DB_PORT_box, lambda: self.update_locker('DB_PORT', self.update_DB_PORT_input_box.value), text='Update DB_PORT', height=2, width=40, grid=[0,0])
# 		self.DATABASE_box = TitleBox(self.title_box, text="database", layout="grid", height='fill', width='fill')
# 		self.update_DATABASE_input_box = TextBox(self.DATABASE_box, text=self.get_current_param('DATABASE'), width=40, grid=[1, 0])
# 		self.update_DATABASE_button = PushButton(self.DATABASE_box, lambda: self.update_locker('DATABASE', self.update_DATABASE_input_box.value), text='Update DATABASE', height=2, width=40, grid=[0,0])

# 		self.go_back_button = PushButton(self.title_box, self.welcome_screen, text='Go Back', height=2, width=40)

# 	def main_app_screen(self):
# 		self.title_box.destroy()
# 		self.title_box = TitleBox(self.app, text="Main", layout="auto", height='fill', width='fill')

# 		self.calibration_box = TitleBox(self.title_box, text="Calibration", height='fill', width='fill', border=5, align='top')
# 		self.calibrate_ec1413_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ec1413'], text='Calibrate EC:1.413us/cm', height=2, width=15, align='left')
# 		self.calibrate_ec1288_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ec1288'], text='Calibrate EC:12.88ms/cm', height=2, width=15, align='left')		
# 		self.calibrate_ph4_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ph4'], text='Calibrate >PH:4.0', height=2, width=15, align='left')
# 		self.calibrate_ph7_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ph7'], text='Calibrate >PH:7.0', height=2, width=15, align='left')

# 		self.testing_box = TitleBox(self.title_box, text="Testing", height='fill', width='fill', border=5, align='top')

# 		self.programs_box = TitleBox(self.title_box, text="Programs", height='fill', width='fill', border=5, align='top')

# 		self.go_back_button = PushButton(self.title_box, self.welcome_screen, text='Go Back', height=2, width=40, align='bottom')

# 	def update_locker(self, key, value):
# 		if isinstance(key, str) is False or isinstance(value, str) is False or key == '':
# 			print("Variable input error, Key: {}, Value: {}".format(key, value))
# 		else:
# 			try:
# 				# Opening JSON file
# 				old_locker = open('nakama_locker.json')
# 				data = json.load(old_locker)
# 				old_locker.close()
# 				if value != '':
# 					data["{}".format(key)] = value
# 					nakama_locker = open("nakama_locker.json", "w")
# 					nakama_locker.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
# 					nakama_locker.close()
# 					print("Replaced {} in nakama_locker.json".format(key))
# 				elif data["{}".format(key)] is None:
# 					raise KeyError
# 				else:
# 					print("Variable input error, Key: {}, Value: {}".format(key, value))
# 			except KeyError as ex:
# 				print("'Missing Key:{}".format(ex))
# 				data["{}".format(key)] = getattr(nakama_store, key)
# 				# Writing to nakama_locker.json
# 				broken_locker = open("nakama_locker.json", "w")
# 				broken_locker.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
# 				broken_locker.close()
# 				print("added {} = {} to nakama_locker.json".format(key, value))
# 			except Exception  as ex:
# 				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
# 				message = template.format(type(ex).__name__, ex.args)
# 				print(message)
# 				sys.exit()

# 	def get_current_param(self, key):
# 		try:
# 			locker = open('nakama_locker.json')
# 			data = json.load(locker)
# 			locker.close()
# 			print(data["{}".format(key)])
# 			value = data["{}".format(key)]
# 			if value is not None:
# 				return value
# 			else:
# 				raise KeyError
# 		except KeyError as ex:
# 				print("No value found for {}, using default setting".format(key))
# 				return getattr(nakama_store, key)
# 		except Exception  as ex:
# 			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
# 			message = template.format(type(ex).__name__, ex.args)
# 			print(message)
# 			print(ex)
# 			return None






























# 	def start_app(self):
# 		self.title_box.destroy()
		
# 		self.title_box = TitleBox(self.app, text="Belle Mere", layout="auto", height='fill', width='fill')
# 		self.section_box = Box(self.title_box, layout="auto", height=360, width='fill', align='top')

# 		# CALIBRATION
# 		self.calibration_box = TitleBox(self.section_box, text="Calibration", height=360, width=260, border=5, align='left')
# 		self.calibrate_ec1413_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ec1413'], text='Calibrate EC:1.413us/cm', height=3, width=22)
# 		self.calibrate_ec1288_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ec1288'], text='Calibrate EC:12.88ms/cm', height=3, width=22)		
# 		self.calibrate_ph4_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ph4'], text='Calibrate >PH:4.0', height=3, width=22)
# 		self.calibrate_ph7_button = PushButton(self.calibration_box, self.select_calibration, args=['calibrate_ph7'], text='Calibrate >PH:7.0', height=3, width=22)

# 		self.calibration_box.disable()

# 		# PROGRAMS
# 		self.program_box = TitleBox(self.section_box, text="Programs", height=360, width=260, border=5,  layout='grid', align='left')
# 		self.basic_test_run_button = PushButton(self.program_box, self.select_program, args=['test'], text='Run basic test', grid=[0,0], height=3, width=12)
# 		self.water_baseline_test_run_button = PushButton(self.program_box, self.select_program, args=['water_baseline_test'], text='Run water\nBaseline test', grid=[0,1], height=3, width=12)
# 		self.water_batch_setup_run_button = PushButton(self.program_box, self.select_program, args=['water_batch_setup'], text='Run water\nBatch setup', grid=[0,2], height=3, width=12)
# 		self.water_check_run_button  = PushButton(self.program_box, self.select_program, args=['water_check'], text='Check water', grid=[0,3], height=3, width=11)
# 		self.phase1_button = PushButton(self.program_box, self.select_program, args=['phase_1'], text='Run phase_1', grid=[1,0], height=3, width=12)
# 		self.phase2_button = PushButton(self.program_box, self.select_program, args=['phase_2'], text='Run phase_2', grid=[1,1], height=3, width=12)
# 		self.phase3_button = PushButton(self.program_box, self.select_program, args=['phase_3'], text='Run phase_3', grid=[1,2], height=3, width=12)
# 		self.phase4_button = PushButton(self.program_box, self.select_program, args=['phase_4'], text='Run phase_4', grid=[1,3], height=3, width=12)
# 		self.program_box.disable()

# 		# SYSTEM
# 		self.system_box = TitleBox(self.section_box, text="System", height=360, width=260, border=5, align='left')
# 		self.exit_button = PushButton(self.system_box, self.exit_app, text='Exit App!', height=4, width=22)
# 		self.exit_button.disable()
# 		self.instance_state_text = Text(self.system_box, text='APP NOT READY', height=250, width='fill', align='bottom', color='red', size=14)
# 		self.instance_state_text.text_size = 8
# 		self.instance_state_text.repeat(800, self.check_instance)
# 		self.app.repeat(1000, self.check_stops)

# 		# INFO
# 		self.info_box = TitleBox(self.title_box, text="Info", layout="grid", height=70, width='fill', align='bottom')
		
# 		self.ads1115_box = Box(self.info_box, grid=[0, 0],  border=1, width=130, height=25)
# 		self.ads1115_text = Text(self.ads1115_box, text='ads1115', align='left')
# 		Box(self.ads1115_box, width=10, height=10, align='right') # padding
# 		self.ads1115_check = Box(self.ads1115_box, width=10, height=10, align='right')
		
# 		self.i2c_box = Box(self.info_box, grid=[1, 0],  border=1, width=130, height=25)
# 		self.i2c_text = Text(self.i2c_box, text='i2c', align='left')
# 		Box(self.i2c_box, width=10, height=10, align='right') # padding
# 		self.i2c_check = Box(self.i2c_box, width=10, height=10, align='right')
		
# 		self.growlights_box = Box(self.info_box, grid=[2,0],  border=1, width=130, height=25)
# 		self.growlights_text = Text(self.growlights_box, text='growlights', align='left')
# 		Box(self.growlights_box, width=10, height=10, align='right') # padding
# 		self.growlights_check = Box(self.growlights_box, width=10, height=10, align='right')
		
# 		self.main_pump_box = Box(self.info_box, grid=[3,0],  border=1, width=130, height=25)
# 		self.main_pump_text = Text(self.main_pump_box, text='main_pump', align='left')
# 		Box(self.main_pump_box, width=10, height=10, align='right') # padding
# 		self.main_pump_check = Box(self.main_pump_box, width=10, height=10, align='right')
		
# 		self.nutrient_pumps_box = Box(self.info_box, grid=[4,0],  border=1, width=130, height=25)
# 		self.nutrient_pumps_text = Text(self.nutrient_pumps_box, text='nutrient_pumps', align='left')
# 		Box(self.nutrient_pumps_box, width=10, height=10, align='right') # padding)
# 		self.nutrient_pumps_check = Box(self.nutrient_pumps_box, width=10, height=10, align='right')
		
# 		self.ec_sensor_box = Box(self.info_box, grid=[5,0],  border=1, width=130, height=25)
# 		self.ec_sensor_text = Text(self.ec_sensor_box, text='ec_sensor', align='left')
# 		Box(self.ec_sensor_box, width=10, height=10, align='right') # padding
# 		self.ec_sensor_check = Box(self.ec_sensor_box, width=10, height=10, align='right')
		
# 		self.water_flow_box = Box(self.info_box, grid=[0,1],  border=1, width=130, height=25)
# 		self.water_flow_text = Text(self.water_flow_box, text='water_flow', align='left')
# 		Box(self.water_flow_box, width=10, height=10, align='right') # padding
# 		self.water_flow_check = Box(self.water_flow_box, width=10, height=10, align='right')
		
# 		self.ph_sensor_box = Box(self.info_box, grid=[1,1],  border=1, width=130, height=25)
# 		self.ph_sensor_text = Text(self.ph_sensor_box, text='ph_sensor', align='left')
# 		Box(self.ph_sensor_box, width=10, height=10, align='right') # padding
# 		self.ph_sensor_check = Box(self.ph_sensor_box, width=10, height=10, align='right')
		
# 		self.water_temperature_box = Box(self.info_box, grid=[2,1],  border=1, width=130, height=25)
# 		self.water_temperature_text = Text(self.water_temperature_box, text='water_temp', align='left')
# 		Box(self.water_temperature_box, width=10, height=10, align='right') # paddingft')
# 		self.water_temperature_check = Box(self.water_temperature_box, width=10, height=10, align='right')
		
# 		self.stop_loops_box = Box(self.info_box, grid=[3,1],  border=1, width=130, height=25)
# 		self.stop_loops_text = Text(self.stop_loops_box, text='stop_loops', align='left')
# 		Box(self.stop_loops_box, width=10, height=10, align='right') # padding
# 		self.stop_loops_check = Box(self.stop_loops_box, width=10, height=10, align='right')
		
# 		self.stop_pump_box = Box(self.info_box, grid=[4,1],  border=1, width=130, height=25)
# 		self.stop_pump_text = Text(self.stop_pump_box, text='stop_pump', align='left')
# 		Box(self.stop_pump_box, width=10, height=10, align='right') # padding
# 		self.stop_pump_check = Box(self.stop_pump_box, width=10, height=10, align='right')
		
# 		self.stop_capacity_box = Box(self.info_box, grid=[5,1],  border=1, width=130, height=25)
# 		self.stop_capacity_text = Text(self.stop_capacity_box, text='stop_capacity', align='left')
# 		Box(self.stop_capacity_box, width=10, height=10, align='right') # padding
# 		self.stop_capacity_check = Box(self.stop_capacity_box, width=10, height=10, align='right')

# 		self.ads1115_check.bg = 'yellow'
# 		self.i2c_check.bg = 'yellow'
# 		self.growlights_check.bg = 'yellow'
# 		self.main_pump_check.bg = 'yellow'
# 		self.nutrient_pumps_check.bg = 'yellow'
# 		self.ec_sensor_check.bg = 'yellow'
# 		self.water_flow_check.bg = 'yellow'
# 		self.ph_sensor_check.bg = 'yellow'
# 		self.water_temperature_check.bg = 'yellow'
# 		self.stop_loops_check.bg = 'yellow'
# 		self.stop_pump_check.bg = 'yellow'
# 		self.stop_capacity_check.bg = 'yellow'
# 		self.setup_thread = threading.Thread(name='setup_thread', target=self.belle_mere.main_setup)
# 		self.setup_thread.start()

# 	def check_color(self, val):
# 		if val == nakama_store.PENDING:
# 			return 'yellow'
# 		elif val == nakama_store.SUCCESS:
# 			return 'green'
# 		elif val == nakama_store.FAILED:
# 			return 'red'
# 		else:
# 			return 'black'

# 	def check_stops(self):
# 		stop_sql = 'SELECT emergency_stop_water_level_loops, emergency_stop_pump, emergency_stop_capacity FROM system_monitoring WHERE program_id = {}'.format(self.belle_mere.program_id)
# 		stop_vals = hydroponic_db.query_table(stop_sql)[0]
# 		self.stop_loops_check.bg = 'red' if stop_vals[0] else 'green'
# 		self.stop_pump_check.bg = 'red' if stop_vals[1] else 'green'
# 		self.stop_capacity_check.bg = 'red' if stop_vals[2] else 'green'

# 	def check_instance(self):
# 		state_sql = 'SELECT ads1115_instance_state, i2c_instance_state, growlights_state, main_pump_state, nutrient_pumps_state, water_ec_sensor_state, water_flow_sensor_state, water_ph_sensor_state, water_temperature_state FROM program_state WHERE id = {}'.format(self.belle_mere.program_id)
# 		inst_vals = hydroponic_db.query_table(state_sql)[0]
# 		self.ads1115_check.bg = self.check_color(inst_vals[0])
# 		self.i2c_check.bg = self.check_color(inst_vals[1])
# 		self.growlights_check.bg = self.check_color(inst_vals[2])
# 		self.main_pump_check.bg = self.check_color(inst_vals[3])
# 		self.nutrient_pumps_check.bg = self.check_color(inst_vals[4])
# 		self.ec_sensor_check.bg = self.check_color(inst_vals[5])
# 		self.water_flow_check.bg = self.check_color(inst_vals[6])
# 		self.ph_sensor_check.bg = self.check_color(inst_vals[7])
# 		self.water_temperature_check.bg = self.check_color(inst_vals[8])

# 		if hasattr(self, 'belle_mere'):
# 			if self.belle_mere.instance_ready:
# 				#################### INSTANCE READY ##############################

# 				# CALIBRATION
# 				self.calibration_box.enable()

# 				# PROGRAMS
# 				self.program_box.enable()

# 				# SYSTEM
# 				self.instance_state_text.destroy()
# 				self.instance_state_text = Text(self.system_box, text='APP READY', height=250, width='fill', align='bottom', color='green', size=14)
# 				self.instance_state_text.value = "APP READY"
# 				self.exit_button.enable()
# 			else:
# 				self.instance_state_text.value = "APP NOT READY"
# 		else:
# 			self.instance_state_text.value = 'INSTANCE NOT FOUND'

# 	def run_nutrient_pump(self, pump):
# 		try:
# 			self.pump1_button.disable()
# 			self.pump2_button.disable()
# 			self.pump3_button.disable()
# 			self.pump4_button.disable()
# 			self.app.update()
# 			if pump == 1:
# 				self.belle_mere.nutrient_pumps_drivers.run_1()
# 			elif pump == 2:
# 				self.belle_mere.nutrient_pumps_drivers.run_2()
# 			elif pump == 3:
# 				self.belle_mere.nutrient_pumps_drivers.run_3()
# 			elif pump == 4:
# 				self.belle_mere.nutrient_pumps_drivers.run_4()
# 			else:
# 				raise 'wrong pump number: {}'.format(pump)
# 		except Exception as e:
# 			print(e)
# 			nakama_utils.log_error('UI.run_nutrient_pump', str(e))
# 		finally:
# 			self.pump1_button.enable()
# 			self.pump2_button.enable()
# 			self.pump3_button.enable()
# 			self.pump4_button.enable()
# 			self.app.update()

# 	def select_calibration(self, prog):
# 		fail = False
# 		try:
# 			self.app.disable()
# 			self.app.update()
# 		except Exception as e:
# 			print(e)
# 			nakama_utils.log_error('UI.select_calibration', str(e))
# 			fail = True
# 		finally:
# 			if not fail:
# 				self.belle_mere.run_calibration(prog)
# 				self.app.enable()
# 				self.app.update()

# 	def select_program(self, prog):
# 		fail = False
# 		try:
# 			self.calibration_box.destroy()
# 			self.program_box.destroy()
# 			self.system_box.destroy()
# 			# MONITORING
# 			self.monitoring_box = TitleBox(self.section_box, text="Monitoring", height=360, width=260, border=5, align='left')
# 			self.readings_text = Text(self.monitoring_box, text=self.make_readings_text(), height=11, width='fill', align='top')
# 			self.program_text = Text(self.monitoring_box, text=self.make_program_text(), height=10, width='fill', align='top')
# 			self.monitoring_box.repeat(1000, self.update_monitoring)

# 			# LOGS
# 			self.log_box = TitleBox(self.section_box, text="Log", height=360, width=260, border=5, align='left')
# 			current_log = open('./logs/logs.txt', 'r', encoding='utf-8')
# 			raw_text = current_log.read()
# 			last_log = raw_text[raw_text.rindex('NAKAMA'):]
# 			self.last_log_text = Text(self.log_box, text=last_log, height=10, width='fill', align='top')
# 			current_log.close()
# 			self.open_full_log_button = PushButton(self.log_box, self.open_full_log, text='Open Full Log', height=1, width=22, align='top')
# 			self.open_interactions_button = PushButton(self.log_box, self.open_interactions, text='Open Interactions Window', height=1, width=22, align='top')
# 			self.last_log_text.text_size = 8
# 			self.last_log_text.repeat(1000, self.update_log)

# 			# SYSTEM
# 			self.system_box = TitleBox(self.section_box, text="System", height=360, width=260, border=5, align='left')
# 			self.emergency_stop_pump_button = PushButton(self.system_box, self.emergency_stop_pump, text='emergency stop\nMain pump!', height=4, width=22)
# 			self.emergency_stop_capacity_button = PushButton(self.system_box, self.emergency_stop_capacity, text='emergency stop\n Reached max capacity!', height=4, width=22)
# 			self.exit_button = PushButton(self.system_box, self.end_program_and_exit_app, text='Exit App!', height=4, width=22)
# 			self.app.update()
# 			print('START PROGRAM "{}"'.format(prog))
# 		except Exception as e:
# 			print(e)
# 			nakama_utils.log_error('UI.select_program', str(e))
# 			fail = True
# 		finally:
# 			if not fail:
# 				print('DEBUG RUN PROGRAM "{}"'.format(prog))
# 				self.current_program = threading.Thread(name='current_program', target=self.belle_mere.start_program, args=[prog])
# 				self.current_program.start()

# 	def open_full_log(self):
# 		current_log = open('./logs/verbose_logs.txt', 'r', encoding='utf-8')
# 		raw_text = current_log.read()
# 		self.log_window = Window(self.app, title = "Full Log", height=480, width=800)
# 		self.log_text = TextBox(self.log_window, scrollbar=True, multiline=True, text=raw_text, height='fill', width='fill', align='top')
# 		self.log_text.text_size = 8
# 		current_log.close()

# 	def open_interactions(self):
# 		self.interaction_window = Window(self.app, title = "Interactions", height=480, width=800)
# 		# MAIN PUMP
# 		self.main_pump_box = TitleBox(self.interaction_window, text="Main Pump", height=200, width=260, border=5, align='left')
# 		self.pause_pump_button = PushButton(self.main_pump_box, self.pause_pump, text='Pause pump', height=1, width=9)
# 		self.restart_pump_button = PushButton(self.main_pump_box, self.restart_pump, text='Start pump', height=1, width=9)
# 		self.pause_pump_button.disable()
# 		self.restart_pump_button.disable()
# 		# NUTRIENT PUMPS
# 		self.nutrient_pumps_box = TitleBox(self.interaction_window, text="Nutrient Pumps", height=200, width=260, border=5, align='left', layout='grid')
# 		self.pump1_button = PushButton(self.nutrient_pumps_box, self.run_nutrient_pump, args=[1], text='Run pump_1', grid=[0,0], height=1, width=9)
# 		self.pump2_button = PushButton(self.nutrient_pumps_box, self.run_nutrient_pump, args=[2], text='Run pump_2', grid=[1,0], height=1, width=9)
# 		self.pump3_button = PushButton(self.nutrient_pumps_box, self.run_nutrient_pump, args=[3], text='Run pump_3', grid=[0,1], height=1, width=9)
# 		self.pump4_button = PushButton(self.nutrient_pumps_box, self.run_nutrient_pump, args=[4], text='Run pump_4', grid=[1,1], height=1, width=9)
# 		self.interaction_window.repeat(500, self.check_interactions)
# 		self.app.update()

# 	def check_interactions(self):
# 		if self.belle_mere.pump_running and not self.belle_mere.force_pause_pump:
# 			self.pause_pump_button.enable()
# 			self.restart_pump_button.disable()
# 		elif not self.belle_mere.pump_running:
# 			self.pause_pump_button.disable()
# 			self.restart_pump_button.enable()

# 	def pause_pump(self):
# 		nakama_utils.log_info("MANUAL 'PAUSE MAIN PUMP' CALLED")
# 		self.belle_mere.pause_pump()

# 	def restart_pump(self):
# 		nakama_utils.log_info("MANUAL 'RESTART MAIN PUMP' CALLED")
# 		self.belle_mere.run_main_pump()

# 	def emergency_stop_pump(self):
# 		nakama_utils.log_info("MANUAL 'STOP OF MAIN PUMP' CALLED")
# 		nakama_utils.set_emergency_stop_pump(True, self.belle_mere.program_id)

# 	def emergency_stop_capacity(self):
# 		nakama_utils.log_info("MANUAL 'MAX CAPACITY REACHED' CALLED")
# 		nakama_utils.set_emergency_stop_capacity(True, self.belle_mere.program_id)

# 	def exit_app(self):
# 		nakama_utils.set_emergency_stop_water_level_loops(True, self.belle_mere.program_id)
# 		sys.exit()


# 	def end_program_and_exit_app(self):
# 		self.monitoring_box.disable()
# 		# self.system_box.disable()
# 		self.instance_state_text = Text(self.system_box, text='APP SHUTDOWN \n This can take some time', height='fill', width='fill', align='bottom', color='red', size=14)
# 		self.app.update()
# 		nakama_utils.log_info("STARTED SHUTDOWN PROCESS", True)
# 		try:
# 			self.belle_mere.force_exit = True
# 			nakama_utils.set_emergency_stop_water_level_loops(True, self.belle_mere.program_id)
# 			nakama_utils.log_info('FORCE END PROGRAM')
# 			current_log = open('./logs/verbose_logs.txt', 'r', encoding='utf-8')
# 			stored_logs = open('./logs/stored_logs.txt', 'a', encoding='utf-8')
# 			stored_logs.write('\n{}'.format(current_log.read()))
# 			current_log.close()
# 			stored_logs.close()

# 			t = time.localtime()
# 			current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)

# 			old_log = open('./logs/logs.txt', 'w+', encoding='utf-8')
# 			old_log.write("--- NAKAMA-LOG {} ---\n".format(current_time))
# 			old_log.close()
# 			verbose_old_log = open('./logs/verbose_logs.txt', 'w+', encoding='utf-8')
# 			verbose_old_log.write("--- NAKAMA-LOG {} ---\n".format(current_time))
# 			verbose_old_log.close()
# 		except Exception as e:
# 			nakama_utils.log_error('hydroponic_ui.end_program_and_exit_app', 'FAILED TO EXIT APP CORRECTLY -- {}'.format(e))
# 		finally:
# 			state_sql = 'SELECT growlights_state, main_pump_state, nutrient_pumps_state FROM program_state WHERE id = {}'.format(self.belle_mere.program_id)
# 			inst_vals = hydroponic_db.query_table(state_sql)[0]
# 			if inst_vals[0] == nakama_store.SUCCESS:
# 				self.belle_mere.switches.switch_growlights(False)
# 			if inst_vals[1] == nakama_store.SUCCESS:
# 				self.belle_mere.switches.switch_main_pump(False)
# 			if inst_vals[2] == nakama_store.SUCCESS:
# 				self.belle_mere.switches.switch_nutrient_pump_1(False)
# 				self.belle_mere.switches.switch_nutrient_pump_2(False)
# 				self.belle_mere.switches.switch_nutrient_pump_3(False)
# 				self.belle_mere.switches.switch_nutrient_pump_4(False)
# 			if hasattr(self.belle_mere, 'main_pump_monitor'):
# 				while self.belle_mere.main_pump_monitor.is_alive():
# 					sleep(5)
# 			GPIO.cleanup()
# 			sys.exit()

# 	def update_log(self):
# 		current_log = open('./logs/logs.txt', 'r', encoding='utf-8')
# 		raw_text = current_log.read()
# 		last_log = raw_text[raw_text.rindex('NAKAMA'):]
# 		self.last_log_text.value = last_log
# 		current_log.close()

# 	def update_monitoring(self):
# 		self.readings_text.value = self.make_readings_text()
# 		self.program_text.value = self.make_program_text()

# 	def make_readings_text(self):
# 		readings = ''.join(('Last PH Reading: {},\n'.format(self.belle_mere.water_ph_sensor.read_last_ph()),
# 			'- At: {}\n'.format(self.belle_mere.water_ph_sensor.read_last_reading_time()),
# 			'Last EC Reading: {},\n'.format(self.belle_mere.water_ec_sensor.read_last_ec()),
# 			'- At: {}\n'.format(self.belle_mere.water_ec_sensor.read_last_reading_time()),
# 			'Last Temp_C Reading: {},\n'.format(self.belle_mere.water_temperature.read_last_rounded_celsius()),
# 			'- At: {}\n'.format(self.belle_mere.water_temperature.read_last_reading_time()),
# 			'Last Temp_F Reading: {},\n'.format(self.belle_mere.water_temperature.read_last_rounded_farenheit()),
# 			'- At: {}\n'.format(self.belle_mere.water_temperature.read_last_reading_time()),
# 			'Last W_flow Reading: {},\n'.format(self.belle_mere.water_flow_sensor.read_last_flow()),
# 			'- At: {}\n'.format(self.belle_mere.water_flow_sensor.read_last_reading_time())))
# 		return readings

# 	def make_program_text(self):
# 		sql = 'SELECT program_name, current_phase, has_failed, start_date, end_date FROM program_state WHERE id = {}'.format(self.belle_mere.program_id)
# 		program_state = hydroponic_db.query_table(sql)[0]
# 		readings = ''.join(('Program: {}\n'.format(program_state[0]),
# 			'ID: {}\n'.format( self.belle_mere.program_id),
# 			'Start DateTime: {}\n'.format(program_state[3]),
# 			'Current Phase: {}\n'.format(program_state[1]),
# 			'Program Has Failed: {}\n'.format('TRUE' if str(program_state[2]) == '1' else 'FALSE'),
# 			'End DateTime: {}\n'.format(program_state[4])))
# 		return readings
