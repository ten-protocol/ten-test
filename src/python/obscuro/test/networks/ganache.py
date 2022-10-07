from obscuro.test.networks.default import Default


class Ganache(Default):
    """A Ganache node giving access to the underlying network."""

    @classmethod
    def chain_id(cls): return 1337
