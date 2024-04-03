import socket
import time
import requests
import urllib3
import json
import websocket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = f"https://localhost:5000/v1/api"

conid_map = {}
conid_map["NYSE_BMO"] = 1

class conid_info:

    def __init__(self):
        self.exchange = ''
        self.product_code = ''
        self.conid = 0
        self.close_price = 0
        self.product_name = ''
        self.ccy = ''
        self.lot_size = 1

    def __str__(self) -> str:
        str = {'exchange': self.exchange,
               'product_code': self.product_code,
               'conid': self.conid,
               'close_price': self.close_price,
               'product_name': self.product_name,
               'ccy': self.ccy,
               'lot_size': self.lot_size}

        return json.dumps(str, indent=4, ensure_ascii=False)

def server_run():
    """
    iserver服务初始化
    """
    try:
        request_url = base_url + f"/iserver/auth/ssodh/init?publish=true&compete=true"
        json_content= {}
        response = requests.post(url=request_url, json=json_content,verify=False)
        if response.status_code == 200:
            request_url = base_url + f"/sso/validate"
            response = requests.get(url=request_url,verify=False)
            if response.status_code == 200:
                return True
            else:
                print(request_url + "[status_code=" + response.status_code + "]")
                return False
        else:
            print(request_url + "[status_code=" + response.status_code + "]")
            return False
    except Exception as e:
        print(e)
        return False
    return True
    
def server_reauthenticate():
    """
    iserver重新认证
    """
    try:
        request_url = base_url + f"/iserver/reauthenticate"
        response = requests.post(url=request_url,verify=False)
        if response.status_code == 200:
            return True
        else:
            print(request_url + "[status_code=" + response.status_code + "]")
            return False
    except Exception as e:
        print(e)
        return False
    return True
    
def load_conids(exchange):
    """
    获取产品代码
    """
    upd_conid_map = {}
    prod = conid_info()
    try:
        request_url = base_url + f"/trsrv/all-conids?exchange=" + exchange
        response = requests.get(url=request_url,verify=False)
        if response.status_code == 200:
            rsp = response.json()
            count = 0
            conids = ""
            for item in rsp:
                count = count + 1
                if count == 1:
                    conids = conids + str(item['conid'])
                else:
                    conids = conids + "," + str(item['conid'])
                if count == 200:
                    request_url = base_url + f"/trsrv/secdef?conids=" + conids
                    response = requests.get(url=request_url,verify=False)
                    if response.status_code == 200:
                        rsp_conids = response.json()
                        for item_conids in rsp_conids['secdef']:
                            if item_conids['listingExchange'] == exchange:
                                product_code = item_conids['ticker']
                                key = exchange + "_" + product_code
                                prod.exchange = exchange
                                prod.product_code = product_code
                                prod.conid = item_conids['conid']
                                upd_conid_map[key] = prod
                                print(upd_conid_map[key])
                    else:
                        print(request_url + "[status_code=" + str(response.status_code) + "]")
                    count = 0
                    conids = ""
                    time.sleep(1)
            if count > 0:
                request_url = base_url + f"/trsrv/secdef?conids=" + conids
                response = requests.get(url=request_url,verify=False)
                if response.status_code == 200:
                    rsp_conids = response.json()
                    for item_conids in rsp_conids['secdef']:
                        if item_conids['listingExchange'] == exchange:
                            product_code = item_conids['ticker']
                            key = exchange + "_" + product_code
                            prod.exchange = exchange
                            prod.product_code = product_code
                            prod.conid = item_conids['conid']
                            upd_conid_map[key] = prod
                else:
                    print(request_url + "[status_code=" + str(response.status_code) + "]")
            print(upd_conid_map['TSEJ_8595'])
            for item in upd_conid_map:
                print(upd_conid_map[item])
                request_url = base_url + f"/iserver/contract/" + str(upd_conid_map[item].conid) + f"/info-and-rules?isBuy=true"
                response = requests.get(url=request_url,verify=False)
                if response.status_code == 200:
                    rsp = response.json()
                    upd_conid_map[item].product_name = rsp['company_name']
                    upd_conid_map[item].ccy = rsp['currency']
                    upd_conid_map[item].lot_size = rsp['rules']['sizeIncrement']
                    print(upd_conid_map[item])
                else:
                    print(request_url + "[status_code=" + str(response.status_code) + "]")
                time.sleep(1)
            request_url = base_url + f"/iserver/accounts"
            response = requests.get(url=request_url,verify=False)
            if response.status_code == 200:
                count = 0
                conids = ""
                for item in upd_conid_map:
                    count = count + 1
                    if count == 1:
                        conids = conids + str(upd_conid_map[item].conid)
                    else:
                        conids =conids + "," + str(upd_conid_map[item].conid)
                    if count == 200:
                        request_url = base_url + f"/iserver/marketdata/snapshot?conids=" + conids + f"&fields=55,7741"
                        response = requests.get(url=request_url,verify=False)
                        time.sleep(1)
                        response = requests.get(url=request_url,verify=False)
                        if response.status_code == 200:
                            rsp_conids = response.json()
                            for item_conids in rsp_conids:
                                key = exchange + "_" + item_conids['55']
                                print("1-" + key)
                                if key in upd_conid_map:
                                    upd_conid_map[key].close_price = item_conids['7741']
                                    print(upd_conid_map[key])
                        else:
                            print(request_url + "[status_code=" + str(response.status_code) + "]")
                        count = 0
                        conids = ""
                if count > 0:
                    request_url = base_url + f"/iserver/marketdata/snapshot?conids=" + conids + f"&fields=55,7741"
                    response = requests.get(url=request_url,verify=False)
                    time.sleep(1)
                    response = requests.get(url=request_url,verify=False)
                    if response.status_code == 200:
                        rsp_conids = response.json()
                        for item_conids in rsp_conids:
                            key = exchange + "_" + item_conids["55"]
                            print("2-" + key)
                            if key in upd_conid_map:
                                upd_conid_map[key].close_price = item_conids['7741']
                                print(upd_conid_map[key])
                    else:
                        print(request_url + "[status_code=" + str(response.status_code) + "]")
            else:
                print(request_url + "[status_code=" + str(response.status_code) + "]")
        else:
            print(request_url + "[status_code=" + str(response.status_code) + "]")
            return False
    except Exception as e:
        print(e)
        return False
    return True

if __name__ == '__main__':
    server_run()
    load_conids("TSEJ")
    # request_url = f"https://localhost:5000/v1/api/trsrv/secdef?conids=265598"
    #request_url = f"https://172.18.180.42:5000/v1/api/iserver/marketdata/snapshot?conids=13906070,265598,8314&fields=31,84,86,7741,7296,88,55,85,73"
    #response = requests.get(url=request_url,verify=False)
    #print(response.content)
    while True:
        time.sleep(1)