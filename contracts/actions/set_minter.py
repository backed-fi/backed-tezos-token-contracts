import smartpy as sp
from contracts.shared.storage import StorageModule

@sp.module
def SetMinterModule():
    SetMinterParams: type = sp.address

    @sp.effects()
    def setMinter(storage, data):
        sp.cast(storage, StorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        minter = sp.unpack(data, SetMinterParams).unwrap_some(error="BACKED_TOKEN_SetMinter_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.roles.minter = minter

        return updated_storage