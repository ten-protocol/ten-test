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


def create_signed_tx(web3, account, nonce, receiver, amount, chain_id):
    tx = {'nonce': nonce,
          'to': receiver,
          'value': amount,
          'gasPrice': web3.eth.gas_price,
          'chainId': chain_id
          }
    tx['gas'] = web3.eth.estimate_gas(tx)
    return account.sign_transaction(tx)


def run(web3, account, receiver, contract, amount, fees, chain_id):
    logging.info('Creating the signed transactions')
    nonce = 0
    signed_txs = []
    for i in range(0, 32):
        nonce = i
        signed_tx = create_signed_tx(web3, account, nonce, receiver, amount, chain_id)
        signed_txs.append((signed_tx, nonce))

    signed_tx = create_signed_withdrawal(contract, account, nonce+1, account.address, amount, chain_id, fees)
    signed_txs.append((signed_tx, nonce+1))

    logging.info('Sending the raw transactions')
    tx_hashes = []
    for signed_tx in signed_txs:
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx[0].rawTransaction)
            tx_hashes.append((tx_hash, signed_tx[1]))
        except Exception as e:
            logging.error('Error sending raw transaction', e)
            logging.warning('Continuing with smaller number of transactions ...')
            break
    logging.info('Number of transactions sent = %d', len(tx_hashes))

    logging.info('Waiting for transactions')
    for tx_hash in tx_hashes:
        try:
            web3.eth.wait_for_transaction_receipt(tx_hash[0], timeout=30)
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
    parser.add_argument('--receiver', help='The receiver of funds')
    parser.add_argument('--amount', help='The amount to send in wei')
    args = parser.parse_args()

    web3: Web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.bridge_abi) as f:
        contract = web3.eth.contract(address=args.bridge_address, abi=json.load(f))
    account = web3.eth.account.from_key(args.pk)

    logging.info('Starting client')
    run(web3, account, args.receiver, contract, int(args.amount), int(args.bridge_fees), int(args.chainId))
