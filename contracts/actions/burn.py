import smartpy as sp
from contracts.shared.storage import storage_module

@sp.module
def burn_module():
    BurnParams: type = sp.record(address=sp.address, value=sp.nat)

    @sp.effects()
    def burn(storage, data):
        sp.cast(storage, storage_module.backed_token)
        sp.cast(data, sp.bytes)
        burnParams = sp.unpack(data, BurnParams).unwrap_some(error="BACKED_TOKEN_Burn_CannotUnpackParams")

        updated_storage = storage
        
        receiver_balance = updated_storage.balances.get(
            burnParams.address, default=sp.record(balance=0, approvals={})
        )
        receiver_balance.balance = sp.as_nat(
            receiver_balance.balance - burnParams.value,
            error="BACKED_TOKEN_Burn_InsufficientBalance",
        )
        updated_storage.balances[burnParams.address] = receiver_balance
        updated_storage.total_supply = sp.as_nat(updated_storage.total_supply - burnParams.value)

        return updated_storage