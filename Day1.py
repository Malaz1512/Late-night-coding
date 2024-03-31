import time
import requests
import urllib.parse
import hashlib
import hmac
import base64

with open("secret_api_keys", "r") as f:
    lines = f.read().splitlines()
    api_key = lines[0].split(" = ")[1]
    sec_key = lines[1].split(" = ")[1]

api_url = "https://api.kraken.com"

def get_kraken_sig(url_path, data, secret_key):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode() # ====REVISION==== I made an error here! it is supposed to be postdata and not [postdata] as the second one is a list, not a string :(
    message = url_path.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret_key), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def kraken_request(url_path, data):
    headers = {"API-Key": api_key, "API-Sign": get_kraken_sig(url_path, data, sec_key)}
    response = requests.post(api_url + url_path, headers=headers, data=data)
    response.raise_for_status()
    return response.json()

def place_order(order_type, volume):
    data = {
        "nonce": str(int(1000 * time.time())),
        "order_type": "market",
        "type": order_type,
        "volume": volume,
        "pair": "XBTCAD" # I'm using cad as i am going to be using this for canadian currency, but if you are in the us, you can use "XBTUSD".
    }
    return kraken_request("/0/private/AddOrder", data)

def get_current_price():
    response = requests.get(f"{api_url}/0/public/Ticker?pair=XBTCAD") # Again, this is set to read the CAD value, but you can certainly use XBTUSD here for the american version
    response.raise_for_status()
    return float(response.json()['result']['XXBTZCAD']['c'][0]) # Over here, for the american version you can use "XXBTZUSD" ==== REVISION ==== I forgot to add the second "X" lol ;)

def main():
    last_price = get_current_price()
    volume_to_trade = 0.0001 #Set to approx. $10 CAD in bitcoin
    while True:
        try:
            current_price = get_current_price()
            print(f"Current price of BTC CAD is {current_price} dollars")
            
            if current_price > last_price:
                print("price is rising, BUYING")
                place_order("buy", volume_to_trade)
            elif current_price < last_price:
                print("price is decreasing, SELLING")
                place_order("sell", volume_to_trade)
            else:
                print("price is stable, NOT DOING ANYTHING CURRENTLY")
        except Exception as e:
            print(f"Oops! An error occured. Here are the details: \n{e}")
        time.sleep(5) # We are going to pause for 30 seconds between every iteration, as we don't want to get banned from the kraken api since when you give requests too frequently, it is suspected as a DDoS attack :((((

if __name__ == "__main__":
    main() #Let's run the program!

#lets speed it up a bit. Change the "time.sleep(30) line to your preferred delay, i'll set it to 5 seconds for fun
#seems like bitcoin is at a stable price right now, lets wait for it to change from $95127.9
#This finally should work guys! lets hope...
#IT WORKSSSS!!!! please don't take this a financial advice guys, this is just a fun program, and I only put in 10 CAD, don't put in a stupid amount of money as it might get cleared out!
#Cya tmrw.
