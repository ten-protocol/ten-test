from web3 import Web3
import secrets, time, os, json
import logging, random, argparse, sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout, level=logging.INFO)


def create_signed_withdrawal(contract, account, nonce, address, value, chain_id, fees):
    target = contract.functions.sendNative(address)
    params = {
        'nonce': nonce,
        'value': value+fees,
        'gasPrice': web3.eth.gas_price,
        'chainId': chain_id
    }
    params['gas'] = target.estimate_gas(params)
    build_tx = target.build_transaction(params)
    return account.sign_transaction(build_tx)


def run(chain_id, web3, account, contract, amount, fees):
    signed_tx = create_signed_withdrawal(contract, account, 0, account.address, amount, chain_id, fees)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    try:
        web3.eth.wait_for_transaction_receipt(tx_hash, timeout=900)
    except Exception as e:
        logging.error('Timed out waiting for %d' % tx_hash[1])
        logging.error(e)
    logging.info('Client completed')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('--network_http', help='Connection URL')
    parser.add_argument('--chainId', help='The network chain Id')
    parser.add_argument('--bridge_address', help='Address of the contract')
    parser.add_argument('--bridge_abi', help='Abi of the contract')
    parser.add_argument('--bridge_fees', help='Bridge fees')
    parser.add_argument('--pk', help='The accounts private key')
    parser.add_argument('--amount', help='The amount to send in wei')
    args = parser.parse_args()

    web3: Web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.bridge_abi) as f:
        contract = web3.eth.contract(address=args.bridge_address, abi=json.load(f))
    account = web3.eth.account.from_key(args.pk)

    logging.info('Starting client')
    run(int(args.chainId), web3, account, contract, int(args.amount), int(args.bridge_fees))
