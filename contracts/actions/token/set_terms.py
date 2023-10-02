import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetTermsModule():
    SetTermsParams: type = sp.string
    
    @sp.effects()
    def setTerms(storage, data):
        '''
        Function to change the contract terms. Allowed only for owner

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed SetTermsParams
            newTerms (sp.string) - a string with the terms. Usually a web or IPFS link.
        Returns:
        BackedToken storage: Updated storage object

        # Emits:
        # NewTerms event
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newTerms = sp.unpack(data, SetTermsParams).unwrap_some(error="BACKED_TOKEN_SetBurner_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.terms = newTerms

        # sp.emit(sp.record(terms=newTerms), tag="NewTerms")

        return updated_storage