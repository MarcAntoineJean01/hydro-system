class Fake_GPIO:
    def __init__(self):
        self.BCM = None
        self.OUT = False
        self.IN = True
        self.LOW = False
        self.HIGH = True
    def cleanup(self):
        pass
    def output(self, pin_number, pin_mode):
        pass
    def setmode(self, mode):
        pass
    def setup(self, pin_number, pin_mode):
        pass

class Fake_ads1115_instance:

    def __init__(self, prog_id):
        pass

    def get_instance(self):
        return None

    def ads1115_instance(self, prog_id):
        return None

    def setGain(self):
        pass

    def readVoltage(self, value):
        return 11

class Fake_i2c_instance:
    def __init__(self, prog_id):
        pass

    def get_instance(self):
        return None

    def i2c_instance(self, prog_id):
        pass

class Fake_lcd_screen:

    def __init__(self, i2c, prog_id):
        pass

    def detect_screen(self):
        return True

    def clear_screen(self):
        pass

    def switch_screen(self, state):
        pass

    def lcd_screen(self, i2c, prog_id):
        pass

    def clean_print(self, t, str1, str2 = False, str3 = False, str4 = False):
        pass

    # prints values formatted to 'Name: Value' with k = name, v = value.
    # useful to cleanly print sensor values or test results.
    def clean_setting_print(self, t,k,v):
        pass

class Fake_water_flow_sensor:

    def __init__(self, prog_id):
        pass

    def read_flow(self, count, start_counter):
        return 0.3

    def read(self):
        return self.read_flow(water_flow_count, start_counter)

    def read_last_reading_time(self):
            return None

    def read_last_flow(self):
            return None

    def read_last_readings(self):
        return [0.3, 0.5, 0.1]

    def water_flow_sensor(self, prog_id):
        pass

    def create_water_flow_readings_table(self):
        hydroponic_db.create_table("CREATE TABLE water_flow_readings ("
            "  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
            "  reading_date DATETIME NOT NULL,"
            "  reading_value float(10,8) NOT NULL"
            ") ENGINE='InnoDB'")

class Fake_water_level_sensors:
    def __init__(self,  prog_id):
        pass

    def bottom_water_level_read(self):
        return False

    def top_water_level_read(self):
        return False

    def bottom_water_level_loop(self):
        pass

    def top_water_level_loop(self):
        pass

    def start_bottom_water_level_monitor(self):
        pass

    def start_top_water_level_monitor(self):
        pass

    def get_top_water_level_monitor(self):
        return self.top_water_level_monitor

    def get_bottom_water_level_monitor(self):
        return self.bottom_water_level_monitor

    def water_level_sensors(self, prog_id):
        pass

    def create_bottom_water_level_state_table(self):
        hydroponic_db.create_table("CREATE TABLE bottom_water_level_state ("
            "  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
            "  state_date DATETIME NOT NULL,"
            "  state_value BOOLEAN NOT NULL"
            ") ENGINE='InnoDB'")

    def create_top_water_level_state_table(self):
        hydroponic_db.create_table("CREATE TABLE top_water_level_state ("
            "  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
            "  state_date DATETIME NOT NULL,"
            "  state_value BOOLEAN NOT NULL"
            ") ENGINE='InnoDB'")

class Fake_water_temperature:

    def __init__(self, prog_id):
        pass

    def water_temperature(self, prog_id):
        return None

    def sensor(self):
        return [11]

    def read(self, ds18b20):
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
        return 25

    def read_last_farenheit(self):
        return 76

    def read_last_rounded_celsius(self):
        return 25

    def read_last_rounded_farenheit(self):
        return 76

    def read_last_readings(self):
        return [25, 76], [25, 76]

    def read_last_reading_time(self):
        return "22:00:00"

    def create_water_temperature_readings_table(self):
        hydroponic_db.create_table("CREATE TABLE water_temperature_readings ("
            "  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
            "  reading_date DATETIME NOT NULL,"
            "  reading_value float(10,8) NOT NULL"
            ") ENGINE='InnoDB'")

class Fake_water_ec_sensor:

    def __init__(self, ads1115, water_temperature, prog_id):
        pass

    def reset(self):
        pass

    def begin(self):
        pass

    def setup(self):
        pass

    def calibration(self):
        pass

    def calibration1413(self):
        pass

    def calibration1288(self):
        pass

    def read(self):
        return 11

    def read_last_reading_time(self):
        return "22:00:00"

    def read_last_ec(self):
        return 11
    def read_last_readings(self):
        return [11, 22, 33]

    def create_water_ec_readings_table(self):
        hydroponic_db.create_table("CREATE TABLE water_ec_readings ("
            "  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
            "  reading_date DATETIME NOT NULL,"
            "  reading_value float(10,8) NOT NULL"
            ") ENGINE='InnoDB'")

    def water_ec_sensor(self, ads1115, water_temp, prog_id):
        return None

class Fake_water_ph_sensor:

    def __init__(self, ads1115, water_temperature, prog_id):
        pass

    def reset(self):
        pass

    def begin(self):
        pass

    def setup(self):
        pass

    def calibration(self):
        pass

    def calibration7(self):
        pass

    def calibration4(self):
        pass

    def read(self):
        return 11

    def read_last_reading_time(self):
        return "22:00:00"

    def read_last_ph(self):
        return 11
    def read_last_readings(self):
        return [11, 22, 33]

    def create_water_ph_readings_table(self):
        hydroponic_db.create_table("CREATE TABLE water_ph_readings ("
            "  id int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,"
            "  reading_date DATETIME NOT NULL,"
            "  reading_value float(10,8) NOT NULL"
            ") ENGINE='InnoDB'")

    def water_ph_sensor(self, ads1115, water_temp, prog_id):
        return None

class A4988Nema:
    def __init__(self):
        pass
    def motor_go(self, bool, string , int, float, other_bool, other_float):
        pass

class Fake_RpiMotorLib:
    def __init__(self):
        pass
    def A4988Nema(self, direction, step, micro_steps_pins, model):
        return A4988Nema()
