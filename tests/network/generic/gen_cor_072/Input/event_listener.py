from web3 import Web3
import logging
import time
import argparse, json, sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Starting to run the event loop')
    event_filter = contract.events.Stored.createFilter(fromBlock='latest')
    logging.info('Starting the polling loop')
    while True:
        for event in event_filter.get_new_entries():
            logging.info('Stored value = %s', event['args']['value'])
        time.sleep(2)