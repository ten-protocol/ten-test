from obscuro.test.networks.ganache import Ganache
from obscuro.test.networks.goerli import Goerli
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.networks.obscuro import ObscuroL1, ObscuroL1Local, ObscuroL1Dev, ObscuroL1Sim


class NetworkFactory:
    """Factory class to return a network node for a given mode the test is run in. """

    @classmethod
    def get_network(cls, environment):
        """Get the network node."""
        if environment == 'obscuro.dev':
            return Obscuro
        elif environment == 'obscuro.local':
            return Obscuro
        elif environment == 'obscuro.sim':
            return Obscuro
        elif environment == 'goerli':
            return Goerli
        elif environment == 'ganache':
            return Ganache
        return Obscuro

    @classmethod
    def get_l1_network(cls, environment):
        """Get the layer 1 network used by a layer 2."""
        if environment == 'obscuro.dev':
            return ObscuroL1Dev
        elif environment == 'obscuro.local':
            return ObscuroL1Local
        elif environment == 'obscuro.sim':
            return ObscuroL1Sim
        return ObscuroL1