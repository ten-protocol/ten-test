from obscuro.test.networks.default import Default


class Ganache(Default):
    """A Ganache node giving access to the underlying network."""

    def chain_id(self): return 1337
