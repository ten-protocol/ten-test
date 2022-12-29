from obscuro.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        self.log.info('Removing entries for environment %s' % self.env)
        self.nonce_db.delete_environment(self.env)

