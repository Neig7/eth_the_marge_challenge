# coding: UTF-8

# before run this, pip3 install requered
# pip3 install python-binance
# pip3 install binance-futures-connector

from binance.cm_futures import CMFutures
from binance.client import Client
import pandas as pd
import requests
import time
import datetime
import json

BINANCE_API_KEY = '' #BINANCEのAPIキーをセット
BINANCE_API_SECRET = '' #BINANCEのシークレットキーをセット
SPOT_URL = 'https://api.binance.com/api/v3/trades?symbol=ETHUSDT'
ETH_SYMBOL = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"


# Coin-M先物のシンボルリストは以下のAPIにアクセスするとわかる。ブラウザで良い
# Base URLとURIが異なる
# https://dapi.binance.com/dapi/v1/exchangeInfo
COIN_M_SPOT_URL = "https://dapi.binance.com/dapi/v1/ticker/price"
ETHUSD_SYMBOL = "https://dapi.binance.com/dapi/v1/ticker/price?symbol=ETHUSD_PERP"
ETH202209_SYMBOL = "https://dapi.binance.com/dapi/v1/ticker/price?symbol=ETHUSD_220930"
ETH202212_SYMBOL = "https://dapi.binance.com/dapi/v1/ticker/price?symbol=ETHUSD_221230"


MY_ENTER_PRICE_ETH = 1675
MY_PURCHASE_PRICE_ETH = 1620
WEBHOOK_URL  = 'https://discord.com/api/webhooks/1005350465464188940/f2DRBgdNUIj2iQpWLtWgNrZZKR9uPyiN8YFDOJoc7GmsawsdVi-9BBjOrH8D89hRdlgm'    #botのwebhookURL


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

# Coim_m 汎用
def get_coin_m_price(symbol):
    r_eth_price = requests.get(symbol)
    r_eth_price.raise_for_status()
    r_2json = r_eth_price.json()
    # Coin-Mはリストで帰ってくる(現物は素のjson)
    # [{"symbol":"ETHUSD_PERP","ps":"ETHUSD","price":"1686.33","time":1660094613388}]
    #print(type(r_2json))
    #print("json:{}",r_2json)
    price: float = r_2json[0]['price']
    #print("Current ETH price{}",current_eth)
    return float(price)


def get_current_eth_price():
    r_eth_price = requests.get(ETH_SYMBOL)
    r_eth_price.raise_for_status()
    r_2json = r_eth_price.json()
    #print("ETH json:{}",r_2json)
    current_eth = r_2json['price']
    #print("Current ETH price{}",current_eth)
    return float(current_eth)

def genbutu_profit():
    current_eth_price = get_current_eth_price()
    genbutu_profit = current_eth_price - MY_ENTER_PRICE_ETH
    #print("Genbutu Profit:{}".format(genbutu_profit))
    return genbutu_profit

def calc_my_profit():
    final_profit = get_spot_price() + genbutu_profit()
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



# 別ファイルから実行用
# リストを返すs
def build_diff_content():
    printlist = list()
    
    slit = "---------"
    printlist.append(slit)

    dt_now = datetime.datetime.now()
    dt_now_d = "TIME: {}".format(dt_now.strftime('%Y-%m-%d %H:%M:%S'))
    printlist.append(dt_now_d)

    eth_enter_price_d = "ETH MY ENTER price: {}".format(MY_ENTER_PRICE_ETH)
    printlist.append(eth_enter_price_d)

    printlist.append(slit)

    eth_price = get_coin_m_price(ETHUSD_SYMBOL)
    eth_price_d = "ETHUSD(永久) price: {}".format(eth_price)
    printlist.append(eth_price_d)

    eth_price09 = get_coin_m_price(ETH202209_SYMBOL)
    eth_price09_d = "ETHU2022(0930) price: {}".format(eth_price09)
    printlist.append(eth_price09_d)

    eth_price12 = get_coin_m_price(ETH202212_SYMBOL)
    eth_price12_d = "ETHUSD(1230) price: {}".format(eth_price12)
    printlist.append(eth_price12_d)

    printlist.append(slit)

    eth_diff09 = round(eth_price - eth_price09, 1)
    eth_diff09_d = "ETHUSD(0930) Diff: {}".format(eth_diff09)
    printlist.append(eth_diff09_d)

    eth_diff12 = round(eth_price - eth_price12,1)
    eth_diff12_d = "ETHUSD(1230) Diff: {}".format(eth_diff12)
    printlist.append(eth_diff12_d)

    printlist.append(slit)

    return printlist


if __name__ == '__main__':
        printlist = list()
        
        slit = "---------"
        printlist.append(slit)

        dt_now = datetime.datetime.now()
        dt_now_d = "TIME: {}".format(dt_now.strftime('%Y-%m-%d %H:%M:%S'))
        # print(dt_now_d)
        printlist.append(dt_now_d)

        # 先物のリストを取得
        #cm_futures_client = CMFutures(key=BINANCE_API_KEY, secret=BINANCE_API_SECRET)
        #client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        #futures_exchange_info = client.futures_exchange_info()  # request info on all futures symbols
        #trading_pairs = [info['symbol'] for info in futures_exchange_info['symbols']]
        #print(trading_pairs)

        eth_enter_price_d = "ETH MY ENTER price: {}".format(MY_ENTER_PRICE_ETH)
        # print(eth_enter_price_d)
        printlist.append(eth_enter_price_d)

        printlist.append(slit)

        eth_price = get_coin_m_price(ETHUSD_SYMBOL)
        eth_price_d = "ETHUSD(永久) price: {}".format(eth_price)
        # print(eth_price_d)
        printlist.append(eth_price_d)

        eth_price09 = get_coin_m_price(ETH202209_SYMBOL)
        eth_price09_d = "ETHU2022(0930) price: {}".format(eth_price09)
        # print(eth_price09_d)
        printlist.append(eth_price09_d)

        eth_price12 = get_coin_m_price(ETH202212_SYMBOL)
        eth_price12_d = "ETHUSD(1230) price: {}".format(eth_price12)
        # print(eth_price12_d)
        printlist.append(eth_price12_d)

        printlist.append(slit)


        eth_diff09 = round(eth_price - eth_price09, 1)
        eth_diff09_d = "ETHUSD(0930) Diff: {}".format(eth_diff09)
        printlist.append(eth_diff09_d)

        eth_diff12 = round(eth_price - eth_price12,1)
        eth_diff12_d = "ETHUSD(1230) Diff: {}".format(eth_diff12)
        printlist.append(eth_diff12_d)

        printlist.append(slit)

        content = '\n'.join(printlist)
        print(content)
        print(".......sending to Discode......")
        send_discord(content)


    #except KeyboardInterrupt:
    #    pass
