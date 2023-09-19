import smartpy as sp
from contracts.shared.storage import storage_module

@sp.module
def mint_module():
    MintParams: type = sp.record(address=sp.address, value=sp.nat)

    @sp.effects()
    def mint(storage, data):
        sp.cast(storage, storage_module.backed_token)
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