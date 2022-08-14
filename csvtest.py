# coding: UTF-8

# before run this, pip3 install requered
# pip3 install python-binance
# pip3 install binance-futures-connector

from binance.cm_futures import CMFutures
import pandas as pd
import requests
import time
import datetime
import json
import eth_diff
import os

# csv file name
CSV_FILE = "./eth_log.csv"

df = pd.read_csv('data/src/sample_pandas_normal.csv', index_col=0)
csv_columns = list()


# ~/.bash_profileなどに設定しておく
# export BINANCE_API_KEY='BINANCEのAPIキー'
# export BINANCE_API_SECRET='BINANCEのシークレットキー'
# export WEBHOOK_URL='discodeのAPIキー'
BINANCE_API_KEY = os.environ['BINANCE_API_KEY'] #BINANCEのAPIキーをセット
BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']  #BINANCEのシークレットキーをセット
WEBHOOK_URL  = os.environ['WEBHOOK_URL'] #botのwebhookURL

SPOT_URL = 'https://api.binance.com/api/v3/trades?symbol=ETHUSDT'
ETH_SYMBOL = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"

MY_ENTER_PRICE_ETH = 1675
MY_PURCHASE_PRICE_ETH = 1620


def send_discord(content):
    main_content    = {
        'username': '',      #表示されるbot名
        'avatar_url': '',    #表示するアイコンのURL
        'content': content   #discordに表示される内容
    }
    headers = {'Content-Type': 'application/json'}

    try:
        res = requests.post(WEBHOOK_URL, json.dumps(main_content), headers=headers)
    except Exception as e:
        print(e)
        return False

def get_spot_price():
    r = requests.get(SPOT_URL).json()
    cm_futures_client = CMFutures(key=BINANCE_API_KEY, secret=BINANCE_API_SECRET)
    asset = pd.DataFrame(cm_futures_client.account()['assets'])
    unrealized_profit = asset[asset['asset'].str.contains('ETH', regex=True)]['unrealizedProfit'].astype(float).values

    return unrealized_profit[0]*float(r[0]['price'])


def get_current_eth_price():
    r_eth_price = requests.get(ETH_SYMBOL)
    r_eth_price.raise_for_status()
    r_2json = r_eth_price.json()
    #print("ETH json:{}",r_2json)
    current_eth = r_2json['price']
    #print("Current ETH price{}",current_eth)
    return float(current_eth)

# LとSを買った時を基準とした価格差
def genbutu_profit():
    current_eth_price = get_current_eth_price()
    genbutu_profit = current_eth_price - MY_ENTER_PRICE_ETH
    #print("Genbutu Profit:{}".format(genbutu_profit))
    return genbutu_profit

# そもそも現物のETHを買った時の価格と現在の価格差
def  genbutu_truely_profit():
    current_eth_price = get_current_eth_price()
    genbutu_profit = current_eth_price - MY_PURCHASE_PRICE_ETH
    return genbutu_profit

# API呼び出しをもう一度行うことになるので遅い。普通にmain内で計算する
# def calc_my_profit():
#     final_profit = get_spot_price() + genbutu_profit()
#     return final_profit

def calc_truely_profit():
    final_profit = get_spot_price() + genbutu_truely_profit()
    return final_profit


CURRENCY_RATES_API = "https://dotnsf-fx.herokuapp.com"
def get_usdjpy_rate():
    r_currency_rates = requests.get(CURRENCY_RATES_API)
    r_c_r_json = r_currency_rates.json()
    if r_c_r_json["status"] == True:
        usdjpy_rate = r_c_r_json["rate"]["USDJPY"]
        #print("USDJPY:{}".format(usdjpy_rate))
        return usdjpy_rate

def convert_usd_jpy(usd: float):
    return usd * get_usdjpy_rate()

if __name__ == '__main__':
    #while True:
        print("Executing...Calling APIs...")
        printlist = list()
        slit = "---------"
        printlist.append(slit)
    
        dt_now = datetime.datetime.now()
        dt_now_d = "TIME: {}".format(dt_now.strftime('%Y-%m-%d %H:%M:%S'))
        # print(dt_now_d)
        printlist.append(dt_now_d)
        csv_columns.append("TIM")


        eth_enter_price_d = "ETH ENTER price: {}".format(MY_ENTER_PRICE_ETH)
        # print(eth_enter_price_d)
        printlist.append(eth_enter_price_d)
        csv_columns.append("ETH ENTER price")

        current_eth_price = get_current_eth_price()
        eth_price_d = "ETH Current price: {}".format(current_eth_price)
        # print(eth_price_d)
        printlist.append(eth_price_d)
        csv_columns.append("ETH Current price")

        jpyrate = get_usdjpy_rate()
        jpyrate_d = "USDJPY Rate: {}".format(jpyrate)
        # print(jpyrate_d)
        printlist.append(jpyrate_d)
        csv_columns.append("USDJPY Rate")

        spot_price = get_spot_price()
        unrealized_profit_usd = round(spot_price,1)
        unrealized_profit_usd_d = '先物 profit: {}USD'.format(unrealized_profit_usd)
        # print(unrealized_profit_usd_d)
        printlist.append(unrealized_profit_usd_d)
        csv_columns.append("先物 profit")

        genbutu_profit = genbutu_profit()
        genbutu_profit_d = "現物 profit: {}USD".format(round(genbutu_profit,1))
        # print(genbutu_profit_d)
        printlist.append(genbutu_profit_d)
        csv_columns.append("現物 profit")

        my_profit = spot_price + genbutu_profit
        profit_d = "Current ETH_LS Profit: {} ☆ここが重要".format(round(my_profit,1))
        # print(profit_d)
        printlist.append(profit_d)
        csv_columns.append("Current ETH_LS Profit")

        in_jpy= convert_usd_jpy(my_profit)
        in_jpy_d = "ETH_LS Profit JPY: {}".format(round(in_jpy,1))
        # print(in_jpy_d)
        printlist.append(in_jpy_d)
        csv_columns.append("ETH_LS Profit JPY")
        
        genbutu_truely_profit = genbutu_truely_profit()
        truely_profit_d = "Deposit Genbutu Profit: {} ※これが合っているのか不明".format(round(genbutu_truely_profit,1))
        # print(truely_profit_d)
        printlist.append(truely_profit_d)
        csv_columns.append("Deposit Genbutu Profit")

        fin_in_jpy = convert_usd_jpy(genbutu_truely_profit)
        fin_in_jpy_d = "Deposit Genbutu JPY: {}".format(round(fin_in_jpy,1))
        # print(fin_in_jpy_d)
        printlist.append(fin_in_jpy_d)
        csv_columns.append("Deposit Genbutu JPY")

        final_profit = genbutu_truely_profit + my_profit
        final_profit_d = "Final Profit: {} ※多分こっちは間違っている".format(round(genbutu_truely_profit,1))
        # print(truely_profit_d)
        printlist.append(final_profit_d)
        final_profit_jpy = convert_usd_jpy(final_profit)
        final_profit_jpy_d = "Deposit Genbutu JPY: {}".format(round(final_profit_jpy,1))
        # print(fin_in_jpy_d)
        printlist.append(final_profit_jpy_d)
        csv_columns.append("Final Profit")

        printlist.append(slit)

        # Discode投稿用の文字列を組み立て
        #content = dt_now_d +"\n"+ eth_price_d +"\n"+ jpyrate_d +"\n"+ str(unrealized_profit_usd_d) +"\n"+ str(genbutu_profit_d) +"\n"+ profit_d +"\n"+ str(in_jpy_d)

        # 差額関連の文字列が入ったリストが返ってくる
        eth_diff_list = eth_diff.build_diff_content()
        printlist.extend(eth_diff_list)

        content = '\n'.join(printlist)

        print(content)
        print(".......sending to Discode......")
        send_discord(content)
        #time.sleep(1*60*60)
    #except KeyboardInterrupt:
    #    pass
