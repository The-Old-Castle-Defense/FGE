import traceback
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from eth_account import Account

Account.enable_unaudited_hdwallet_features()

class EVMWalletAPI:

    def __init__(self):
        self.w3 = None
        self.explorer_link = None
        self.rpc = None
        self.chain = None
        self.chain_id = None

    def init(self, chain_id, chains):
        _chain_id_str = str(chain_id)
        self.chain_id = chain_id
        self.chain = chains[_chain_id_str]['name']
        self.rpc = chains[_chain_id_str]['rpc']
        self.explorer_link = chains[_chain_id_str]['explorer_link']
        self.w3 = Web3(HTTPProvider(self.rpc))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)


        print("%s is ready to use: %s " % (self.chain, self.w3.is_connected()))
        if not self.w3.is_connected():
            print("Web3 Is not connected")

        return self.w3

    def get_contract(self, address, abi):
        contract = self.w3.eth.contract(
            abi=abi,
            address=self.w3.to_checksum_address(address)
        )
        return contract

    """
        Validate address
    """
    def validate_address(self, address):
        try:
            return self.w3.isAddress(address)
        except Exception as exc:
            print(exc)
            return False

    def get_tx_status(self, tx_hash):
        """
            Get tx status
        """
        try:
            result = self.w3.eth.get_transaction_receipt(tx_hash)
            return result
        except Exception as exc:
            print(exc)
            traceback.print_exc()
            return None

    def get_block_number(self):
        return self.w3.eth.block_number

    def current_height(self):
        return int(self.w3.eth.block_number)

    def get_nonce(self, address):
        return self.w3.eth.get_transaction_count(self.w3.to_checksum_address(address))


