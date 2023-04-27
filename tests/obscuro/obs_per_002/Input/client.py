from web3 import Web3
import secrets, requests, json
import logging, random, argparse, sys
from eth_account.messages import encode_defunct

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def generate_viewing_key(web3, url, address, private_key):
    """Generate a viewing key with the wallet extension. """
    logging.info('Generating viewing key for %s' % private_key)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"address": address}
    response = requests.post('%s/generateviewingkey/' % url, data=json.dumps(data), headers=headers)

    signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)
    data = {"signature": signed_msg.signature.hex(), "address": address}
    requests.post('%s/submitviewingkey/' % url, data=json.dumps(data), headers=headers)


def create_signed_tx(chainId, web3, account, nonce, address, amount):
    """Create a signed transaction to transfer funds to an address. """
    tx = {'nonce': nonce,
          'to': address,
          'value': web3.toWei(amount, 'ether'),
          'gas': 4 * 720000,
          'gasPrice': 21000,
          'chainId': chainId
          }
    return account.sign_transaction(tx)


def run(name, chainId, web3, account, num_accounts, num_iterations):
    """Run a loop of bulk loading transactions into the mempool, draining, and collating results. """
    accounts = [Web3().eth.account.privateKeyToAccount(x).address for x in [secrets.token_hex()]*num_accounts]

    logging.info('Creating and signing %d transactions' % num_iterations)
    txs = []
    for i in range(0, num_iterations):
        tx = create_signed_tx(chainId, web3, account, i, random.choice(accounts), 0.0000000001)
        txs.append((tx, i))

    logging.info('Bulk sending transactions to the network')
    receipts = []
    for tx in txs:
        try:
            receipts.append((web3.eth.send_raw_transaction(tx[0].rawTransaction), tx[1]))
        except:
            logging.info('Error sending raw transaction, sent = %d' % len(receipts))

    logging.info('Waiting for last transaction')
    web3.eth.wait_for_transaction_receipt(receipts[-1][0], timeout=600)

    logging.info('Constructing binned data from the transaction receipts')
    with open('%s.log' % name, 'w') as fp:
        for receipt in receipts:
            block_number_deploy = web3.eth.get_transaction(receipt[0]).blockNumber
            timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
            fp.write('%d %d\n' % (receipt[1], timestamp))

    logging.info('Client %s completed' % name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='event_listener')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-c', '--chainId', help='The network chain Id')
    parser.add_argument('-p', '--pk', help='The accounts private key')
    parser.add_argument('-a', '--num_accounts', help='Number of accounts to send funds to')
    parser.add_argument('-i', '--num_iterations', help='Number of iterations')
    parser.add_argument('-n', '--client_name', help='The logical name of the client')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    account = web3.eth.account.privateKeyToAccount(args.pk)
    name = args.client_name
    logging.info('Starting client %s' % name)

    generate_viewing_key(web3, args.network_http, account.address, args.pk)
    run(name, int(args.chainId), web3, account, int(args.num_accounts), int(args.num_iterations))