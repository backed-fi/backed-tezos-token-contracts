import smartpy as sp
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def DelegatedTransferModule():
    DelegatedTransferParams: type = sp.record(owner=sp.key, spender=sp.address, amount=sp.nat, deadline=sp.timestamp, signature=sp.signature)

    @sp.effects()
    def delegatedTransfer(storage, data):
        '''
        Perform an intended transfer on one account's behalf, from another account,
        who actually pays fees for the transaction. Allowed only if the sender
        is whitelisted, or the delegateMode is set to true

        Params:
        storage (BackedToken storage) - current storage of the BackedToken contract
        data (sp.bytes) - packed DelegatedTransferParams
            owner (sp.address) - token owner's public key (Authorizer)
            spender (sp.address) - spender's address
            amount (sp.nat) - amount of allowance
            deadline (sp.timestamp) - expiration time, seconds since the epoch
            signature (sp.signature) - token owner's signature of the message

        Returns:
        BackedToken storage: Updated storage object
        '''
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        params = sp.unpack(data, DelegatedTransferParams).unwrap_some(error="BACKED_TOKEN_DelegatedTransfer_CannotUnpackParams")
        
        assert params.deadline > sp.now, 'BACKED_TOKEN_DelegatedTransfer_ExpiredSignature'
        updated_storage = storage

        assert updated_storage.delegateMode or updated_storage.delegateWhitelist[sp.sender], 'BACKED_TOKEN_DelegatedTransfer_UnauthorizedDelegate'
        
        owner_address = sp.to_address(sp.implicit_account(sp.hash_key(params.owner)))
        
        nonce = updated_storage.nonce.get(owner_address, default=0)

        message = sp.pack(sp.record(
            deadline=params.deadline, spender=params.spender, amount=params.amount, nonce=nonce
        ))

        assert sp.check_signature(params.owner, params.signature, message), 'BACKED_TOKEN_DelegatedTransfer_InvalidSigner'

        balance_from = updated_storage.balances.get(
            owner_address, default=sp.record(balance=0, approvals={})
        )
        balance_to = updated_storage.balances.get(
            params.spender, default=sp.record(balance=0, approvals={})
        )
        balance_from.balance = sp.as_nat(
            balance_from.balance - params.amount, error="BACKED_TOKEN_DelegatedTransfer_InsufficientBalance"
        )

        balance_to.balance += params.amount 
       
        updated_storage.balances[owner_address] = balance_from
        updated_storage.balances[params.spender] = balance_to

        updated_storage.nonce[owner_address] = nonce + 1

        return updated_storage