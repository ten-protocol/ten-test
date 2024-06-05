from web3 import Web3
from pysys.constants import BLOCKED
from ten.test.basetest import TenNetworkTest



class PySysTest(TenNetworkTest):
    GNOSIS_ADDRESS = None
    DEPLOYER_PK = None

    def execute(self):
        if self.GNOSIS_ADDRESS is None or self.DEPLOYER_PK is None:
            self.addOutcome(BLOCKED, abortOnError=True,
                            outcomeReason='Gnosis address and deployer pk must be specified to run')
        network = self.get_l1_network_connection(self.env)
        url = network.connection_url()
        web3 = Web3(Web3.HTTPProvider(url))

        deployer_account = web3.eth.account.from_key(self.DEPLOYER_PK)
        deployer_balance = web3.from_wei(web3.eth.get_balance(deployer_account.address), 'ether')
        self.log.info('Deployer account balance %.6f ETH', deployer_balance)

