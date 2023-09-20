import smartpy as sp
from contracts.shared.storage import StorageModule

@sp.module
def SetBurnerModule():
    SetBurnerParams: type = sp.address

    @sp.effects()
    def setBurner(storage, data):
        sp.cast(storage, StorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        burner = sp.unpack(data, SetBurnerParams).unwrap_some(error="BACKED_TOKEN_SetBurner_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.roles.burner = burner

        return updated_storage