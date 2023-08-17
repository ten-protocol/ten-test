from obscuro.test.networks.default import Default
from obscuro.test.networks.ganache import Ganache
from obscuro.test.networks.goerli import Goerli
from obscuro.test.networks.arbitrum import Arbitrum
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.networks.obscuro import ObscuroL1, ObscuroL1Local, ObscuroL1Dev, ObscuroL1Sim


class NetworkFactory:
    """Factory class to return a network node for a given mode the test is run in.

    Note that network instances should never be accessed directly, but always through the factory class.
    """

    @classmethod
    def get_network(cls, test):
        """Get the network node."""
        if test.env in ['obscuro', 'obscuro.dev', 'obscuro.local', 'obscuro.sim']:
            network = Obscuro()
            network.PORT = test.wallet_extension.port
            network.WS_PORT = test.wallet_extension.ws_port
            network.ID = test.wallet_extension.user_id
            return network
        elif test.env == 'goerli':
            return Goerli()
        elif test.env == 'ganache':
            return Ganache()
        elif test.env == 'arbitrum':
            return Arbitrum()
        return Default()

    @classmethod
    def get_l1_network(cls, test):
        """Get the layer 1 network used by a layer 2."""
        if test.env == 'obscuro':
            return ObscuroL1()
        elif test.env == 'obscuro.dev':
            return ObscuroL1Dev()
        elif test.env == 'obscuro.local':
            return ObscuroL1Local()
        elif test.env == 'obscuro.sim':
            return ObscuroL1Sim()
        return Default()
