import smartpy as sp
# from contracts.actions.shared import shared_module
# from contracts.shared.error_messages import CANNOT_UNPACK

@sp.module
def mint_module():
    BackedTokenStorage: type = sp.record(
        balances=sp.big_map[sp.address, sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat)],
        total_supply=sp.nat,
        token_metadata=sp.big_map[sp.nat, sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes])],
        metadata=sp.big_map[sp.string, sp.bytes],

    )
    MintParams: type = sp.record(address=sp.address, value=sp.nat)

    @sp.effects()
    def mint(storage, data):
        sp.cast(storage, BackedTokenStorage)
        sp.cast(data, sp.bytes)
        mintParams = sp.unpack(data, MintParams).unwrap_some(error="CANNOT_UNPACK")
        
        updated_storage = storage

        receiver_balance = updated_storage.balances.get(
            mintParams.address, default=sp.record(balance=0, approvals={})
        )
        receiver_balance.balance += mintParams.value
        updated_storage.balances[mintParams.address] = receiver_balance
        updated_storage.total_supply += mintParams.value

        return updated_storage