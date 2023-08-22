from web3 import Web3
import logging, random
import argparse, json, sys, time

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='error_client')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Client running')
    while True:
        value = random.randint(0, 3)
        try:
            if value == 0:
                contract.functions.force_require().call()
            elif value == 1:
                contract.functions.force_revert().call()
            else:
                contract.functions.force_assert().call()
        except Exception as e:
            logging.info('Exception type: %s', type(e).__name__)
            logging.info('Exception args: %s', e.args[0])

        time.sleep(0.1)
