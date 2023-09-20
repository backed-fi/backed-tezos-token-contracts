import smartpy as sp

@sp.module
def NonceModule():
    class NonceInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def getNonce(self, owner):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""
            return 0
        @sp.private(with_storage="read-write")
        def useNonce(self, owner):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""

    class Nonce(sp.Contract):
        def __init__(self):
            self.data.storage.nonce = sp.big_map()

        @sp.private(with_storage="read-only")
        def getNonce(self, owner):
            return self.data.storage.nonce.get(owner, default = 0)
        
        @sp.private(with_storage="read-write")
        def useNonce(self, owner):
            nonce = self.data.storage.nonce.get(owner, default = 0)

            self.data.storage.nonce[owner] = nonce + 1
        