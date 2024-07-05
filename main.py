# # import sys
# # sys.path.append('libraries/in_house')
# import hydroponic_ui
# # import nakama_store
# # if sys.platform == "linux" or sys.platform == "linux2":
# # 	# linux
# # 	pass
# # elif sys.platform == "darwin" or sys.platform == "win32":
# # 	# OS X or # Windows...
# # 	import nakama_mocker
# # 	GPIO = nakama_mocker.Fake_GPIO()
# # elif sys.platform == "RASP_PI":
# # 	import RPi.GPIO as GPIO

# try:
# 	new_ui = hydroponic_ui.UI()
# except Exception as e:
# 	state_sql = 'SELECT growlights_state, main_pump_state, nutrient_pumps_state FROM program_state WHERE id = {}'.format(new_ui.belle_mere.program_id)
# 	inst_vals = hydroponic_db.query_table(state_sql)[0]
# 	if inst_vals[0] == nakama_store.SUCCESS:
# 		new_ui.belle_mere.switches.switch_growlights(False)
# 	if inst_vals[1] == nakama_store.SUCCESS:
# 		new_ui.belle_mere.switches.switch_main_pump(False)
# 	if inst_vals[2] == nakama_store.SUCCESS:
# 		new_ui.belle_mere.switches.switch_nutrient_pump_1(False)
# 		new_ui.belle_mere.switches.switch_nutrient_pump_2(False)
# 		new_ui.belle_mere.switches.switch_nutrient_pump_3(False)
# 		new_ui.belle_mere.switches.switch_nutrient_pump_4(False)
# 	GPIO.cleanup()
# 	print(e)
# 	nakama_utils.log_error('UI INSTANCE', str(e))
# 	print("ERROR BEFORE UI COMPLETE")
# finally:
# 	print("UI COMPLETE")

import ui_shell

ui_instance = ui_shell.UI_Shell(True)