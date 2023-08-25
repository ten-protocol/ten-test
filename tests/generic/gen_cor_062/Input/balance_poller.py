from web3 import Web3
import logging, time
import argparse, json, sys

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='balance_poller')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    parser.add_argument('-p', '--polling_address', help='Address of account to poll')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Account balance is %d', web3.eth.get_balance(args.polling_address))
    logging.info('Starting to run the polling loop')
    last_balance = 0
    while True:
        balance = contract.functions.balanceOf(args.polling_address).call({"gas":1000000})
        if balance > last_balance:
            last_balance = balance
            logging.info('New balance = %s', balance)
        time.sleep(2)


