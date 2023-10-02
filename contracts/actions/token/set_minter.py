import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetMinterModule():
    SetMinterParams: type = sp.address

    @sp.effects()
    def setMinter(storage, data):
        '''
        Function to change the contract minter. Allowed only for owner

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed SetMinterParams
            newMinter (sp.address) - the address of the new minter

        Returns:
        BackedToken storage: Updated storage object

        # Emits:
        # NewMinter event
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newMinter = sp.unpack(data, SetMinterParams).unwrap_some(error="BACKED_TOKEN_SetMinter_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.roles.minter = newMinter

        # sp.emit(sp.record(address=newMinter), tag="NewMinter")

        return updated_storage