from pysys.constants import PLATFORM, PROJECT


class Processes:
    """Utility wrapper to select process binaries based on the underlying OS of execution."""

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

    @classmethod
    def get_node_bin(cls):
        if PLATFORM == 'darwin':
            return PROJECT.nodeBin_darwin
        elif PLATFORM == 'linux':
            return PROJECT.nodeBin_linux
        return 'node'
