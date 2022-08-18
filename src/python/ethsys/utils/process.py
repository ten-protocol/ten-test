from pysys.constants import PLATFORM, PROJECT


class Processes:

    @classmethod
    def get_solidity_compiler(cls):
        if PLATFORM == 'darwin':
            return PROJECT.solcBin_darwin
        elif PLATFORM == 'linux':
            return PROJECT.solcBin_linux
        return 'solc'

    @classmethod
    def get_ganache_bin(cls):
        if PLATFORM == 'darwin':
            return PROJECT.ganacheBin_darwin
        elif PLATFORM == 'linux':
            return PROJECT.ganacheBin_linux
        return 'ganache-cli'
