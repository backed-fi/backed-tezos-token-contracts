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
        ##
        # @dev Initializes the contract in unpaused state and setting the address provided by the deployer as the initial pauser
        #
        # @param pauser - sp.address    pauser account
        def __init__(self, pauser):
            OwnableModule.OwnableInterface.__init__(self)
            self.data.pauser = pauser
            self.data.paused = False
        ##
        # @dev Returns true if the contract is paused, and false otherwise.
        #
        @sp.private(with_storage="read-only")
        def isPaused(self):
            return self.data.paused
        ##
        # @dev Transfers pauser role of the contract to a new account.
        # Can only be called by the current owner.
        #
        # @param param - sp.address     new pauser account
        #
        # Emits a { NewPauser } event
        @sp.entrypoint
        def setPauser(self, param):
            sp.cast(param, sp.address)
            assert self.isOwner(sp.sender), "BACKED_TOKEN_SetPauser_NotOwner"
            self.data.pauser = param

            sp.emit(sp.record(address=self.data.pauser), tag="NewPauser")

        ##
        # @dev Function to set the pause in order to block or restore all
        # actions. Allowed only for pauser
        #
        # @param param - sp.bool    The new pause mode
        #
        # Emits a { PauseModeChange } event
        @sp.entrypoint
        def setPause(self, param):
            sp.cast(param, sp.bool)
            assert sp.sender == self.data.pauser, "BACKED_TOKEN_SetPause_NotPauser"
            self.data.paused = param

            sp.emit(sp.record(mode=self.data.paused), tag="PauseModeChange")