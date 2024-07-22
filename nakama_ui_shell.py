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
class UI_Shell:

	def __init__(self, remote_sensors=False):
		try:
			self.remote_sensors=remote_sensors
			self.app=App(title="My app", width=800, height=480)
			self.app.full_screen=True if sys.platform == "RASP_PI" else False
			self.welcome_screen(False)

			self.app.display()
		except Exception  as e:
			print(e)
			print("something went wrong with UI_Shell.__init__()")
			sys.exit()

#SCREENS
	def welcome_screen(self, dest=True):
		if dest:
			self.title_box.destroy()
		self.title_box=TitleBox(self.app, text="Welcome", layout="auto", height='fill', width='fill')

		welcome_text="Hello and welcome!"
		self.welcome_text=Text(self.title_box, text=welcome_text)
		self.setup_button=PushButton(self.title_box, self.start_setup, text='Setup')
		self.locker_button=PushButton(self.title_box, self.locker_screen, text='Locker')
		self.exit_button=PushButton(self.title_box, self.exit_app, text='Exit')

	def setup_screen(self):
		self.title_box.destroy()

		self.title_box=TitleBox(self.app, text="Setup", layout="auto", height='fill', width='fill')
		self.packages_state_text=Text(self.title_box, text='Checking packages: WORKING', color='red', size=14)
		self.libraries_state_text=Text(self.title_box, text='Checking libraries: WAITING', color='yellow', size=14)
		self.sensors_state_text=Text(self.title_box, text='Checking sensors: WAITING', color='yellow', size=14)
		self.database_state_text=Text(self.title_box, text='Checking database: WAITING', color='yellow', size=14)
		self.app.update()

		self.check_packages()

		self.libraries_state_text.value='Checking libraries: WORKING'
		self.libraries_state_text.text_color='red'
		self.app.update()

		self.check_libraries()

		self.sensors_state_text.value='Checking sensors: WORKING'
		self.sensors_state_text.text_color='red'
		self.app.update()

		self.check_sensors()

		self.database_state_text.value='Checking sensors: WORKING'
		self.database_state_text.text_color='red'
		self.app.update()

		self.check_database()

		self.app.update()
		self.exit_app()

	def locker_screen(self):
		self.title_box.destroy()

		self.title_box = TitleBox(self.app, text="Locker", layout="auto", height='fill', width='fill')
		self.DB_USER_box = TitleBox(self.title_box, text="db user", layout="grid", width='fill')
		self.update_DB_USER_input_box = TextBox(self.DB_USER_box, text=self.get_current_param('DB_USER'),  width=40, grid=[1, 0])
		self.update_DB_USER_button = PushButton(self.DB_USER_box, lambda: self.update_locker('DB_USER', self.update_DB_USER_input_box.value), text='Update DB_USER', width=40, grid=[0,0])
		self.DB_PASSWORD_box = TitleBox(self.title_box, text="db password", layout="grid", width='fill')
		self.update_DB_PASSWORD_input_box = TextBox(self.DB_PASSWORD_box, text=self.get_current_param('DB_PASSWORD'), width=40, hide_text=True, grid=[1, 0])
		self.update_DB_PASSWORD_button = PushButton(self.DB_PASSWORD_box, lambda: self.update_locker('DB_PASSWORD', self.update_DB_PASSWORD_input_box.value), text='Update DB_PASSWORD', width=40, grid=[0,0])
		self.DB_HOST_box = TitleBox(self.title_box, text="db host", layout="grid", width='fill')
		self.update_DB_HOST_input_box = TextBox(self.DB_HOST_box, text=self.get_current_param('DB_HOST'), width=40, grid=[1, 0])
		self.update_DB_HOST_button = PushButton(self.DB_HOST_box, lambda: self.update_locker('DB_HOST', self.update_DB_HOST_input_box.value), text='Update DB_HOST', width=40, grid=[0,0])
		self.DB_PORT_box = TitleBox(self.title_box, text="db port", layout="grid", width='fill')
		self.update_DB_PORT_input_box = TextBox(self.DB_PORT_box, text=self.get_current_param('DB_PORT'), width=40, grid=[1, 0])
		self.update_DB_PORT_button = PushButton(self.DB_PORT_box, lambda: self.update_locker('DB_PORT', self.update_DB_PORT_input_box.value), text='Update DB_PORT', width=40, grid=[0,0])
		self.DATABASE_box = TitleBox(self.title_box, text="database", layout="grid", width='fill')
		self.update_DATABASE_input_box = TextBox(self.DATABASE_box, text=self.get_current_param('DATABASE'), width=40, grid=[1, 0])
		self.update_DATABASE_button = PushButton(self.DATABASE_box, lambda: self.update_locker('DATABASE', self.update_DATABASE_input_box.value), text='Update DATABASE', width=40, grid=[0,0])
		self.SENSORS_ENDPOINT_box = TitleBox(self.title_box, text="sensors endpoint", layout="grid", width='fill')
		self.update_SENSORS_ENDPOINT_input_box = TextBox(self.DATABASE_box, text=self.get_current_param('SENSORS_ENDPOINT'), width=40, grid=[1, 0])
		self.update_SENSORS_ENDPOINT_button = PushButton(self.DATABASE_box, lambda: self.update_locker('SENSORS_ENDPOINT', self.update_SENSORS_ENDPOINT_input_box.value), text='Update SENSORS_ENDPOINT', width=40, grid=[0,0])

		self.go_back_button = PushButton(self.title_box, self.welcome_screen, text='Go Back', width=40,  align='bottom')
		self.app.update()

#POPUPS
	def start_setup(self):
		start_setup=self.app.yesno("Start Setup?", "You're about to start the setup. this process will check for missing libraries and packages and install them if needed.")
		if start_setup == True:
		    self.setup_screen()
		else:
		    pass

#METHODS
	def exit_app(self):
		sys.exit()

	def check_packages(self):
		try:
			all_good=True
			print("checking packages")
			data=subprocess.check_output(["pip", "list", "--format", "json"])
			parsed_results = json.loads(data)

			for pack in nakama_dependency_list.packages:
				if any(installed["name"] == pack[0] for installed in parsed_results): 
					print(f"done checking {pack[0]}")
				else:
					all_good=False
					print(f"couldn't find package {pack[0]}, attempting install.")
					cmd=f"pip install {pack[0]}"
					open_process = subprocess.Popen(shlex.split(cmd))
					open_process.wait()
					if open_process.returncode != 0:
						pass
					else:
						all_good=True

			if all_good:
				self.packages_state_text.value='Checking packages: DONE'
				self.packages_state_text.text_color='green'
				print("done checking packages")
			else:
				new_data = subprocess.check_output(["pip", "list", "--format", "json"])
				new_parsed_results = json.loads(new_data)

				for pack in nakama_dependency_list.packages:
					if any(installed["name"] == pack[0] for installed in new_parsed_results): 
						pass
					else:
						raise Exception(f"package {pack[0]} still missing, aborting install.")
				self.packages_state_text.value='Checking packages: FAILED'
				self.packages_state_text.text_color='black'
				print("failed packages install")
		except Exception as e:
			self.packages_state_text.value='Checking packages: FAILED'
			self.packages_state_text.text_color='black'
			print(e)
			print("something wrong while checking packages, call for help!")

	def check_libraries(self):
		try:
			all_good=True
			print("checking libraries")
			for lib in nakama_dependency_list.libraries:
				if os.path.isdir(f"libraries_wip/{lib}"):
					print(f"done checking {lib}")
				else:
					print(f"couldn't find libraries {lib}, attempting download.")
					cmd = f"git restore libraries_wip/{lib}"
					open_process = subprocess.Popen(shlex.split(cmd))
					open_process.wait()
					if open_process.returncode != 0:
						all_good=False
						print(f"failed to install {lib}")
						try:
							if os.path.isdir(f"libraries_wip/{lib}"):
								cmd = f"rmdir libraries_wip/{lib} -r"
								open_process = subprocess.Popen(shlex.split(cmd))
								open_process.wait()
						except Exception as e:
							print(e)
					else:
						print(f"done installing {lib}")
			if all_good:
				self.libraries_state_text.value='Checking libraries: DONE'
				self.libraries_state_text.text_color='green'
				print("done checking libraries")
				print("appending in_house directory to sys.path")
				sys.path.append('libraries_wip/in_house')
			else:
				self.libraries_state_text.value='Checking libraries: FAILED'
				self.libraries_state_text.text_color='black'
				print("failed libraries install")
		except Exception as e:
			self.libraries_state_text.value='Checking libraries: FAILED'
			self.libraries_state_text.text_color='black'
			print(e)
			print("something wrong while checking libraries, call for help!")

	def check_sensors(self):
		try:
			all_good=True
			if self.remote_sensors:
				#test sensors api
				import sensors_api
				# self.sensors_api=sensors_api.Sensors_Apis()
				self.s_api=sensors_api.Sensors_Apis()
				call=self.s_api.test_call()
				if call is False:
					all_good=False
				else:
					print("successfully tested sensors api")
			else:
				#test sensors on pie
				pass
			if all_good:
				self.sensors_state_text.value='Checking sensors: DONE'
				self.sensors_state_text.text_color='green'
				print("done checking sensors")
			else:
				self.sensors_state_text.value='Checking sensors: FAILED'
				self.sensors_state_text.text_color='black'
		except Exception as e:
			self.sensors_state_text.value='Checking sensors: FAILED'
			self.sensors_state_text.text_color='black'
			print(e)
			print("something wrong while checking sensors, call for help!")

	def check_database(self):
		try:
			all_good=True
			if all_good:
				self.database_state_text.value='Checking database: DONE'
				self.database_state_text.text_color='green'
				print("done checking database")
			else:
				self.database_state_text.value='Checking database: FAILED'
				self.database_state_text.text_color='black'
		except Exception as e:
			self.database_state_text.value='Checking database: FAILED'
			self.database_state_text.text_color='black'
			print(e)
			print("something wrong while checking database, call for help!")


	def update_locker(self, key, value):
		if isinstance(key, str) is False or isinstance(value, str) is False or key == '':
			print("Variable input error, Key: {}, Value: {}".format(key, value))
		else:
			try:
				# Opening JSON file
				old_locker = open('nakama_locker.json')
				data = json.load(old_locker)
				old_locker.close()
				if value != '':
					data["{}".format(key)] = value
					nakama_locker = open("nakama_locker.json", "w")
					nakama_locker.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
					nakama_locker.close()
					print("Replaced {} in nakama_locker.json".format(key))
				elif data["{}".format(key)] is None:
					raise KeyError
				else:
					print("Variable input error, Key: {}, Value: {}".format(key, value))
			except KeyError as ex:
				print("'Missing Key:{}".format(ex))
				data["{}".format(key)] = getattr(nakama_store, key)
				# Writing to nakama_locker.json
				broken_locker = open("nakama_locker.json", "w")
				broken_locker.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
				broken_locker.close()
				print("added {} = {} to nakama_locker.json".format(key, value))
			except Exception  as ex:
				template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				message = template.format(type(ex).__name__, ex.args)
				print(message)
				sys.exit()

	def get_current_param(self, key):
		try:
			locker = open('nakama_locker.json')
			data = json.load(locker)
			locker.close()
			print(data["{}".format(key)])
			value = data["{}".format(key)]
			if value is not None:
				return value
			else:
				raise KeyError
		except KeyError as ex:
				print("No value found for {}, using default setting".format(key))
				return getattr(nakama_store, key)
		except Exception  as ex:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			print(message)
			print(ex)
			return None
