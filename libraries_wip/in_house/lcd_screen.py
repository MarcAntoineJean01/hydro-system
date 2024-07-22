# lcd_screen.py

import sys
# sys.path is a list of absolute path strings
sys.path.append('/home/nakama01/Desktop/Hydro_system/libraries_wip/hd44780')
import lcddriver
from time import sleep
import nakama_utils
import nakama_store

class lcd_screen:

	def __init__(self, i2c, prog_id):
		self.program_id = prog_id
		if nakama_utils.get_instance_startup_state(self.program_id, 'i2c_instance') == nakama_store.SUCCESS:
			self.i2c = i2c
			self.lcd = lcddriver.lcd()
			self.detect_screen()
		else:
			head_mess = "FAILED TO START LCD SCREEN. MISSING DEPENDENCY "
			i2c_mess = "i2c_state: '{}' ".format(nakama_utils.get_instance_startup_state(self.program_id, 'i2c_instance'))
			mess = head_mess + i2c_mess
			nakama_utils.log_warning('lcd_screen.init', mess, True)

	def detect_screen(self):
		while True:
			while not self.i2c.get_instance().try_lock():
				try:
					addrss = [hex(device_address) for device_address in self.i2c.get_instance().scan()]
					nakama_utils.log_info(" i2c addresses: {}".format(addrss))
					for addrs in addrss:
						if addrs == '0x27':
							nakama_utils.log_info("LCD screen detected. you can proceed with lcd usage.")
							return True
						else:
							nakama_utils.log_info("LCD screen NOT detected. check the LCD screen connections.")
							return False
				finally:
					self.i2c.get_instance().unlock()
					nakama_utils.log_info("unlocked i2c")
					self.clean_print(5, "SUCCESSFULLY STARTED", "     LCD SCREEN     ", "  USER CAN PROCEED  ", " PRINTING TO SCREEN ")

	def clear_screen(self):
		self.lcd.lcd_clear()

	def switch_screen(self, state):
		st = "ON" if state else "OFF"
		self.lcd.lcd_backlight(st)


	def clean_print(self, t, str1, str2 = False, str3 = False, str4 = False):
		try:
			self.clear_screen()
			if str1:
				self.lcd.lcd_display_string(str1, 1)
				if len(str1) > 20:
					nakama_utils.log_warning('lcd_screen.clean_print', "LCD ERROR: STRING '{}' exceeds max 20 characters per line".format(str1), False)
			if str2:
				self.lcd.lcd_display_string(str2, 2)
				if len(str2) > 20:
					nakama_utils.log_warning('lcd_screen.clean_print', "LCD ERROR: STRING '{}' exceeds max 20 characters per line".format(str2), False)
			if str3:
				self.lcd.lcd_display_string(str3, 3)
				if len(str3) > 20:
					nakama_utils.log_warning('lcd_screen.clean_print', "LCD ERROR: STRING '{}' exceeds max 20 characters per line".format(str3), False)
			if str4:          
				self.lcd.lcd_display_string(str4, 4)
				if len(str4) > 20:
					nakama_utils.log_warning('lcd_screen.clean_print', "LCD ERROR: STRING '{}' exceeds max 20 characters per line".format(str4), False)
		except Exception  as e:
			mess = "COULDN'T PRINT TO LCD -- {}".format(e)
			nakama_utils.log_error('lcd_screen.clean_print', mess)
		finally:
			sleep(t)
			self.clear_screen()
			self.switch_screen(False)

	# prints values formatted to 'Name: Value' with k = name, v = value.
	# useful to cleanly print sensor values or test results.
	def clean_setting_print(self, t,k,v):
		if len(k) + len(v) > 18:
			try:
				self.clear_screen()
				self.lcd.lcd_display_string("{}:".format(k), 1)
				if len(k) > 20:
					nakama_utils.log_warning('lcd_screen.clean_setting_print', "LCD ERROR: STRING '{}' exceeds max 20 characters per line".format(k))
				self.lcd.lcd_display_string(v, 2)
			finally:
				sleep(t)
				self.clear_screen()
				self.switch_screen(False)
		else:
			try:
				self.clear_screen()
				self.lcd.lcd_display_string("{}: {}".format(k, v), 1)
			finally:
				sleep(t)
				self.clear_screen()
				self.switch_screen(False)