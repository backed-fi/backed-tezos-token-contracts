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
            '''
            Initializes the contract in unpaused state and setting the address provided by the deployer as the initial pauser

            Params:
            pauser (sp.address) - initial pauser account
            '''
            OwnableModule.OwnableInterface.__init__(self)
            self.data.pauser = pauser
            self.data.paused = False
       
        @sp.private(with_storage="read-only")
        def isPaused(self):
            '''
            Returns true if the contract is paused, and false otherwise.
            '''
            return self.data.paused
        
        @sp.entrypoint
        def setPauser(self, param):
            '''
            Transfers pauser role of the contract to a new account.
            Can only be called by the current owner.

            Params:
            param (sp.address) - new pauser account

            Emits:
            NewPauser event
            '''
            sp.cast(param, sp.address)
            assert self.isOwner(sp.sender), "BACKED_TOKEN_SetPauser_NotOwner"
            self.data.pauser = param

            sp.emit(sp.record(address=self.data.pauser), tag="NewPauser")

        @sp.entrypoint
        def setPause(self, param):
            '''
            Function to set the pause in order to block or restore all actions. Allowed only for pauser

            Params:
            param (sp.bool) - the new pause mode

            Emits:
            PauseModeChange event
            '''
            sp.cast(param, sp.bool)
            assert sp.sender == self.data.pauser, "BACKED_TOKEN_SetPause_NotPauser"
            self.data.paused = param

            sp.emit(sp.record(mode=self.data.paused), tag="PauseModeChange")