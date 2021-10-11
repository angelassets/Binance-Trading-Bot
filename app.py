import os
from flask import Flask,render_template
import json
from bot.grab import get_price
from bot.report import report_update
from bot.session import session
from bot.settings import coins_bought_file_path
from bot.trade import  sell_coin,  update_sold_coin
from decimal import *
from binance.enums import *
from flask import request
import simplejson

app = Flask(__name__,
            static_url_path='', 
            static_folder='frontend/static',
            template_folder='frontend/templates')

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/coins/bought")
def coins_bought():
	try:
		with open(coins_bought_file_path, 'r') as jsonFile:
			data = jsonFile.read()
	except Exception: 
		return  {"error":-1, "message":"coins.json file not found"}
	if len(data)>0:
		data = json.loads(data)
		for item in data:
			if not data[item]['sold']:
				data[item]['c_profit'] = get_coin_profit(item, data[item]['bought_at'])
		return data
	else:
		data = {"error":-1, "message": "No record"}
		return data

def get_coin_profit(coin , bought_at):
		last_price = get_price(False) # don't populate rolling window
		profit = 0
		try:
			lastPrice = last_price[coin]['price']
			profit    = float(lastPrice)
		except Exception:
			profit = 'N/A'
		return profit
		

@app.route("/coins/sell", methods=["POST"])
def sell():
	if request.method == "POST":
		coin = json.loads(request.data)["symbol"]
		coins_sold,status = sell_coin(coin)
		last_price = get_price(False) # don't populate rolling window
		update_sold_coin(coins_sold,last_price)
		report_update()
		#session calculations like unrealised potential etc
		session('calc')
		#save session data to session_info file
		session('save')
	
		if status:
			return json.dumps({"status":1, "message":"success", "data":"coin sold"})
		else:
			return json.dumps({"status":1, "message":"something went wrong", "data":"coin sold"})



@app.route("/coins/purge", methods=["POST"])
def purge():
	if request.method == "POST":
		coin = json.loads(request.data)["symbol"]
		if os.path.isfile(coins_bought_file_path) and os.stat(coins_bought_file_path).st_size!= 0:
			with open(coins_bought_file_path) as file:
				coins_bought = simplejson.load(file, use_decimal=True)
		if(coins_bought[coin]):
			del coins_bought[coin]
			with open(coins_bought_file_path, 'w') as file:
				simplejson.dump(coins_bought, file, indent=4, use_decimal=True)
				return json.dumps({"status":1, "message":"purged: "+ coin})
		else:
			return json.dumps({"status":-1, "message": "Coin not in the list"})





if __name__ == "__main__":
	app.run(host="0.0.0.0")
