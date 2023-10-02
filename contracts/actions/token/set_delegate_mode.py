import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetDelegateModeModule():
    SetDelegateModeParams: type = sp.bool
    
    @sp.effects()
    def setDelegateMode(storage, data):
        '''
        EIP-712 Function to change the contract delegate mode. Allowed only for owner

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed SetDelegateModeParams
            newDelegateMode (sp.bool) - the new delegate mode for the contract

        Returns:
        BackedToken storage: Updated storage object

        # Emits:
        # DelegateModeChange event
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newDelegateMode = sp.unpack(data, SetDelegateModeParams).unwrap_some(error="BACKED_TOKEN_SetDelegateMode_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.delegateMode = newDelegateMode

        # sp.emit(sp.record(delegateMode=newDelegateMode), tag="DelegateModeChange")

        return updated_storage