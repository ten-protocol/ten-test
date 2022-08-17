from pysys.basetest import BaseTest


class EthereumTest(BaseTest):

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.env = 'obscuro' if self.mode is None else self.mode
