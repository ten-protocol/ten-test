# HTTP proxy to log traffic between web3 and the wallet extension. Note this is still in development.
#
import argparse, sys, socket
from _thread import *


def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', int(args.port)))
    sock.listen(1)

    sys.stdout.write('Connection bound and listening')
    sys.stdout.flush()

    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        start_new_thread(proxy_server, (conn, data, addr))


def proxy_server(conn, addr, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.remote_host, int(args.remote_port)))
    sock.send(data)

    while True:
        reply = sock.recv(1024)
        if len(reply) > 0:
            conn.send(reply)

            dar = float(len(reply))
            dar = float(dar/1024)
            dar = "%.3s" % (str(dar))
            dar = "%s KB" % (dar)
            FP.write("[*] Request Done: %s => %s <=\n" % (str(addr[0]), str(dar)))
            FP.flush()
        else:
            break

    sock.close()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http proxy.')
    parser.add_argument('--port', help='Port to bind to')
    parser.add_argument('--remote_host', help='Remote hostname to connect to')
    parser.add_argument('--remote_port', help='Remote port to connect to')
    parser.add_argument('--filename', help='Log messages to this filename')
    args = parser.parse_args()

    sys.stdout.write('Connection to remote url %s:%d' % (args.remote_host, int(args.remote_port)))
    sys.stdout.flush()
    FP = open(args.filename, 'w')

    start()
