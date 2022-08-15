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

# ~/.bash_profileなどに設定しておく
# export BINANCE_API_KEY='BINANCEのAPIキー'
# export BINANCE_API_SECRET='BINANCEのシークレットキー'
# export WEBHOOK_URL='discodeのAPIキー'
BINANCE_API_KEY = os.environ['BINANCE_API_KEY'] #BINANCEのAPIキーをセット
BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']  #BINANCEのシークレットキーをセット
WEBHOOK_URL  = os.environ['WEBHOOK_URL'] #botのwebhookURL

SPOT_URL = 'https://api.binance.com/api/v3/trades?symbol=ETHUSDT'
ETH_SYMBOL = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
#~/.bash_profileなどに設定しておく
#export MY_ENTER_PRICE_ETH = 2100
#export MY_PURCHASE_PRICE_ETH = 2000
#export ETH_PURCHASED_NUMBER = 0.7(=>0.7eth)
MY_ENTER_PRICE_ETH = float(os.environ['MY_ENTER_PRICE_ETH'])
MY_PURCHASE_PRICE_ETH = float(os.environ['MY_PURCHASE_PRICE_ETH'])
ETH_PURCHASED_NUMBER = float(os.environ['ETH_PURCHASED_NUMBER'])

# csvにデータを入れる際のカラム(1行目)
columns_list = list()
#columns= pd.Index(columns_list)
csv_values = list()

def send_to_discord(content):
    contents    = {
        'botname': '',      #表示されるbot名.空だとDiscodeの標準
        'avatar_url': '',    #アイコンURL.空だとDiscodeの標準
        'content': content   #投稿したい本文
    }
    headers = {'Content-Type': 'application/json'}

    try:
        res = requests.post(WEBHOOK_URL, json.dumps(contents), headers=headers)
    except Exception as e:
        print(e)
        return False

def get_spot_price():
    r = requests.get(SPOT_URL).json()
    cm_futures_client = CMFutures(key=BINANCE_API_KEY, secret=BINANCE_API_SECRET)
    asset = pd.DataFrame(cm_futures_client.account()['assets'])
    futures_profit = asset[asset['asset'].str.contains('ETH', regex=True)]['unrealizedProfit'].astype(float).values
    return futures_profit[0]*float(r[0]['price'])

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
        columns_list.append("TIME")
        csv_values.append(dt_now.strftime('%Y-%m-%d %H:%M:%S'))

        eth_enter_price_d = "ETH ENTER price: {}".format(MY_ENTER_PRICE_ETH)
        # print(eth_enter_price_d)
        printlist.append(eth_enter_price_d)
        columns_list.append("ETH ENTER price")
        csv_values.append(MY_ENTER_PRICE_ETH)

        current_eth_price = get_current_eth_price()
        eth_price_d = "ETH Current price: {}".format(current_eth_price)
        # print(eth_price_d)
        printlist.append(eth_price_d)
        columns_list.append("ETH Current price")
        csv_values.append(current_eth_price)

        jpyrate = get_usdjpy_rate()
        jpyrate_d = "USDJPY Rate: {}".format(jpyrate)
        # print(jpyrate_d)
        printlist.append(jpyrate_d)
        columns_list.append("USDJPY Rate")
        csv_values.append(jpyrate)

        spot_price = get_spot_price()
        unrealized_profit_usd = round(spot_price,1)
        unrealized_profit_usd_d = '先物 profit: {}USD'.format(unrealized_profit_usd)
        # print(unrealized_profit_usd_d)
        printlist.append(unrealized_profit_usd_d)
        columns_list.append("先物 profit")
        csv_values.append(spot_price)

        genbutu_profit = genbutu_profit()
        genbutu_profit_d = "現物 profit: {}USD".format(round(genbutu_profit,1))
        # print(genbutu_profit_d)
        printlist.append(genbutu_profit_d)
        columns_list.append("現物 profit")
        csv_values.append(genbutu_profit)

        my_profit = spot_price + genbutu_profit
        profit_d = "Current ETH_LS Profit: {} ☆ここが重要".format(round(my_profit,1))
        # print(profit_d)
        printlist.append(profit_d)
        columns_list.append("Current ETH_LS Profit")
        csv_values.append(my_profit)

        in_jpy= convert_usd_jpy(my_profit)
        in_jpy_d = "ETH_LS Profit JPY: {}".format(round(in_jpy,1))
        # print(in_jpy_d)
        printlist.append(in_jpy_d)
        columns_list.append("ETH_LS Profit JPY")
        csv_values.append(in_jpy)

        genbutu_truely_profit = genbutu_truely_profit()
        truely_profit_d = "Deposit Genbutu Profit: {} ※これが合っているのか不明".format(round(genbutu_truely_profit,1))
        # print(truely_profit_d)
        printlist.append(truely_profit_d)
        columns_list.append("Deposit Genbutu Profit")
        csv_values.append(genbutu_truely_profit)

        fin_in_jpy = convert_usd_jpy(genbutu_truely_profit)
        fin_in_jpy_d = "Deposit Genbutu JPY: {}".format(round(fin_in_jpy,1))
        # print(fin_in_jpy_d)
        printlist.append(fin_in_jpy_d)
        columns_list.append("Deposit Genbutu JPY")
        csv_values.append(fin_in_jpy)

        final_profit = genbutu_truely_profit + my_profit
        final_profit_d = "Final Profit: {} ※多分こっちは間違っている".format(round(final_profit,1))
        # print(truely_profit_d)
        printlist.append(final_profit_d)
        columns_list.append("Final Profit")
        csv_values.append(final_profit)

        final_profit_jpy = convert_usd_jpy(final_profit)
        final_profit_jpy_d = "Deposit Genbutu JPY: {}".format(round(final_profit_jpy,1))
        # print(fin_in_jpy_d)
        printlist.append(final_profit_jpy_d)
        columns_list.append("Deposit Genbutu JPY")
        csv_values.append(final_profit_jpy)

        printlist.append(slit)

        print(".........writting to csv...........")
        # Pandas組み立て
        # print(csv_values)
        # print(columns_list)
        df = pd.DataFrame([csv_values],columns=columns_list)
        # csv読み込み&追記
        # headerが何度も書き込まれないようにチェックする
        with open('./eth_recode.csv', mode = 'a') as f:
            df.to_csv(f, header=f.tell()==0,index = False)

        # 差額関連の文字列が入ったリストが返ってくる
        eth_diff_list = eth_diff.build_diff_content()
        printlist.extend(eth_diff_list)

        # 投稿用の内容組み立て
        content = '\n'.join(printlist)

        print(content)
        print(".......sending to Discode......")
        send_to_discord(content)
        #time.sleep(1*60*60)
    #except KeyboardInterrupt:
    #    pass
