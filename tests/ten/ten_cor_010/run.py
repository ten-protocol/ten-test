from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        response = self.obscuro_config()
        self.log.info(response)

        response = self.obscuro_health()
        self.log.info(response)