import smartpy as sp

@sp.module
def OwnableModule():
    class OwnableInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def isOwner(self, sender):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""
            return True

    class Ownable(sp.Contract):
        def __init__(self, owner):
            self.data.owner = owner

        @sp.private(with_storage="read-only")
        def isOwner(self, sender):
            return sender == self.data.owner

        @sp.entrypoint
        def transferOwnership(self, params):
            sp.cast(params, sp.address)
            assert self.isOwner(sp.sender), "Ownable_NotOwner"
            self.data.owner = params

        @sp.entrypoint
        def renounceOwnership(self):
            assert self.isOwner(sp.sender), "Ownable_NotOwner"
            # null address
            self.data.owner = sp.address("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU")  

        @sp.entrypoint()
        def getOwner(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.address]])
            sp.transfer(self.data.owner, sp.tez(0), sp.snd(param))

        @sp.onchain_view()
        def get_owner(self):
            return self.data.owner
