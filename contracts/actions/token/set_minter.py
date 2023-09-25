import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetMinterModule():
    SetMinterParams: type = sp.address

    ##
    # @dev Function to change the contract minter. Allowed only for owner
    #
    # @param newMinter The address of the new minter
    #
    # Emits a { NewMinter } event
    @sp.effects()
    def setMinter(storage, data):
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newMinter = sp.unpack(data, SetMinterParams).unwrap_some(error="BACKED_TOKEN_SetMinter_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.roles.minter = newMinter

        # sp.emit(sp.record(address=newMinter), tag="NewMinter")

        return updated_storage