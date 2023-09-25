import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def TransferModule():
    TransferParams: type = sp.record(from_=sp.address, to_=sp.address, value=sp.nat).layout(("from_ as from", ("to_ as to", "value")))

    ##
    # @dev Moves a `value` amount of tokens from `from` to `to` using the
    # allowance mechanism. `value` is then deducted from the caller's
    # allowance.
    #
    # Returns a boolean value indicating whether the operation succeeded.
    #
    # Emits a {Transfer} event.
    @sp.effects()
    def transfer(storage, data):
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        transferParams = sp.unpack(data, TransferParams).unwrap_some(error="BACKED_TOKEN_Transfer_CannotUnpackParams")
      
        updated_storage = storage

        balance_from = updated_storage.balances.get(
            transferParams.from_, default=sp.record(balance=0, approvals={})
        )
        balance_to = updated_storage.balances.get(
            transferParams.to_, default=sp.record(balance=0, approvals={})
        )
        balance_from.balance = sp.as_nat(
            balance_from.balance - transferParams.value, error="BACKED_TOKEN_Transfer_InsufficientBalance"
        )

        balance_to.balance += transferParams.value 
       
        if transferParams.from_ != sp.sender:
            balance_from.approvals[sp.sender] = sp.as_nat(
                balance_from.approvals[sp.sender] - transferParams.value,
                error="BACKED_TOKEN_Transfer_NotAllowed",
            )
       
        updated_storage.balances[transferParams.from_] = balance_from
        updated_storage.balances[transferParams.to_] = balance_to
        return updated_storage


