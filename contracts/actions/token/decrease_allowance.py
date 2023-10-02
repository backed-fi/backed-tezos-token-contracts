import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def DecreaseAllowanceModule():
    DecreaseAllowanceParams: type = sp.record(spender=sp.address, value=sp.nat).layout(("spender", "value"))

    @sp.effects()
    def decreaseAllowance(storage, data):
        '''
        Decreases by `value` amount of tokens as the allowance of `spender` over the caller's tokens

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed DecreaseAllowanceParams
            spender (sp.address) - address that will have allowance to spend caller's tokens
            value (sp.nat) - amount of the tokens that the allowance will be decreased by

        Returns:
        BackedToken storage: Updated storage object
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        decreaseAllowanceParams = sp.unpack(data, DecreaseAllowanceParams).unwrap_some(error="BACKED_TOKEN_DecreaseAllowance_CannotUnpackParams")
      
        updated_storage = storage

        spender_balance = updated_storage.balances.get(
            sp.sender, default=sp.record(balance=0, approvals={})
        )
        spender_balance.approvals[decreaseAllowanceParams.spender] = sp.as_nat(
            spender_balance.approvals[decreaseAllowanceParams.spender] - decreaseAllowanceParams.value,
            error="BACKED_TOKEN_DecreaseAllowance_AllownaceCannotBeLessThanZero",
        )
        updated_storage.balances[sp.sender] = spender_balance

        return updated_storage



 
 
 