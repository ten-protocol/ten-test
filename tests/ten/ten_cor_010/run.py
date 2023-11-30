from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        response = self.get_config()
        self.log.info(response)

        response = self.get_health()
        self.log.info(response)