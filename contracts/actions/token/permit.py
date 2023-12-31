import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def PermitModule():
    PermitParams: type = sp.record(owner=sp.key, spender=sp.address, amount=sp.nat, deadline=sp.timestamp, signature=sp.signature)

    @sp.effects()
    def permit(storage, data):
        '''
        Update allowance with a signed permit. Allowed only if
        the sender is whitelisted, or the delegateMode is set to true
        
        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed PermitParams
            owner (sp.address) - token owner's public key (Authorizer)
            spnder (sp.address) - spender's address
            amount (sp.nat) - amount of allowance
            deadline (sp.timestamp) - expiration time, seconds since the epoch
            signature (sp.signature) - token owner's signature of the message

        Returns:
        BackedToken storage: Updated storage object
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        params = sp.unpack(data, PermitParams).unwrap_some(error="BACKED_TOKEN_Permit_CannotUnpackParams")

        assert params.deadline > sp.now, 'BACKED_TOKEN_Permit_ExpiredSignature'
        updated_storage = storage

        assert updated_storage.delegateMode or updated_storage.delegateWhitelist[sp.sender], 'BACKED_TOKEN_Permit_UnauthorizedDelegate'

        
        owner_address = sp.to_address(sp.implicit_account(sp.hash_key(params.owner)))
        
        nonce = updated_storage.nonce.get(owner_address, default=0)

        message = sp.pack(sp.record(
            deadline=params.deadline, spender=params.spender, amount=params.amount, nonce=nonce
        ))

        assert sp.check_signature(params.owner, params.signature, message), 'BACKED_TOKEN_Permit_InvalidSigner'

        owner_balance = updated_storage.balances.get(
            owner_address, default=sp.record(balance=0, approvals={})
        )
        alreadyApproved = owner_balance.approvals.get(params.spender, default=0)
        assert (
            alreadyApproved == 0 or params.amount == 0
        ), "BACKED_TOKEN_Permit_UnsafeAllowanceChange"

        owner_balance.approvals[params.spender] = params.amount
        updated_storage.balances[owner_address] = owner_balance

        updated_storage.nonce[owner_address] = nonce + 1

        return updated_storage