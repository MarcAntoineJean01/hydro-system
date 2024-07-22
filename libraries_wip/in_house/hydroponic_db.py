# hydroponic_db.py

# Module Imports
import mysql.connector
import nakama_store
import nakama_utils
import sys

def create_table(sql):
	try:
		conn = mysql.connector.connect(
			user=nakama_utils.get_locker_value("DB_USER"),
			password=nakama_utils.get_locker_value("DB_PASSWORD"),
			host=nakama_utils.get_locker_value("DB_HOST"),
			port=nakama_utils.get_locker_value("DB_PORT"),
			database=nakama_utils.get_locker_value("DATABASE")
		)
	except mysql.connector.Error as e:
		nakama_utils.log_error('hydroponic_db.create_table' , f"Error connecting to MariaDB Platform: {e}")
	try:
		cur = conn.cursor()
		cur.execute(sql)
		nakama_utils.log_warning('CREATING MISSING TABLE', sql, True)
	except Exception as e:
		mess = "FAILED TO CREATE TABLE -- SQL: '{}' -- ERROR: '{}'".format(sql, e)
		nakama_utils.log_error('hydroponic_db.create_table', mess)
	finally:
		cur.close()
		conn.close()

def create_db(sql):
	try:
		conn = mysql.connector.connect(
			user=nakama_utils.get_locker_value("DB_USER"),
			password=nakama_utils.get_locker_value("DB_PASSWORD"),
			host=nakama_utils.get_locker_value("DB_HOST"),
			port=nakama_utils.get_locker_value("DB_PORT"),
		)
	except mysql.connector.Error as e:
		nakama_utils.log_error('hydroponic_db.create_db' , f"Error connecting to MariaDB Platform: {e}")
	try:
		cur = conn.cursor()
		cur.execute(sql)
		nakama_utils.log_warning('CREATING MISSING DATABASE', sql, True)
	except Exception as e:
		mess = "FAILED TO CREATE DATABASE -- SQL: '{}' -- ERROR: '{}'".format(sql, e)
		nakama_utils.log_error('hydroponic_db.create_db', mess)
	finally:
		cur.close()
		conn.close()

def query_table(sql):
	try:
		conn = mysql.connector.connect(
			user=nakama_utils.get_locker_value("DB_USER"),
			password=nakama_utils.get_locker_value("DB_PASSWORD"),
			host=nakama_utils.get_locker_value("DB_HOST"),
			port=nakama_utils.get_locker_value("DB_PORT"),
			database=nakama_utils.get_locker_value("DATABASE")
		)
	except mysql.connector.Error as e:
		nakama_utils.log_error('hydroponic_db.query_table' , f"Error connecting to MariaDB Platform: {e}")
	try:
		cur = conn.cursor(buffered=True)
		cur.execute(sql)
		res = cur.fetchall()
	except Exception as e:
		mess = "FAILED TO QUERY TABLE -- SQL: '{}' -- ERROR: '{}'".format(sql, e)
		nakama_utils.log_error('hydroponic_db.query_table', mess)
	finally:
		cur.close()
		conn.close()
		return res

def update_table(sql):
	try:
		conn = mysql.connector.connect(
			user=nakama_utils.get_locker_value("DB_USER"),
			password=nakama_utils.get_locker_value("DB_PASSWORD"),
			host=nakama_utils.get_locker_value("DB_HOST"),
			port=nakama_utils.get_locker_value("DB_PORT"),
			database=nakama_utils.get_locker_value("DATABASE")
		)
	except mysql.connector.Error as e:
		nakama_utils.log_error('hydroponic_db.update_table' , f"Error connecting to MariaDB Platform: {e}")
	try:
		cur = conn.cursor(buffered=True)
		cur.execute(sql)
	except Exception as e:
		mess = "FAILED TO UPDATE TABLE -- SQL: '{}' -- ERROR: '{}'".format(sql, e)
		nakama_utils.log_error('hydroponic_db.update_table', mess)
	finally:
		conn.commit()
		cur.close()
		conn.close()

def insert_and_get_id(sql):
	try:
		conn = mysql.connector.connect(
			user=nakama_utils.get_locker_value("DB_USER"),
			password=nakama_utils.get_locker_value("DB_PASSWORD"),
			host=nakama_utils.get_locker_value("DB_HOST"),
			port=nakama_utils.get_locker_value("DB_PORT"),
			database=nakama_utils.get_locker_value("DATABASE")
		)
	except mysql.connector.Error as e:
		nakama_utils.log_error('hydroponic_db.insert_and_get_id' , f"Error connecting to MariaDB Platform: {e}")
	try:
		cur = conn.cursor(buffered=True)
		cur.execute(sql)
		res = cur.lastrowid
	except Exception as e:
		mess = "FAILED TO INSERT NEW ROW -- SQL: '{}' -- ERROR: '{}'".format(sql, e)
		nakama_utils.log_error('hydroponic_db.insert_and_get_id', mess)
	finally:
		conn.commit()
		cur.close()
		conn.close()
		return res

def table_exists(table_name):
	try:
		conn = mysql.connector.connect(
			user=nakama_utils.get_locker_value("DB_USER"),
			password=nakama_utils.get_locker_value("DB_PASSWORD"),
			host=nakama_utils.get_locker_value("DB_HOST"),
			port=nakama_utils.get_locker_value("DB_PORT"),
			database=nakama_utils.get_locker_value("DATABASE")
		)
	except mysql.connector.Error as e:
		nakama_utils.log_error('hydroponic_db.table_exists' , f"Error connecting to MariaDB Platform: {e}")
	try:
		cur = conn.cursor()
		sql = "SELECT EXISTS ( SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME = '{}');".format(table_name)
		cur.execute(sql)
	except Exception as e:
		mess = "FAILED TO CHECK IF TABLE '{}' EXISTS  -- ERROR: '{}'".format(table_name, e)
		nakama_utils.log_error('hydroponic_db.table_exists', mess)
	finally:
		for tables in cur:
			exists = tables[0] > 0
		cur.close()
		conn.close()
		if exists == False:
			nakama_utils.log_info("MISSING TABLE '{}', WILL CREATE TABLE.".format(table_name))
		elif exists == True:
			nakama_utils.log_info("FOUND TABLE '{}', PROCEED WITH USAGE.".format(table_name))
		return exists

def db_exists(db_name):
	try:
		conn = mysql.connector.connect(
			user=nakama_utils.get_locker_value("DB_USER"),
			password=nakama_utils.get_locker_value("DB_PASSWORD"),
			host=nakama_utils.get_locker_value("DB_HOST"),
			port=nakama_utils.get_locker_value("DB_PORT"),
		)
	except mysql.connector.Error as e:
		nakama_utils.log_error('hydroponic_db.db_exists' , f"Error connecting to MariaDB Platform: {e}")
	try:
		cursor = conn.cursor()
		sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}';".format(db_name)
		cursor.execute(sql)
		row_count = cursor.fetchall()
	except Exception as e:
		mess = "FAILED TO CHECK IF DATABASE '{}' EXISTS  -- ERROR: '{}'".format(db_name, e)
		nakama_utils.log_error('hydroponic_db.db_exists', mess)
	finally:
		if len(row_count) > 0:
			exists = True
		else:
			exists = False
		cursor.close()
		conn.close()
		if exists == False:
			nakama_utils.log_info("MISSING DATABASE '{}', WILL CREATE DATABASE.".format(db_name))
		elif exists == True:
			nakama_utils.log_info("FOUND DATABASE '{}', PROCEED WITH USAGE.".format(db_name))
		return exists

