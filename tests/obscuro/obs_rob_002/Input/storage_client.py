from web3 import Web3
import logging, random
import argparse, json, sys, time

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def store_value(value, web3, account, contract):
    build_tx = contract.functions.store(value).buildTransaction(
        {
            'nonce': web3.eth.get_transaction_count(account.address),
            'gasPrice': web3.eth.gas_price,
            'gas': 720000,
            'chainId': web3.eth.chain_id
        }
    )
    signed_tx = account.sign_transaction(build_tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
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
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Client running')
    account = web3.eth.account.privateKeyToAccount(args.pk_to_register)

    while True:
        store_value(random.randint(0,100), web3, account, contract)
        time.sleep(0.1)



