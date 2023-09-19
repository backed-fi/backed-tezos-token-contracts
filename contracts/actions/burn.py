import smartpy as sp
from contracts.actions.shared import shared_module

@sp.module
def burn_module():
    BackedTokenStorage: type = sp.record(
        balances=sp.big_map[sp.address, sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat)],
        total_supply=sp.nat,
        token_metadata=sp.big_map[sp.nat, sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes])],
        metadata=sp.big_map[sp.string, sp.bytes],

    )
    BurnParams: type = sp.record(address=sp.address, value=sp.nat)

    @sp.effects()
    def burn(storage, data):
        sp.cast(storage, BackedTokenStorage)
        sp.cast(data, sp.bytes)
        burnParams = sp.unpack(data, BurnParams).unwrap_some(error="CANNOT_UNPACK")

        updated_storage = storage
        
        receiver_balance = updated_storage.balances.get(
            burnParams.address, default=sp.record(balance=0, approvals={})
        )
        receiver_balance.balance = sp.as_nat(
            receiver_balance.balance - burnParams.value,
            error="FA1.2_InsufficientBalance",
        )
        updated_storage.balances[burnParams.address] = receiver_balance
        updated_storage.total_supply = sp.as_nat(updated_storage.total_supply - burnParams.value)

        return updated_storage