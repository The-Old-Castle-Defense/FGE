import json
import logging


class Config:
    config: dict = {}
    connectionString: str = None
    GRAPH_QL_EVENTS: dict

    def init_config(self):
        logging.info("Loading config file...")
        with open('services.json') as conf_file:
            conf = json.load(conf_file)
            self.config = conf
        self.GRAPH_QL_EVENTS = {
            "buyAttacks": ["transactionHash","player","teamId","siegeId","battleId","attackValue","investedAmount","fee","referrer","blockNumber","blockTimestamp"],
            #"investments": ["transactionHash","player","teamId","metadata","investedAmount","fee","referrer","battleId","siegeId","blockNumber","blockTimestamp"],
            #"boosts": ["transactionHash","player","teamId","tokenId","investedAmount","fee","referrer","battleId","siegeId","blockNumber","blockTimestamp"],
            #"resurrects": ["transactionHash","player","teamId","tokenId","investedAmount","fee","referrer","battleId","siegeId","blockNumber","blockTimestamp"],
            #"dealers": ["transactionHash","player","teamId","sphAmount","investedAmount","fee","referrer","battleId","siegeId","blockNumber","blockTimestamp"],
            #"heals": ["transactionHash","player","teamId","tokenId","battleId","siegeId","blockNumber","blockTimestamp"],
            #"earnAndBurnSPHToNFTs": ["transactionHash","player","teamId","tokenId","amount","battleId","siegeId","blockNumber","blockTimestamp"],
            #"upgrades": ["transactionHash","player","teamId","tokenId","upgradeBlock","addAttack","battleId","siegeId","blockNumber","blockTimestamp"],
            #"gameStarteds": ["transactionHash","siegeId","startBlock","pFee","blocksPerBattle","blocksPerLvl","pricePerAttack","boostPrice","upgradePrice","pricePerSPH","sphPerBattle","totalBattles","sphPrice","blockNumber","blockTimestamp"],
            #"battleStarteds": ["transactionHash","siegeId","blockNumber","blockTimestamp"],
            #"battleEndeds": ["transactionHash","siegeId","battleId","t0AttackValue","t1AttackValue","t0SPHReward","t1SPHReward","winningTeamId","blockNumber","blockTimestamp"],
            #"siegeCompleteds": ["transactionHash","siegeId","battleId","t0AttackValue","t1AttackValue","t0BoughtAttack","t1BoughtAttack","winnerTeamId","blockNumber","blockTimestamp"],
            "siegeRewards": ["transactionHash","player","siegeId","rewardAmount","teamId","rewartType","blockNumber","blockTimestamp"],
            #"battleRewards": ["transactionHash","player","siegeId","battleId","tokenId","rewardAmount","teamId","blockNumber","blockTimestamp"],
            #"stakeNFTs": ["transactionHash","player","tokenId","defaultAttack","siegeId","isStake","blockNumber","blockTimestamp"]
        }
        logging.info("Vars loaded")

    def get_config(self):
        return self.config

    def formatDecStr(self, value, to_decimals=False, to_string=True):
        if to_decimals and isinstance(value, str) and value.replace('.', '', 1).isdigit():
            if "." in str(value):
                return float(value)
            return int(value) 
        elif to_string:
            if isinstance(value, int) or isinstance(value, float):
                if value > 18_446 or value < -189_551:
                    return str(value)
                else:
                    return value
            return value
        return value
    
    def formatNestedDict(self, d, to_decimals=False, to_string=True):
        if isinstance(d, dict):
            for key, value in d.items():
                if isinstance(value, (dict, list)):
                    d[key] = self.formatNestedDict(value, to_decimals, to_string)
                else:
                    d[key] = self.formatDecStr(value, to_decimals, to_string)
        elif isinstance(d, list):
            d = [self.formatNestedDict(item, to_decimals, to_string) if isinstance(item, (dict, list)) else self.formatDecStr(item, to_decimals, to_string) for item in d]
        else:
            d = self.formatDecStr(d, to_decimals, to_string)

        return d
