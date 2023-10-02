import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def ApproveModule():
    ApproveParams: type = sp.record(spender=sp.address, value=sp.nat).layout(("spender", "value"))

    @sp.effects()
    def approve(storage, data):
        '''
        Sets a `value` amount of tokens as the allowance of `spender` over the caller's tokens

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed ApproveParams
            spender (sp.address) - address that will have allowance to spend caller's tokens
            value (sp.nat) - amount of the tokens that will be allowed to spend

        Returns:
        BackedToken storage: Updated storage object

        # Emits:
        # Approval event
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        approvalParams = sp.unpack(data, ApproveParams).unwrap_some(error="BACKED_TOKEN_Approve_CannotUnpackParams")
      
        updated_storage = storage

        spender_balance = updated_storage.balances.get(
            sp.sender, default=sp.record(balance=0, approvals={})
        )
        alreadyApproved = spender_balance.approvals.get(approvalParams.spender, default=0)
        assert (
            alreadyApproved == 0 or approvalParams.value == 0
        ), "BACKED_TOKEN_Approve_UnsafeAllowanceChange"
        spender_balance.approvals[approvalParams.spender] = approvalParams.value
        updated_storage.balances[sp.sender] = spender_balance

        return updated_storage



 
 
 