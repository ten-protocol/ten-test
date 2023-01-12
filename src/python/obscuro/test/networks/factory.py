from obscuro.test.networks.ganache import Ganache
from obscuro.test.networks.goerli import Goerli
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.networks.obscuro import ObscuroL1, ObscuroL1Local, ObscuroL1Dev, ObscuroL1Sim


class NetworkFactory:
    """Factory class to return a network node for a given mode the test is run in. """

    @classmethod
    def get_network(cls, test):
        """Get the network node."""
        if test.env == 'obscuro.dev':
            return Obscuro
        elif test.env == 'obscuro.local':
            return Obscuro
        elif test.env == 'obscuro.sim':
            return Obscuro
        elif test.env == 'goerli':
            return Goerli
        elif test.env == 'ganache':
            return Ganache
        return Obscuro

    @classmethod
    def get_l1_network(cls, test):
        """Get the layer 1 network used by a layer 2."""
        if test.env == 'obscuro.dev':
            return ObscuroL1Dev
        elif test.env == 'obscuro.local':
            return ObscuroL1Local
        elif test.env == 'obscuro.sim':
            return ObscuroL1Sim
        return ObscuroL1