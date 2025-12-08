from web3 import Web3
import logging, random
import argparse, json, sys, time

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def store_value(value, web3, address, contract):
    gas_price = web3.eth.gas_price
    params = {
        'from': address,
        'nonce': web3.eth.get_transaction_count(address),
        'chainId': web3.eth.chain_id,
        'gasPrice': gas_price
    }
    gas_estimate = contract.functions.store(value).estimate_gas(params)
    params['gas'] = gas_estimate

    logging.info('Account Balance: %d', web3.eth.get_balance(address))
    logging.info('Cost Estimate:   %d', gas_estimate*gas_price)
    logging.info('Gas Estimate:    %d', gas_estimate)
    logging.info('Gas Price:       %d', gas_price)

    build_tx = contract.functions.store(value).build_transaction(params)
    tx_hash = web3.eth.send_transaction(build_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt.status != 1:
        logging.error('Error performing transaction\n')
    else:
        logging.info('Transaction complete - stored value %d', value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='storage_client')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    parser.add_argument('-p', '--session_key', help='Session key to use')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Client running')
    while True:
        store_value(random.randint(0,100), web3, args.session_key, contract)
        time.sleep(0.1)



