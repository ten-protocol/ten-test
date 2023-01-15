import argparse, sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http proxy.')
    parser.add_argument('--port', help='Port to bind to')
    parser.add_argument('--remote_host', help='Remote hostname to connect to')
    parser.add_argument('--remote_port', help='Remote port to connect to')
    parser.add_argument('--filename', help='Log messages to this filename')
    args = parser.parse_args()

    REMOTE_URL = args.remote_url
    sys.stdout.write('Connection to remote url %s' % REMOTE_URL)
    sys.stdout.flush()
    FP = open(args.filename, 'w')
