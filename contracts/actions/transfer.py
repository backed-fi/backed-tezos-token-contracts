import smartpy as sp
# from contracts.actions.shared import shared_module
# from contracts.shared.error_messages import CANNOT_UNPACK

@sp.module
def transfer_module():
    BackedTokenStorage: type = sp.record(
        balances=sp.big_map[sp.address, sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat)],
        total_supply=sp.nat,
        token_metadata=sp.big_map[sp.nat, sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes])],
        metadata=sp.big_map[sp.string, sp.bytes]
    )
    TransferParams: type = sp.record(from_=sp.address, to_=sp.address, value=sp.nat).layout(("from_ as from", ("to_ as to", "value")))

    @sp.effects()
    def transfer(storage, data):
        sp.cast(storage, BackedTokenStorage)
        sp.cast(data, sp.bytes)
        transferParams = sp.unpack(data, TransferParams).unwrap_some(error="CANNOT_UNPACK")
      
        updated_storage = storage

        balance_from = updated_storage.balances.get(
            transferParams.from_, default=sp.record(balance=0, approvals={})
        )
        balance_to = updated_storage.balances.get(
            transferParams.to_, default=sp.record(balance=0, approvals={})
        )
        balance_from.balance = sp.as_nat(
            balance_from.balance - transferParams.value, error="FA1.2_InsufficientBalance"
        )


        balance_to.balance += transferParams.value 
       
        if transferParams.from_ != sp.sender:
            balance_from.approvals[sp.sender] = sp.as_nat(
                balance_from.approvals[sp.sender] - transferParams.value,
                error="FA1.2_NotAllowed",
            )
       
        updated_storage.balances[transferParams.from_] = balance_from
        updated_storage.balances[transferParams.to_] = balance_to
        return updated_storage


