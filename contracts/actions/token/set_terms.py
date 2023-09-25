import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def SetTermsModule():
    SetTermsParams: type = sp.string
    
    ##
    # @dev Function to change the contract terms. Allowed only for owner
    #
    # @param newTerms A string with the terms. Usually a web or IPFS link.
    #
    # Emits a { NewTerms } event
    @sp.effects()
    def setTerms(storage, data):
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        newTerms = sp.unpack(data, SetTermsParams).unwrap_some(error="BACKED_TOKEN_SetBurner_CannotUnpackParams")

        updated_storage = storage
        
        updated_storage.terms = newTerms

        # sp.emit(sp.record(terms=newTerms), tag="NewTerms")

        return updated_storage