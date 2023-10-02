import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def MintModule():
    MintParams: type = sp.record(address=sp.address, value=sp.nat)

    @sp.effects()
    def mint(storage, data):
        '''
        Function to mint tokens. Allowed only for minter

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed MintParams
            account (sp.address) - the account to which the tokens will be minted
            amount (sp.nat) - the amount of tokens to be minted

        Returns:
        BackedToken storage: Updated storage object
        '''
        assert sp.sender == storage.roles.minter, "BACKED_TOKEN_Mint_NotMinter"

        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        mintParams = sp.unpack(data, MintParams).unwrap_some(error="BACKED_TOKEN_Mint_CannotUnpackParams")
        
        updated_storage = storage

        receiver_balance = updated_storage.balances.get(
            mintParams.address, default=sp.record(balance=0, approvals={})
        )
        receiver_balance.balance += mintParams.value
        updated_storage.balances[mintParams.address] = receiver_balance
        updated_storage.total_supply += mintParams.value

        return updated_storage