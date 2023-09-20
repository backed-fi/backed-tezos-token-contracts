import smartpy as sp
from contracts.shared.storage import StorageModule

@sp.module
def SetDelegateModeModule():
    SetDelegateModeParams: type = sp.bool
    
    ##
    # @dev EIP-712 Function to change the contract delegate mode. Allowed only for owner
    #
    # @param newDelegateMode The new delegate mode for the contract
    #
    # Emits a { DelegateModeChange } event
    @sp.effects()
    def setDelegateMode(storage, data):
        sp.cast(storage, StorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newDelegateMode = sp.unpack(data, SetDelegateModeParams).unwrap_some(error="BACKED_TOKEN_SetDelegateMode_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.delegateMode = newDelegateMode

        # sp.emit(sp.record(delegateMode=newDelegateMode), tag="DelegateModeChange")

        return updated_storage