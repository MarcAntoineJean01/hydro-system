import requests

class Sensors_Apis:

	def __init__(self):
		try:
			self.dest=dest
		except Exception  as e:
			pass

	def test_call(self):
		# Define the API endpoint URL
		all_good=True
		url='http://localhost:4567/test_call'

		try:
			# Make a GET request to the API endpoint using requests.get()
			response = requests.get(url)

			# Check if the request was successful (status code 200)
			if response.status_code == 200:
				posts = response.json()
				if posts["test_result"]:
					print("SENSORS API REQUEST SUCCESS:", posts["test_result"])
				else:
					print('SENSORS API Error, test result', posts["test_result"])
					all_good=False
			else:
				print('SENSORS API Error:', response.status_code)
				all_good=False
		except Exception  as e:
			print("ERROR SENSORS API")
			print(e)
			all_good=False

		try:
			url='http://localhost:4567/water_ph'
			response = requests.get(url)

			if response.status_code == 200:
				posts = response.json()
				print("WATER PH REQUEST SUCCESS:", posts["value"])
			else:
				print('WATER PH Error:', response.status_code)
				all_good=False
		except Exception  as e:
			print("ERROR WATER PH")
			print(e)
			all_good=False

		try:
			url='http://localhost:4567/water_ec'
			response = requests.get(url)

			if response.status_code == 200:
				posts = response.json()
				print("WATER EC REQUEST SUCCESS:", posts["value"])
			else:
				print('WATER EC Error:', response.status_code)
				all_good=False
		except Exception  as e:
			print("ERROR WATER EC")
			print(e)
			all_good=False

		try:
			url='http://localhost:4567/water_temperature'
			response = requests.get(url)

			if response.status_code == 200:
				posts = response.json()
				print("WATER TEMP REQUEST SUCCESS:", posts["value"])
			else:
				print('WATER TEMP Error:', response.status_code)
				all_good=False
		except Exception  as e:
			print("ERROR WATER TEMP")
			print(e)
			all_good=False
		return all_good