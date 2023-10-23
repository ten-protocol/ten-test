from web3 import Web3
import logging, requests, time, os, secrets, argparse, json, sys
from eth_account.messages import encode_defunct

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def join(host, port):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get('%s:%d/v1/join/' % (host, port),  headers=headers)
    return response.text


def register(account, host, port, user_id):
    text_to_sign = "Register " + user_id + " for " + str(account.address).lower()
    eth_message = f"{text_to_sign}"
    encoded_message = encode_defunct(text=eth_message)
    signature = account.sign_message(encoded_message)

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"signature": signature['signature'].hex(), "message": text_to_sign}
    response = requests.post('%s:%d/v1/authenticate/?u=%s' % (host, port, user_id),
                             data=json.dumps(data), headers=headers)
    return response


def wait(file, timeout=20):
    start = time.time()
    while True:
        if time.time() > start + timeout:
            logging.error('Timed out waiting for the trigger file')
            break
        time.sleep(0.01)
        if os.path.exists(file): return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='error_client')
    parser.add_argument('-t', '--host', help='Connection host')
    parser.add_argument('-p', '--port', help='Connection port')
    parser.add_argument('-a', '--pk', help='Account private key')
    parser.add_argument('-b', '--balance', help='Expected balance')
    parser.add_argument('-f', '--trigger', help='Path to the trigger file')
    parser.add_argument('-n', '--iterations', help='Number of iterations to perform')
    parser.add_argument('-x', '--additional_accounts', help='Additional accounts to register each iteration')
    args = parser.parse_args()

    account = Web3().eth.account.privateKeyToAccount(args.pk)
    logging.info('Client running ... waiting for trigger file')
    wait(args.trigger)
    logging.info('Client starting ... trigger file seen')

    for i in range(0, int(args.iterations)):
        logging.info('Joining network using url %s:%s/v1/join/', args.host, args.port)
        user_id = join(args.host, int(args.port))

        logging.info('Registering account %s with the network on user id %s', account.address, user_id)
        response = register(account, args.host, int(args.port), user_id)
        logging.info('Registration success was %s', response.ok)
        web3 = Web3(Web3.HTTPProvider('%s:%s/v1/?u=%s' % (args.host, args.port, user_id)))

        for j in range(0, int(args.additional_accounts)):
            _account = Web3().eth.account.privateKeyToAccount(secrets.token_hex(32))
            response = register(_account, args.host, int(args.port), user_id)
            logging.info('Additional clients, registration for %s success was %s', _account.address, response.ok)

        balance = web3.eth.get_balance(account.address)
        logging.info('Balance is %d', balance)
        time.sleep(0.01)

    logging.info('Client completed')
