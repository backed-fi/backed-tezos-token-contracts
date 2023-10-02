import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetDelegateWhitelistModule():
    SetDelegateWhitelistParams: type = sp.record(address=sp.address, status=sp.bool)
    
    @sp.effects()
    def setDelegateWhitelist(storage, data):
        '''
        EIP-712 Function to change the delegate status. Allowed only for owner

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed SetDelegateModeParams
            whitelistAddress (sp.bool) - the address for which to change the delegate status
            status (sp.bool) - the new delegate status

        Returns:
        BackedToken storage: Updated storage object

        # Emits:
        # DelegateWhitelistChange event
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        params = sp.unpack(data, SetDelegateWhitelistParams).unwrap_some(error="BACKED_TOKEN_SetDelegateMode_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.delegateWhitelist[params.address] = params.status

        # sp.emit(sp.record(address=params.address, status=params.status), tag="DelegateWhitelistChange")

        return updated_storage