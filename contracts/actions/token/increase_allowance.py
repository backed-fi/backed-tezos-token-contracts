import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def IncreaseAllowanceModule():
    IncreaseAllowanceParams: type = sp.record(spender=sp.address, value=sp.nat).layout(("spender", "value"))

    @sp.effects()
    def increaseAllowance(storage, data):
        '''
        Increases by `value` amount of tokens as the allowance of `spender` over the caller's tokens

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed IncreaseAllowanceParams
            spender (sp.address) - address that will have allowance to spend caller's tokens
            value (sp.nat) - amount of the tokens that the allowance will be increased by

        Returns:
        BackedToken storage: Updated storage object
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        increaseAllowanceParams = sp.unpack(data, IncreaseAllowanceParams).unwrap_some(error="BACKED_TOKEN_IncreaseAllowance_CannotUnpackParams")
      
        updated_storage = storage

        spender_balance = updated_storage.balances.get(
            sp.sender, default=sp.record(balance=0, approvals={})
        )
        spender_balance.approvals[increaseAllowanceParams.spender] += increaseAllowanceParams.value
        updated_storage.balances[sp.sender] = spender_balance

        return updated_storage



 
 
 