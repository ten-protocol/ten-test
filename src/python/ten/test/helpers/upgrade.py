import os
from pysys.constants import FOREGROUND, PROJECT
from ten.test.utils.properties import Properties


class UpgradeL1ContractsHelper:
    """A wrapper over upgrading a local testnet."""

    def __init__(self, test):
        """Create an instance."""
        self.test = test

        props = Properties()
        self.binary = props.go_binary()
        self.docker_image = 'testnetobscuronet.azurecr.io/obscuronet/hardhatdeployer:latest'
        self.network_config_addr = props.l1_network_config_address()

    def run(self):
        """Run the upgrade. """
        self.test.log.info('Running the L1 contract upgrade process ...')

        arguments = ['run', './testnet/launcher/l1upgrade/cmd',
                     '-network_config_addr=%s' % self.network_config_addr,
                     '-docker_image=%s' % self.docker_image]

        stdout = os.path.join(self.test.output, 'upgrade_network.out')
        stderr = os.path.join(self.test.output, 'upgrade_network.err')
        dir = os.path.join(os.path.dirname(PROJECT.root), 'go-ten')

        hprocess = self.test.startProcess(command=self.binary, displayName='go',
                                          workingDir=dir, environs=os.environ, quiet=True,
                                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND)

        self.test.assertGrep(file=stdout, expr='L1 upgrades were successfully completed...')
        return hprocess
