from api.bsc_wallet_api import EVMWalletAPI
from config import config

evm_apis = {}
for _k, _v in config.chains.items():
    evm_apis[_k] = EVMWalletAPI()

evm_api = evm_apis['8453']
