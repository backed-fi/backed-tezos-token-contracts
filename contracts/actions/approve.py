import smartpy as sp
# from contracts.actions.shared import shared_module
# from contracts.shared.error_messages import CANNOT_UNPACK

@sp.module
def approve_module():
    BackedTokenStorage: type = sp.record(
        balances=sp.big_map[sp.address, sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat)],
        total_supply=sp.nat,
        token_metadata=sp.big_map[sp.nat, sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes])],
        metadata=sp.big_map[sp.string, sp.bytes],

    )
    ApproveParams: type = sp.record(spender=sp.address, value=sp.nat).layout(("spender", "value"))

    @sp.effects()
    def approve(storage, data):
        sp.cast(storage, BackedTokenStorage)
        sp.cast(data, sp.bytes)
        transferParams = sp.unpack(data, ApproveParams).unwrap_some(error="CANNOT_UNPACK")
      
        updated_storage = storage

        # assert not self.is_paused_(), "FA1.2_Paused"
        spender_balance = updated_storage.balances.get(
            sp.sender, default=sp.record(balance=0, approvals={})
        )
        alreadyApproved = spender_balance.approvals.get(transferParams.spender, default=0)
        # assert (
        #     alreadyApproved == 0 or param.value == 0
        # ), "FA1.2_UnsafeAllowanceChange"
        spender_balance.approvals[transferParams.spender] = transferParams.value
        updated_storage.balances[sp.sender] = spender_balance

        return updated_storage



 
 
 