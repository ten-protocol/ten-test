import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract merged PRs from given tag to current main. ')
    parser.add_argument('--from_pk', required=True, help='The private key sending from')
    parser.add_argument('--to_account', required=True, help='The account to send the funds to')
    parser.add_argument('--floor', required=True, help='Only transfer funds above the floor limit')
    args = parser.parse_args()