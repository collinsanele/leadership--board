import requests



def doBatchRequest(symbols_arr, init_price_arr, date_added_arr):
	"""
	args: array of symbols, initial price array, date added array
	
	returns a list of dictionaries eg:
	[
		{'symbol': 'fb', 'companyName': 'facebook',
		'close': '26.0', 'previousClose': '25.10', 'initial_price': '23', 'date_added': '2021/6/2'} , ...
	]
	"""
	symbols = ",".join(symbols_arr)
	
	url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbols}&types=quote&token=pk_71f03934a0e845619ebc4d31de0dee6b'
	
	r = requests.get(url)
	result_arr = []
	result = r.json()
	result_keys = result.keys()
	#print(result)
	for index, key in enumerate(result_keys):
		obj = {}
		obj['symbol'] = result[key]["quote"]["symbol"]
		obj["company_name"] = result[key]["quote"]["companyName"]
		obj["current_price"] = result[key]["quote"]["close"] if result[key]["quote"]["close"] else result[key]["quote"]["iexClose"]
		obj["prev_close"] = result[key]["quote"]["previousClose"]
		obj["initial_price"] = init_price_arr[index]
		obj["date_added"] = date_added_arr[index]
		result_arr.append(obj)
		
	return result_arr
	


print(doBatchRequest(["fb", "tsla"], [10, 20], ["2021/6/2", "2021/6/1"]))
