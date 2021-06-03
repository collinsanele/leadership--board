
import requests
from datetime import datetime, timedelta
import time
from collections import Counter, OrderedDict
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True)
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)

    
    def __str__(self):
    	return f"{self.user_id}"
    
    @staticmethod	
    def get_user(userId):
    	'''
    	Gets a user by userId
    	'''
    	user = User.query.filter(User.user_id==str(userId))
    	return user
    	
    @staticmethod
    def is_user(userId):
    	'''
    	checks if user exists with userId
    	'''
    
    	return bool(User.query.filter_by(user_id=str(userId)).all())
    	
    	
    @staticmethod
    def get_all_users():
    	'''
    	gets all user ids
    	'''
    	users = [user.user_id for user in User.query.all()]
    	return {"users": users}
    	
    	
    @staticmethod
    def add_user(userId):
    	"""
    	adds a user to the database using userId
    	"""
    	has_user = User.is_user(userId)
    	if has_user == False:
    		user = User(user_id=str(userId))
    		try:
    			db.session.add(user)
    			db.session.commit()
    			return {"status": f"{userId} created successfully"}
    		except Exception as e:
    			db.session.rollback()
    			print(e)
    			return {"status": f"There was a problem adding {userId}"}
    	else:
    		print(f"{userId} already exists")
    		return {"status": f"{userId} already exists"}
    
    
    @staticmethod
    def delete_user(userId):
    	"""
    	deletes a user from the database using userId
    	"""
    	user_exists = User.is_user(userId)
    	if user_exists:
    		user = User.get_user(userId=userId)
    		try:
    			user.delete()
    			db.session.commit()
    			return {"status": f"{userId} removed successfully"}
    		except Exception as e:
    			db.session.rollback()
    			print(e)
    			return {"status": f"There was a problem removing {userId}"}
    	else:
    		print(f"{userId} does not  exist")
    		return {"status": f"{userId} does not exist"}
    
    @staticmethod
    def edit_user(userId, newUserId):
    	'''
    	edits ther old userId with the newUserId
    	'''
    	user_exists = User.is_user(userId=userId)
    	if user_exists:
    		user = User.get_user(userId=userId)
    		try:
    			user.delete()
    			new_user = User(user_id=str(newUserId))
    			db.session.add(new_user)
    			db.session.commit()
    			return {"status": f"{userId} was replaced with {newUserId} successfully"}
    		except Exception as e:
    			print(e)
    			return {"status": f"There was an error editing {userId}"}
    	else:
    			return {"status": f"{userId} does not exist in the database"}
    			
    @staticmethod
    def get_user_portfolios(userId):
        '''
        gets all portfolios for a userId
        '''
        symbols_list = []
        user_exists = User.is_user(userId=userId)
        if user_exists:
            user = User.get_user(userId=userId).first()
            for item in user.portfolios:
            	obj = {}
            	obj["symbol"] = item.symbol
            	obj["initial_price"] = float(item.initial_price)
            	obj["date_added"] = item.date_added
            	obj["company_name"] = item.company_name
            	symbols_list.append(obj)
            return {"symbols": symbols_list}
        return {"status": f"{userId} does not exist"}
    			
  
    			
class DeletedPortfolio(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(30), unique=False)
	initial_price = db.Column(db.Numeric, unique=False)
	date_deleted = db.Column(db.DateTime, default=datetime.utcnow)
	company_name = db.Column(db.String(120))
	_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  	
	
	@staticmethod
	def add_to_deletedportfolio(portfolio_item, userId):
		deleted_item = DeletedPortfolio(initial_price=portfolio_item.initial_price, symbol=portfolio_item.symbol,
_user_id=userId, company_name=portfolio_item.company_name)
		try:
			db.session.add(deleted_item)
			db.session.commit()
			print("Added to DeletedPortfolio successfully")
		except Exception as e:
			db.session.rollback()
			  		  			  			  			  			
    			  			  			  			  	
class Portfolio(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(30), unique=False)
	initial_price = db.Column(db.Numeric, unique=False)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	company_name = db.Column(db.String(120))
	_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        
		
	@staticmethod
	def has_symbol(userId, symbol):
		'''
		checks if a symbol exists in a portfolio
		'''
		user = User.get_user(userId=str(userId)).first()
		for item in user.portfolios:
			if item.symbol == symbol:
				return True
		return False 
		
		
	@staticmethod
	def doBatchRequest(symbols_arr, init_price_arr, date_added_arr):
		symbols = ",".join(symbols_arr)
	
		url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbols}&types=quote&token=pk_71f03934a0e845619ebc4d31de0dee6b'
		
		try:
			r = requests.get(url)
			result_arr = []
			result = r.json()
			result_keys = result.keys()
		except Exception:
			return {"status": "An error occured"}

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
		
		
	@staticmethod
	def getPriceAndCompanyName(symbol):
		'''
		gets iexClose price and company 
		name and prev_close price from iexapi
		'''
		url = f"https://cloud.iexapis.com/stable/stock/{str(symbol)}/quote?token=pk_71f03934a0e845619ebc4d31de0dee6b"

		try:
			r = requests.get(url)
			close_price = r.json()["iexClose"]
			company_name = r.json()["companyName"]
			prev_close = r.json()["previousClose"]
			return [close_price, company_name, prev_close]

		except Exception as e:
			return "symbol not found"
    
    	
	@staticmethod
	def add_to_portfolio(userId, symbol):
		'''
		adds a symbol to portfolio 
		'''
		user_exists = User.is_user(userId=userId)
		if user_exists:
			try:
				user = User.get_user(userId=userId).first()
				symbols = [item.symbol.lower() for item in user.portfolios]
				if symbol.lower() not in symbols:
					initial_price, company_name, prev_close = Portfolio.getPriceAndCompanyName(symbol=symbol)
					if type(initial_price) !=float:
						return {"status": f"{symbol} not found"}
					portfolio = Portfolio(symbol=str(symbol),  initial_price=initial_price, _user_id=user.id,
					company_name=company_name)
					db.session.add(portfolio)
					db.session.commit()
					return {"status": f"{symbol} was added successfully to the portfolio for user with userId of {userId} "}
				return {"status": f"{symbol} already exist in portfolio in user with userId {userId}"}
				
			except Exception as e:
				print(e)
				db.session.rollback()
				return {"status": f"There was a problem adding {symbol} to the database"}
		return {"status": f"{userId} does not exist"}
				
				
	@staticmethod
	def edit_portfolio(userId, symbol, newSymbol):
		user_exists = User.is_user(userId=userId)
		if user_exists:
			if Portfolio.has_symbol(userId=userId, symbol=symbol):
				user = User.get_user(userId=userId).first()
				for item in user.portfolios:
					if item.symbol == symbol:
						initial_price, company_name, prev_close = Portfolio.getPriceAndCompanyName(newSymbol)
						if type(initial_price) != float:
							return {"status": f"{newSymbol} not found"}
						item.symbol = newSymbol
						item.initial_price = initial_price
						item.company_name = company_name
						db.session.commit()
						return {"status": f"{symbol} was replaced with {newSymbol} successfully"}
			else:
				return {"status": f"{symbol} does not exist for {userId}"}
		else:
			return {"status": f"{userId} does not exist"}
			
				
	@staticmethod
	def delete_symbol(userId, symbol):
		user_exists = User.is_user(userId=userId)
		if user_exists:
			user = User.get_user(userId=userId).first()
			for portfolio in user.portfolios:
				if portfolio.symbol == symbol:
					db.session.delete(portfolio)
					db.session.commit()
					DeletedPortfolio.add_to_deletedportfolio(portfolio_item=portfolio, userId=user.id)
					return {"status": f"{symbol} removed successfully"}
			return {"status": f"{symbol} not found in portfolio"}
		return {"status": f"{userUd} does not exist"}
	
	@staticmethod
	def get_symbol_profit_or_loss(userId, symbol):
		current_price, company, prev_close = Portfolio.getPriceAndCompanyName(symbol)
		if type(current_price) != float:
			return {"status": "symbol not found in the api"}
		user = User.get_user(userId=userId).first()
		for item in user.portfolios:
			if item.symbol.lower()== symbol.lower():
				initial_price = item.initial_price
				if str(item.date_added.date()) != str(datetime.now().date()):
					profit_or_loss = float(current_price) - float(initial_price)
				else:
					profit_or_loss = float(current_price) - float(prev_close)
				return {"symbol": symbol, "profit_or_loss": profit_or_loss}
		return {"status": f"{symbol} not found"}
		
		
	@staticmethod
	def get_portfolio_performance_metric(userId):
		result = []
		symbols_arr = []
		init_price_arr = []
		date_added_arr = []
		
		user_exists = User.is_user(userId=userId)
		if user_exists == False:
			return {"status": f"{userId} does not exit"}
		user = User.get_user(userId=userId).first()
		portfolios = Portfolio.query.filter(Portfolio._user_id==user.id).all()
		
		if not portfolios:
			return {"status": "There is no symbol in portfolio"}
		for portfolio in portfolios:
			symbols_arr.append(portfolio.symbol)
			init_price_arr.append(portfolio.initial_price)
			date_added_arr.append(str(portfolio.date_added.date()))
			
		batch_request = Portfolio.doBatchRequest(symbols_arr, init_price_arr, date_added_arr)
		
		if type(batch_request) != list:
			return batch_request
		
		for item in batch_request:
			obj = {}	
			if item["date_added"] != str(datetime.now().date()):
				roi = float(item["current_price"]) - float(item["initial_price"])
			else:
				roi = float(item["current_price"]) - float(item["prev_close"])
			obj["name"] = item["company_name"]
			obj["symbol"] = item["symbol"]
			obj["roi"] = roi
			result.append(obj)
		
		return result
		
		
	@staticmethod
	def delete_user_portfolio(userId):
			if User.is_user == False:
				return {"status": f"{userId} does not exist"}
			try:
				user = User.get_user(userId=userId).first()
				Portfolio.query.filter_by(_user_id=user.id).delete()
				db.session.commit()
				return {"status": f"portfolio for user {userId} was deleted successfully"}
			except Exception as e:
				print(e)
				return {"status": f"there was a problem deleting portfolio for {userId}"}
				
	@staticmethod
	def clear_all_portfolios():
			try:
				Portfolio.query.delete()
				db.session.commit()
				return {"status": "All portfolios were successfully cleared :) "}
			except Exception as e:
				print(e)
				return {"status": "there was a problem clearing all portfolios"}
				
				
	@staticmethod
	def get_user_portfolio_ranking(userId,timeframe):
		'''
		gets portfolio ranking for a userId
		'''
		portfolio_array = []
		symbols_arr = []
		init_price_arr = []
		date_added_arr = []

		if User.is_user(userId=userId) == False:
				return {"status": f"{userId} does not exist"}
		
		if "week" in timeframe:
			timeframe = datetime.now() - timedelta(7)
		elif "month" in timeframe:
				timeframe = datetime.now() - timedelta(30)
		elif "to-date" in timeframe:
			timeframe = "all"
		else:
			return {"status": f"Invalid argument {timeframe}"}
		user = User.get_user(userId=userId).first()
		if timeframe=="all":
			portfolios = Portfolio.query.filter_by(_user_id=user.id).all()
		if timeframe != "all":
			portfolios = Portfolio.query.filter_by(_user_id=user.id).filter(Portfolio.date_added.between(timeframe.date(), datetime.now().date())).all()
			
		if portfolios:
			for portfolio in portfolios:
				symbols_arr.append(portfolio.symbol)
				init_price_arr.append(portfolio.initial_price)
				date_added_arr.append(str(portfolio.date_added.date()))
			
			batch_request = Portfolio.doBatchRequest(symbols_arr, init_price_arr, date_added_arr)
		
			if type(batch_request) != list:
				return batch_request
		
			for item in batch_request:
				obj = {}	
				if item["date_added"] != str(datetime.now().date()):
					profit_or_loss = float(item["current_price"]) - float(item["initial_price"])
				else:
					profit_or_loss = float(item["current_price"]) - float(item["prev_close"])
				
				obj["company_name"] = item["company_name"]
				obj["symbol"] = item["symbol"]
				obj["date_added"] = item["date_added"]
				obj["performance_metric"] = profit_or_loss
				portfolio_array.append(obj)
			portfolio_array = sorted(portfolio_array, key=lambda x: x["performance_metric"], reverse=True)
			return portfolio_array
		
	@staticmethod
	def get_global_portfolio_ranking(top_rank_x, timeframe):
		'''
		gets portfolio ranking for all users
		'''
		global_portfolio = []
		sorted_global_portfolio = []
		users = User.query.all()
		for user in users:
			user_obj = {}
			user_portfolio_ranking = Portfolio.get_user_portfolio_ranking(userId=user.user_id,timeframe=timeframe)
			if not user_portfolio_ranking:
				continue
			try:
				num_of_symbols = len(user_portfolio_ranking)
				user_rois = [float(item["performance_metric"]) for item in user_portfolio_ranking]
			except Exception as e:
				print(e)
				return user_portfolio_ranking
			try:
				avg_user_roi = sum(user_rois)/ len(user_rois)
			except ZeroDivisionError:
				avg_user_roi = 0
			user_obj["average_user_roi"] = avg_user_roi
			user_obj["userId"] = str(user.user_id)
			user_obj["number_of_symbols"] = num_of_symbols
			global_portfolio.append(user_obj)
		sorted_global_portfolio = sorted(global_portfolio, key=lambda x: x["average_user_roi"], reverse=True)
		
		if sorted_global_portfolio:
			for index,item in enumerate(sorted_global_portfolio):
				item["ranking"] = str(index+1)
			sorted_global_portfolio = [item for item in sorted_global_portfolio if float(item["average_user_roi"]) != 0 and float(item["number_of_symbols"]) != 0]
		
			#To make sure the ranking is correct
			for index, item in enumerate(sorted_global_portfolio):
				item["ranking"] = str(index+1)
			
			try:
				if len(sorted_global_portfolio) > 0: 	
					arr = sorted_global_portfolio[0:int(top_rank_x)]
					return arr 	
				else:
			 		return []
			except Exception as e:
				arr =  sorted_global_portfolio[0:top_rank_x]
				return arr
				
		else:
		 	return {"status": "No result found"}
		 	

				
	@staticmethod
	def get_user_global_portfolio_ranking(userId, timeframe):
		if User.is_user(userId=userId) == False:
			return {"status":f"{userId} does not exist"}
		top_rank_x = None
		sorted_global_portfolio = Portfolio.get_global_portfolio_ranking(top_rank_x=top_rank_x, timeframe=timeframe)							
		
		sorted_global_portfolio = [item for item in sorted_global_portfolio if float(item["average_user_roi"]) != 0 and float(item["number_of_symbols"]) != 0]
		
		for item in sorted_global_portfolio:
			if str(item["userId"]) == str(userId):
				
				user = {"userId":item["userId"], "ranking": item["ranking"], "number_of_symbols":item["number_of_symbols"], "average_user_roi" : item["average_user_roi"], "status": "target_user"}
				break	
		try:	
			sorted_global_portfolio.insert(0, user)
		except Exception as e:
			print(e)
		
		return sorted_global_portfolio[0] if len(sorted_global_portfolio) > 0 else []
		
		
	@staticmethod
	def get_trending_symbols(timeframe):
		portfolio_array = []
		if "week" in timeframe:
			timeframe = datetime.now() - timedelta(7)
		elif "month" in timeframe:
				timeframe = datetime.now() - timedelta(30)
		elif "to-date" in timeframe:
			timeframe = "all"
		else:
			return {"status": f"Invalid argument {timeframe}"}
		
		if timeframe !="all":
			users = User.query.join(Portfolio, User.id==Portfolio._user_id).filter(Portfolio.date_added.between(timeframe.date(), datetime.now().date())).all()
			
		if timeframe == "all":
			users = User.query.all()
		
		if users:	
			for user in users:
				for portfolio in user.portfolios:
					portfolio_array.append(portfolio.symbol)
			result = dict(Counter(portfolio_array))
			return {"result": result}
		return {"status": "No result for the given timeframe"}
		
		
			
			
				
			
			




























