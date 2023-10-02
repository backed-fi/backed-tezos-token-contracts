import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetBurnerModule():
    SetBurnerParams: type = sp.address
    
    @sp.effects()
    def setBurner(storage, data):
        '''
        Function to change the contract burner. Allowed only for owner

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed SetBurnerParams
            newBurner (sp.address) - the address of the new burner

        Returns:
        BackedToken storage: Updated storage object

        # Emits:
        # NewBurner event
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newBurner = sp.unpack(data, SetBurnerParams).unwrap_some(error="BACKED_TOKEN_SetBurner_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.roles.burner = newBurner

        # sp.emit(sp.record(address=newBurner), tag="NewBurner")

        return updated_storage