from ethsys.networks.ganache import Ganache
from ethsys.networks.ropsten import Ropsten
from ethsys.networks.obscuro import Obscuro
from ethsys.networks.obscuro import ObscuroL1, ObscuroL1Local, ObscuroL1Dev


class NetworkFactory:
    """Factory class to return a network node for a given mode the test is run in. """

    @classmethod
    def get_network(cls, environment):
        """Get the network node.

        Currently supported networks are ganache, ropsten and obscuro.local (obscuro being
        the default network used in all tests)
        """
        if environment == 'obscuro.dev':
            return Obscuro
        elif environment == 'obscuro.local':
            return Obscuro
        elif environment == 'ropsten':
            return Ropsten
        elif environment == 'ganache':
            return Ganache
        return Obscuro

    @classmethod
    def get_l1_network(cls, environment):
        """Get the layer 1 network used by a layer 2.

        Currently this is only for Obscuro networks and returns either a node in the L1 running
        in a local deployment, or in the testnet deployment.
        """
        if environment == 'obscuro.dev':
            return ObscuroL1Dev
        elif environment == 'obscuro.local':
            return ObscuroL1Local
        return ObscuroL1