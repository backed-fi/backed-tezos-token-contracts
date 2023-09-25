import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetBurnerModule():
    SetBurnerParams: type = sp.address
    
    ##
    # @dev Function to change the contract burner. Allowed only for owner
    #
    # @param newBurner The address of the new burner
    #
    # Emits a { NewBurner } event
    @sp.effects()
    def setBurner(storage, data):
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newBurner = sp.unpack(data, SetBurnerParams).unwrap_some(error="BACKED_TOKEN_SetBurner_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.roles.burner = newBurner

        # sp.emit(sp.record(address=newBurner), tag="NewBurner")

        return updated_storage