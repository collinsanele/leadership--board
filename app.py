from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Portfolio, DeletedPortfolio
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__)
db.init_app(app)
db_url = "your_db_url"
app.config['SQLALCHEMY_DATABASE_URI'] = db_url 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


   
    
@app.route('/get_all_users')
def get_all_users():
	all_users = User.get_all_users()
	return jsonify({"message": all_users})

@app.route('/create_user/<userId>')
def create_user(userId):
	result = User.add_user(userId=userId)
	return jsonify(result)
	
@app.route('/delete_user/<userId>')
def remove_user(userId):
	result = User.delete_user(userId=userId)
	return jsonify(result)
	
@app.route('/edit_user/<userId>/<newUserId>')
def edit_user(userId, newUserId):
	result = User.edit_user(userId=userId, newUserId=newUserId)
	return jsonify(result)
	
	
@app.route('/get_user_portfolio/<userId>')
def get_user_portfolio(userId):
	result = User.get_user_portfolios(userId=userId)
	return jsonify(result)
	
@app.route('/add_to_portfolio/<userId>/<symbol>')
def add_to_portfolio(userId, symbol):
	result = Portfolio.add_to_portfolio(userId=userId, symbol=symbol)
	return jsonify(result)


@app.route('/edit_portfolio/<userId>/<symbol>/<newSymbol>')
def edit_portfolio(userId, symbol, newSymbol):
	result = Portfolio.edit_portfolio(userId=userId, symbol=symbol, newSymbol=newSymbol)
	return jsonify(result)


@app.route('/delete_symbol/<userId>/<symbol>')
def delete_symbol_from_portfolio(userId, symbol):
	result = Portfolio.delete_symbol(userId=userId, symbol=symbol)
	return jsonify(result)	


@app.route('/delete_user_portfolio/<userId>')
def delete_user_portfolio(userId):
	result = Portfolio.delete_user_portfolio(userId=userId)
	return jsonify(result)
	
@app.route('/clear_all_portfolios')
def clear_all_portfolios():
	result = Portfolio.clear_all_portfolios()
	return jsonify(result)


@app.route('/get_symbol_pnl/<userId>/<symbol>')
def get_symbol_pnl(userId, symbol):
	result = Portfolio.get_symbol_profit_or_loss(userId=userId, symbol=symbol)
	return jsonify(result)


@app.route('/get_portfolio_performance/<userId>')
def get_portfolio_performance(userId):
	result = Portfolio.get_portfolio_performance_metric(userId=userId)
	return jsonify(result)

	
@app.route('/get_global_portfolio_ranking/<top_rank_x>/<timeframe>')
def get_global_portfolio_ranking(top_rank_x, timeframe):
	result = Portfolio.get_global_portfolio_ranking(top_rank_x, timeframe)
	return jsonify(result)
	
@app.route('/get_user_global_portfolio_ranking/<userId>/<timeframe>')
def get_user_global_portfolio_ranking(userId, timeframe):
	result = Portfolio.get_user_global_portfolio_ranking(userId, timeframe)
	return jsonify(result)
	
@app.route('/get_trending_symbols/<timeframe>')
def get_trending_symbols(timeframe):
	result = Portfolio.get_trending_symbols(timeframe)
	return jsonify(result)

def main():
	with app.app_context():
		db.create_all()
		app.run(debug=False)
		

if __name__ == "__main__":
	main()
	
	
		











