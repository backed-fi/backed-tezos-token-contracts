import smartpy as sp
from contracts.shared.storage import StorageModule

@sp.module
def ApproveModule():
    ApproveParams: type = sp.record(spender=sp.address, value=sp.nat).layout(("spender", "value"))

    @sp.effects()
    def approve(storage, data):
        sp.cast(storage, StorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        transferParams = sp.unpack(data, ApproveParams).unwrap_some(error="BACKED_TOKEN_Approve_CannotUnpackParams")
      
        updated_storage = storage

        spender_balance = updated_storage.balances.get(
            sp.sender, default=sp.record(balance=0, approvals={})
        )
        alreadyApproved = spender_balance.approvals.get(transferParams.spender, default=0)
        assert (
            alreadyApproved == 0 or transferParams.value == 0
        ), "BACKED_TOKEN_Approve_UnsafeAllowanceChange"
        spender_balance.approvals[transferParams.spender] = transferParams.value
        updated_storage.balances[sp.sender] = spender_balance

        return updated_storage



 
 
 