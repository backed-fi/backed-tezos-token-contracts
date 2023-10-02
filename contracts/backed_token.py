# Fungible Assets - FA12
# Inspired by https://gitlab.com/tzip/tzip/blob/master/A/FA1.2.md

import smartpy as sp
from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule
from contracts.utils.nonce import NonceModule
from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def BackedTokenModule():
    BACKED_TERMS = "https://www.backedassets.fi/legal-documentation"

    class CommonInterface(OwnableModule.OwnableInterface, PausableModule.PausableInterface, NonceModule.NonceInterface):
        def __init__(self, minter, burner):
            OwnableModule.OwnableInterface.__init__(self)
            PausableModule.PausableInterface.__init__(self)
            NonceModule.NonceInterface.__init__(self)
            sp.cast(self.data.storage, BackedTokenStorageModule.BackedToken)
            self.data.storage.terms = BACKED_TERMS
            self.data.storage.balances = sp.big_map()
            self.data.storage.total_supply = 0
            self.data.storage.token_metadata = sp.big_map()
            self.data.storage.metadata = sp.big_map()
            self.data.storage.roles = sp.record(minter=minter, burner=burner)
            self.data.storage.delegateWhitelist= sp.big_map()
            self.data.storage.nonce = sp.big_map()
            self.data.storage.delegateMode=False
           
    class Fa1_2(CommonInterface):
        def __init__(self, metadata, ledger, token_metadata, implementation, minter, burner):
            """
            token_metadata spec: https://gitlab.com/tzip/tzip/-/blob/master/proposals/tzip-12/tzip-12.md#token-metadata
            Token-specific metadata is stored/presented as a Michelson value of type (map string bytes).
            A few of the keys are reserved and predefined:

            - ""          : Should correspond to a TZIP-016 URI which points to a JSON representation of the token metadata.
            - "name"      : Should be a UTF-8 string giving a “display name” to the token.
            - "symbol"    : Should be a UTF-8 string for the short identifier of the token (e.g. XTZ, EUR, …).
            - "decimals"  : Should be an integer (converted to a UTF-8 string in decimal)
                which defines the position of the decimal point in token balances for display purposes.

            contract_metadata spec: https://gitlab.com/tzip/tzip/-/blob/master/proposals/tzip-16/tzip-16.md
            """
            CommonInterface.__init__(self, minter, burner)
            sp.cast(implementation, 
                    sp.big_map[
                        sp.string,
                        sp.record(
                            action=sp.lambda_[
                                sp.record(storage=BackedTokenStorageModule.BackedToken, data=sp.bytes),
                                BackedTokenStorageModule.BackedToken
                            ],
                            only_admin=sp.bool
            )])

            self.data.implementation = implementation
            self.data.storage.metadata = metadata
            self.data.storage.token_metadata = sp.big_map(
                {0: sp.record(token_id=0, token_info=token_metadata)}
            )

            for owner in ledger.items():
                self.data.storage.balances[owner.key] = owner.value
                self.data.storage.total_supply += owner.value.balance

        @sp.private(with_storage='read-write')
        def invoke(self, params):
            sp.cast(params, sp.record(actionName=sp.string, data=sp.bytes))

            updated_storage = self.data.implementation[params.actionName].action(sp.record(storage=self.data.storage, data=params.data))

            self.data.storage = updated_storage

        @sp.entrypoint
        def execute(self, actionName, data):
            '''
            Executes action registered in implementation registry. 

            Params:
            actionName (sp.string) - action's name registered in implementation registry
            data (sp.bytes) - packed action data in proper format
            '''
            assert not self.isPaused(), "BACKED_TOKEN_Paused"

            actionEntry = self.data.implementation.get(actionName, error="BACKED_TOKEN_UnknownAction")

            if actionEntry.only_admin:
                assert self.isOwner(sp.sender), "BACKED_TOKEN_NotAdmin"

            self.invoke(sp.record(actionName=actionName, data=data))
  
        @sp.entrypoint
        def transfer(self, param):
            '''
            Moves a `value` amount of tokens from the 'from' account to `to`.
            '''
            assert not self.isPaused(), "BACKED_TOKEN_Paused"

            sp.cast(
                param,
                sp.record(from_=sp.address, to_=sp.address, value=sp.nat).layout(
                    ("from_ as from", ("to_ as to", "value"))
                ),
            )
            data = sp.pack(param)

            self.invoke(sp.record(actionName='transfer', data=data))

        @sp.entrypoint
        def approve(self, param):
            '''
            Sets a `value` amount of tokens as the allowance of `spender` over the caller's tokens.
            '''
            assert not self.isPaused(), "BACKED_TOKEN_Paused"

            sp.cast(
                param,
                sp.record(spender=sp.address, value=sp.nat).layout(
                    ("spender", "value")
                ),
            )
            data = sp.pack(param)
            self.invoke(sp.record(actionName='approve', data=data))

        @sp.entrypoint
        def getBalance(self, param):
            '''
            Returns the value of tokens owned by `address`.
            '''
            (address, callback) = param
            result = self.data.storage.balances.get(
                address, default=sp.record(balance=0, approvals={})
            ).balance
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getAllowance(self, param):
            '''
            Returns the remaining number of tokens that `spender` will be
            allowed to spend on behalf of `owner`. This is zero by default.
            '''
            (args, callback) = param
            result = self.data.storage.balances.get(
                args.owner, default=sp.record(balance=0, approvals={})
            ).approvals.get(args.spender, default=0)
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getTotalSupply(self, param):
            '''
            Returns the value of tokens in existence.
            '''
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.nat]])
            sp.transfer(self.data.storage.total_supply, sp.tez(0), sp.snd(param))

        @sp.offchain_view()
        def token_metadata(self, token_id):
            '''
            Return the token-metadata URI for the given token. (token_id must be 0).
            '''
            sp.cast(token_id, sp.nat)
            return self.data.storage.token_metadata[token_id]

    class BackedToken(OwnableModule.Ownable, PausableModule.Pausable, NonceModule.Nonce, Fa1_2):
        '''
        This token contract is following the FA1.2 standard. It can be paused by the owner that freezes all actions. It is upgradeable by adding or replacing lambdas for specific actions.
        The contract contains three roles:
        - A minter, that can mint new tokens.
        - A burner, that can burn its own tokens, or contract's tokens.
        - A pauser, that can pause or restore all transfers in the contract.
        - An owner, that can set the three above.
        '''
        
        def __init__(self, owner, metadata, ledger, token_metadata, implementation, minter, burner, pauser):
            '''
            Params:
            owner (sp.address) - the address of the account that will be set as owner of the contract
            metadata (sp.big_map) - contract-specific metadata
            ledger (sp.big_map) - initial balances
            token_metadata (sp.big_map) - token-specific metadata
            implementation (sp.big_map) - implementation of the actions in form of lambdas that take storage and return updated one,
            minter (sp.address) - the address of the account that will be set as minter of the contract
            burner (sp.address) - the address of the account that will be set as burner of the contract
            pauser (sp.address) - the address of the account that will be set as pauser of the contract
            '''
            OwnableModule.Ownable.__init__(self, owner)
            PausableModule.Pausable.__init__(self, pauser)
            NonceModule.Nonce.__init__(self)
            Fa1_2.__init__(self, metadata, ledger, token_metadata, implementation, minter, burner)
       
        @sp.entrypoint
        def updateMetadata(self, key, value):
            '''
            An entrypoint to allow the contract metadata to be updated

            Params:
            key (sp.string) - metadata's key for entry that will be changed
            value (sp.bytes) - updated metadata data
            '''
            assert self.isOwner(sp.sender), "BACKED_TOKEN_NotOwner"
            self.data.storage.metadata[key] = value

        
        @sp.entrypoint
        def updateImplementation(self, implementation):
            '''
            Update the implementation. Callable only by the owner

            Params:
            implementation (sp.big_map) - New implementation of the actions in form of lambdas that take storage and return updated one
            '''
            assert self.isOwner(sp.sender), "BACKED_TOKEN_NotOwner"

            self.data.implementation = implementation

  
