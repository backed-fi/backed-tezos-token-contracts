import smartpy as sp
from contracts.shared.storage import StorageModule

@sp.module
def SetDelegateWhitelistModule():
    SetDelegateWhitelistParams: type = sp.record(address=sp.address, status=sp.bool)
    
    ##
    # @dev EIP-712 Function to change the delegate status of account.
    # Allowed only for owner
    #
    # @param whitelistAddress  The address for which to change the delegate status
    # @param status            The new delegate status
    #
    # Emits a { DelegateWhitelistChange } event
    @sp.effects()
    def setDelegateWhitelist(storage, data):
        sp.cast(storage, StorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        params = sp.unpack(data, SetDelegateWhitelistParams).unwrap_some(error="BACKED_TOKEN_SetDelegateMode_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.delegateWhitelist[params.address] = params.status

        # sp.emit(sp.record(address=params.address, status=params.status), tag="DelegateWhitelistChange")

        return updated_storage