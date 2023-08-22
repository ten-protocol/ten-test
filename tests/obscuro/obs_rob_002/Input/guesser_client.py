from web3 import Web3
import logging, random
import argparse, json, sys, time

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='guesser_client')
    parser.add_argument('-u', '--network_http', help='Connection URL')
    parser.add_argument('-a', '--address', help='Address of the contract')
    parser.add_argument('-b', '--contract_abi', help='Abi of the contract')
    args = parser.parse_args()

    web3 = Web3(Web3.HTTPProvider(args.network_http))
    with open(args.contract_abi) as f:
        contract = web3.eth.contract(address=args.address, abi=json.load(f))

    logging.info('Client running')
    while True:
        guess = random.randint(0, 25)
        ret = contract.functions.guess(guess).call()
        if ret == 1:
            logging.info("Guess is %d, need to go higher", guess)
        elif ret == -1:
            logging.info("Guess is %d, need to go lower", guess)
        else:
            logging.info("You've guessed the secret %s", guess)

        time.sleep(0.1)

