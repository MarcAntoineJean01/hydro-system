# i2c_instance.py

import board
import nakama_utils
import nakama_store

class i2c_instance:

	def __init__(self, prog_id):
		self.program_id = prog_id
		try:
			nakama_utils.update_instance_startup_state(self.program_id, 'i2c_instance', nakama_store.PENDING)
			self.i2c = board.I2C()
			nakama_utils.update_instance_startup_state(self.program_id, 'i2c_instance', nakama_store.SUCCESS)
		except Exception  as e:
			nakama_utils.update_instance_startup_state(self.program_id, 'i2c_instance', nakama_store.FAILED)
			mess = "COULDN'T SETUP I2C -- {}".format(e)
			nakama_utils.log_error('i2c_instance.init', mess)

	def get_instance(self):
		return self.i2c