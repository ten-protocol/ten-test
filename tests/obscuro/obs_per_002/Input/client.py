from web3 import Web3
import secrets, logging, random, argparse, sys, os
from collections import OrderedDict

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


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
        receipts.append((web3.eth.send_raw_transaction(tx[0].rawTransaction), tx[1]))

    logging.info('Waiting for last transaction')
    web3.eth.wait_for_transaction_receipt(receipts[-1][0], timeout=600)

    logging.info('Constructing binned data from the transaction receipts')
    bins = OrderedDict()
    for receipt in receipts:
        block_number_deploy = web3.eth.get_transaction(receipt[0]).blockNumber
        timestamp = int(web3.eth.get_block(block_number_deploy).timestamp)
        bins[timestamp] = 1 if timestamp not in bins else bins[timestamp] + 1

    times = list(bins)
    first = times[0]
    with open('data_%s.bin' % name, 'w') as fp:
        for i in range(times[0], times[-1]+1):
            num = bins[i] if i in bins else 0
            fp.write('%d %d\n' % ((i - first), num))


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
    name = args.name