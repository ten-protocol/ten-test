import random, string, os, json
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.emitter import TransparentEventEmitter


def rstr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        emitter = TransparentEventEmitter(self, web3)
        emitter.deploy(network, account)

        # transact and check event logs in the tx receipt
        self.log.info('Transact by calling emitArrayEvent')
        receipt = network.transact(self, web3,
                                   emitter.contract.functions.emitArrayEvent(int(1), [1,2], [rstr(), rstr()]),
                                   account, emitter.GAS_LIMIT)
        self.dump(network, web3, emitter, 'ArrayEvent(uint256,uint256[],string[])', receipt, 'array_event.log')

        self.log.info('Transact by calling emitStructEvent')
        receipt = network.transact(self, web3,
                                   emitter.contract.functions.emitStructEvent(int(2), rstr()),
                                   account, emitter.GAS_LIMIT)
        self.dump(network, web3, emitter, 'StructEvent(uint256,(uint256,string,address))', receipt, 'struct_event.log')

        self.log.info('Transact by calling emitMappingEvent')
        receipt = network.transact(self, web3,
                                   emitter.contract.functions.emitMappingEvent(int(3), [account.address], [random.randrange(100)]),
                                   account, emitter.GAS_LIMIT)
        self.dump(network, web3, emitter, 'MappingEvent(uint256,address[],uint256[])', receipt, 'map_event.log')

    def dump(self, network, web3, contract, signature, receipt, filename):
        response = self.get_debug_event_log_relevancy(url=network.connection_url(),
                                                      address=contract.address,
                                                      signature=web3.keccak(text=signature).hex(),
                                                      fromBlock=hex(receipt.blockNumber), toBlock='latest')

        self.assertTrue(response[0]['contractAddress'] == contract.address.lower())
        self.assertTrue(response[0]['eventSig'] == web3.keccak(text=signature).hex())
        self.assertTrue(response[0]['transactionHash'] == receipt.transactionHash.hex())
        self.assertTrue(response[0]['defaultContract'] == False)
        self.assertTrue(response[0]['transparentContract'] == True)
        self.assertTrue(response[0]['eventConfigPublic'] == True)
        self.assertTrue(response[0]['topic1Relevant'] == None)
        self.assertTrue(response[0]['topic2Relevant'] == None)
        self.assertTrue(response[0]['topic3Relevant'] == None)
        self.assertTrue(response[0]['senderRelevant'] == None)
        self.assertTrue(response[0]['eventAutoVisibility'] == False)
        self.assertTrue(response[0]['eventAutoPublic'] == None)
        self.assertTrue(response[0]['topic1AutoRelevant'] == False)
        self.assertTrue(response[0]['topic2AutoRelevant'] == False)
        self.assertTrue(response[0]['topic3AutoRelevant'] == False)

        with open(os.path.join(self.output, filename), 'w') as file:
            json.dump(response, file, indent=4)