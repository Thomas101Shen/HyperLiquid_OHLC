from hyperliquid.info import Info
from hyperliquid.utils import constants
import json

def coin_fetcher():
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    meta_data = info.meta()
    coins = []
    for coin in meta_data['universe']:
        if int(coin["maxLeverage"]) >= 5:
            coins.append(coin["name"])
    return coins

if __name__ == '__main__':
    print(coin_fetcher())