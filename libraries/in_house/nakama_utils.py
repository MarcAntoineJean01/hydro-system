# nakama_utils.py

import time
import os
import traceback
import logging
import nakama_store
import nakama_default_locker
import hydroponic_db

from pushbullet import Pushbullet

import json
def get_locker_value(key):
    try:
        locker = open('nakama_locker.json')
        data = json.load(locker)
        locker.close()
        return data[key]
    except KeyError as ex:
        print("Couldn't find locker value, using store default for: {}".format(key))
        return getattr(nakama_default_locker, key)

pb = Pushbullet(get_locker_value("PUSHBULLET_KEY"))
mobile = pb.get_device(get_locker_value("PUSHBULLET_DEVICE"))

def now():
    return time.strftime("%d/%m/%Y-%H:%M:%S", time.localtime())

def take_picture(name):
    os.system ('libcamera-jpeg -o {}/../../pictures/{}.jpg'.format(os.path.dirname(__file__), name))

def push_to_mobile(head, body, message_type="note"):
    # # comment the next three lines to enable notifications to mobile
    # mess = "PUSH TO MOBILE DISABLED -- couldn't send message -- '{}'".format(head)
    # # log_warning('nakama_utils.push_to_mobile', mess, False)
    # return
    try:
        if message_type == "note":
            mobile.push_note(head, body)
        elif message_type == "pic":
            t = time.localtime()
            current_time = time.strftime("%d-%m-%Y-%H:%M:%S", t)
            pic_name = 'PIC-{}'.format(current_time)
            take_picture(pic_name)
            pic_path = '{}/../../pictures/{}.jpg'.format(os.path.dirname(__file__), pic_name)
            with open(pic_path, "rb", encoding='utf-8') as pic:
                file_data = pb.upload_file(pic, "{}.jpg".format(pic_name))

            mobile.push_file(**file_data, title=head, body=body)
    except Exception  as e:
        mess = "COULDN'T SEND MESSAGE  -- '{}' -- {}".format(message_type, e)
        log_warning('nakama_utils.push_to_mobile', mess, False)

def log_error(origin, error):
    text_logs = open_retry('{}/../../logs/logs.txt'.format(os.path.dirname(__file__)), 'a')
    t = time.localtime()
    current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
    level = "NAKAMA-ERROR"
    error_head = "|{}||{}||{}|".format(level, origin, current_time)
    error_body = traceback.format_exc()
    logging.error("{}\n{}".format(error_head, error), stack_info=True)
    text_logs.write("\n{}\n    {}\n".format(error_head, error_body))
    text_logs.close()
    verbose_text_logs = open_retry('{}/../../logs/logs.txt'.format(os.path.dirname(__file__)), 'a')
    verbose_text_logs.write("\n{}\n    {}\n".format(error_head, error_body))
    verbose_text_logs.close()
    push_to_mobile(error_head, error_body)

def log_info(mess, verbose=False):
    text_logs = open_retry('{}/../../logs/verbose_logs.txt'.format(os.path.dirname(__file__)), 'a')
    t = time.localtime()
    current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
    level = "NAKAMA-INFO"
    info_head = "|{}||{}|".format(level, current_time)
    message = "{} -- {}".format(info_head, mess)
    text_logs.write("\n{}\n    {}\n".format(info_head, mess))
    text_logs.close()
    if verbose:
        logging.info(message)

def log_warning(origin, warning, push_to_mob):
    text_logs = open_retry('{}/../../logs/logs.txt'.format(os.path.dirname(__file__)), 'a')
    t = time.localtime()
    current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
    level = "NAKAMA-WARNING"
    warning_head = "|{}||{}||{}|".format(level, origin, current_time)
    logging.warning("{}\n{}".format(warning_head, warning))
    text_logs.write("\n{}\n    {}\n".format(warning_head, warning))
    text_logs.close()
    verbose_text_logs = open_retry('{}/../../logs/logs.txt'.format(os.path.dirname(__file__)), 'a')
    verbose_text_logs.write("\n{}\n    {}\n".format(warning_head, warning))
    verbose_text_logs.close()
    if push_to_mob:
        push_to_mobile(warning_head, warning)


def open_retry(file_path, action):
    retries = 0
    while retries < 3:
        try:
            return open(file_path, action, encoding='utf-8')
        except Exception  as e:
            mess = "COULDN'T OPEN FILE  -- {} -- RETRYING -- {}".format(file_path, e)
            log_warning('open_retry', mess)
            retries += 1
        time.sleep(0.5)
    else:
        log_warning("open_retry", "NO MORE RETRIES FOR " + file_path)
        return open(file_path, action, encoding='utf-8')

def emergency_stop_water_level_loops(prog_id):
    try:
        sql = "SELECT emergency_stop_water_level_loops FROM system_monitoring WHERE program_id = {};".format(prog_id)
        res = True if hydroponic_db.query_table(sql)[0][0] == 1 else False
        return res
    except Exception as e:
        mess = "FAILED TO CHECK emergency_stop_water_level_loops -- {}".format(e)
        log_error('nakama_utils.emergency_stop_water_level_loops', mess)

def emergency_stop_pump(prog_id):
    try:
        sql = "SELECT emergency_stop_pump FROM system_monitoring WHERE program_id = {};".format(prog_id)
        res = True if hydroponic_db.query_table(sql)[0][0] == 1 else False
        return res
    except Exception as e:
        mess = "FAILED TO CHECK emergency_stop_pump -- {}".format(e)
        log_error('nakama_utils.emergency_stop_pump', mess)

def emergency_stop_capacity(prog_id):
    try:
        sql = "SELECT emergency_stop_capacity FROM system_monitoring WHERE program_id = {};".format(prog_id)
        res = True if hydroponic_db.query_table(sql)[0][0] == 1 else False
        return res
    except Exception as e:
        mess = "FAILED TO CHECK emergency_stop_capacity -- {}".format(e)
        log_error('nakama_utils.emergency_stop_capacity', mess)

def set_emergency_stop_water_level_loops(val, prog_id):
    try:
        q_val = 'TRUE' if val else 'FALSE'
        t = time.localtime()
        current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
        sql = "UPDATE system_monitoring SET emergency_stop_water_level_loops = {}, last_update = STR_TO_DATE('{}', '%d/%m/%Y-%T') WHERE program_id = {};".format(q_val, current_time, prog_id)
        hydroponic_db.update_table(sql)
    except Exception as e:
        mess = "FAILED TO SET emergency_stop_water_level_loops -- {}".format(e)
        log_error('nakama_utils.set_emergency_stop_water_level_loops', mess)

def set_emergency_stop_pump(val, prog_id):
    try:
        q_val = 'TRUE' if val else 'FALSE'
        t = time.localtime()
        current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
        sql = "UPDATE system_monitoring SET emergency_stop_pump = {}, last_update = STR_TO_DATE('{}', '%d/%m/%Y-%T') WHERE program_id = {};".format(q_val, current_time, prog_id)
        hydroponic_db.update_table(sql)
    except Exception as e:
        mess = "FAILED TO SET emergency_stop_pump -- {}".format(e)
        log_error('nakama_utils.set_emergency_stop_pump', mess)

def set_emergency_stop_capacity(val, prog_id):
    try:
        q_val = 'TRUE' if val else 'FALSE'
        t = time.localtime()
        current_time = time.strftime("%d/%m/%Y-%H:%M:%S", t)
        sql = "UPDATE system_monitoring SET emergency_stop_capacity = {}, last_update = STR_TO_DATE('{}', '%d/%m/%Y-%T') WHERE program_id = {};".format(q_val, current_time, prog_id)
        hydroponic_db.update_table(sql)
    except Exception as e:
        mess = "FAILED TO SET emergency_stop_capacity -- {}".format(e)
        log_error('nakama_utils.set_emergency_stop_capacity', mess)

def update_instance_startup_state(prog_id, inst, state):
    if inst == 'ads1115_instance':
        sql = "UPDATE program_state SET ads1115_instance_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'i2c_instance':
        sql = "UPDATE program_state SET i2c_instance_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'water_flow_sensor':
        sql = "UPDATE program_state SET water_flow_sensor_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'growlights':
        sql = "UPDATE program_state SET growlights_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'main_pump':
        sql = "UPDATE program_state SET main_pump_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'nutrient_pumps':
        sql = "UPDATE program_state SET nutrient_pumps_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'water_ec_sensor':
        sql = "UPDATE program_state SET water_ec_sensor_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'water_ph_sensor':
        sql = "UPDATE program_state SET water_ph_sensor_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    elif inst == 'water_temperature':
        sql = "UPDATE program_state SET water_temperature_state = '{}' WHERE id = {};".format(state, prog_id)
        hydroponic_db.update_table(sql)
    else:
        log_warning('nakama_utils.update_instance_startup_state', 'UNKNOWN INSTANCE NAME: {};'.format(inst), True)

def get_instance_startup_state(prog_id, inst):
    if inst == 'ads1115_instance':
        sql = "SELECT ads1115_instance_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'i2c_instance':
        sql = "SELECT i2c_instance_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'water_flow_sensor':
        sql = "SELECT water_flow_sensor_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'growlights':
        sql = "SELECT growlights_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'main_pump':
        sql = "SELECT main_pump_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'nutrient_pumps':
        sql = "SELECT nutrient_pumps_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'water_temperature':
        sql = "SELECT water_temperature_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'water_ph_sensor':
        sql = "SELECT water_ph_sensor_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    elif inst == 'water_ec_sensor':
        sql = "SELECT water_ec_sensor_state FROM program_state WHERE id = {};".format(prog_id)
        return hydroponic_db.query_table(sql)[0][0]
    else:
        log_warning('nakama_utils.get_instance_startup_state', 'UNKNOWN INSTANCE NAME: {};'.format(inst), True)

def avarage_value(values, limit=0):
    try:
        total = 0
        if limit == 0 or (limit != 0 and limit == len(values)):
            for i in range(0, len(values)):    
                total = total + values[i];
            avarage = total/len(values)
            if avarage:
                return round(avarage, 8)
            else:
                raise Exception('NAKAMA_UTILS ERROR. Failed to avarage values: "{}"'.format(values))
        elif limit < len(values):
            values = values[-limit]
            for i in range(0, len(values)):    
                total = total + values[i];
            avarage = total/limit
            if avarage:
                return round(avarage, 8)
            else:
                raise Exception('NAKAMA_UTILS ERROR. Failed to avarage values: "{}"'.format(values))
        else:
            log_warning('nakama_utils.avarage_value', 'Failed to avarage values, not enough values: limit: "{}", values: "{}"'.format(limit, values), True)
            return None
    except Exception as e:
        log_error('nakama_utils.avarage_value', e)
