import smartpy as sp

from contracts.utils.ownable import OwnableModule 

@sp.module
def PausableModule():
    class PausableInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def isPaused(self, sender):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""
            return True

    class Pausable(OwnableModule.OwnableInterface):
        def __init__(self, pauser):
            OwnableModule.OwnableInterface.__init__(self)
            self.data.pauser = pauser
            self.data.paused = False

        @sp.private(with_storage="read-only")
        def isPaused(self):
            return self.data.paused

        @sp.entrypoint
        def setPauser(self, param):
            sp.cast(param, sp.address)
            assert self.isOwner(sp.sender), "BACKED_TOKEN_SetPauser_NotOwner"
            self.data.pauser = param

        @sp.entrypoint
        def setPause(self, param):
            sp.cast(param, sp.bool)
            assert sp.sender == self.data.pauser, "BACKED_TOKEN_SetPause_NotPauser"
            self.data.paused = param