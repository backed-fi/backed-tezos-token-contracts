import smartpy as sp

from contracts.backed_token import BackedTokenModule

from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule

@sp.module
def BackedTokenFactoryModule():
    BACKED_TERMS = "https://www.backedassets.fi/legal-documentation"
    class BackedFactory(OwnableModule.Ownable):
        '''
        Factory contract, used for creating new, upgradable tokens.

        The contract contains one role:
        - An owner, which can deploy new tokens
        '''
        def __init__(self, implementation, metadata, owner):
            '''
            Params:
            owner (sp.address) - the address of the account that will be set as owner of the contract
            implementation (sp.big_map) - implementation of the actions in form of lambdas that take storage 
                and return updated one, that can be invoked in newly deployed token
            '''
            OwnableModule.Ownable.__init__(self, owner)
            self.data.implementation = implementation
            self.data.metadata = metadata
        
        @sp.entrypoint
        def deployToken(self, tokenOwner, minter, burner, pauser, metadata, name, symbol, icon, decimals):
            '''
            Deploy and configures new instance of BackedFi Token. Callable only by the factory owner

            Params:
            name (sp.bytes) - the name that the newly created token will have
            symbol (sp.bytes) - the symbol that the newly created token will have
            icon (sp.bytes) - the icon that the newly created token will have
            decimals (sp.bytes) - the number of decimals that the newly created token will have
            tokenOwner (sp.address) - the address of the account to which the owner role will be assigned

            Emits:
            NewToken event
            '''
            assert self.isOwner(sp.sender), "BACKED_TOKEN_Factory_NotOwner"

            token_metadata = {
                "decimals": decimals,  # Mandatory by the spec
                "name": name,
                "symbol": symbol,
                "icon": icon,
            }
            token_metadata_storage = sp.big_map(
                {0: sp.record(token_id=0, token_info=token_metadata)}
            )

            metadata_storage = sp.big_map({"" : metadata})

            balances = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.address,
                    sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat),
                ],
            )
            
            newToken = sp.create_contract(
                BackedTokenModule.BackedToken,
                None,
                sp.mutez(0),
                sp.record(
                    owner=tokenOwner,
                    pauser=pauser,
                    paused=False,
                    metadata=metadata_storage,
                    storage=sp.record(
                        balances=balances,
                        total_supply=0,
                        token_metadata=token_metadata_storage,
                        terms=BACKED_TERMS,
                        roles=sp.record(minter=minter, burner=burner),
                        nonce=sp.big_map(),
                        delegateMode=False,
                        delegateWhitelist=sp.big_map()
                    ),
                    implementation=self.data.implementation
                )
            )
            sp.emit(sp.record(address=newToken, name=name, symbol=symbol), tag="NewToken")

        @sp.entrypoint
        def updateMetadata(self, key, value):
            '''
            An entrypoint to allow the contract metadata to be updated

            Params:
            key (sp.string) - metadata's key for entry that will be changed
            value (sp.bytes) - updated metadata data
            '''
            assert self.isOwner(sp.sender), "BACKED_TOKEN_FACTORY_NotOwner"
            self.data.metadata[key] = value

        @sp.entrypoint
        def updateImplementation(self, implementation):
            '''
            Update the implementation for future deployments. Callable only by the factory owner

            Params:
            implementation (sp.big_map) - New implementation of the actions in form of lambdas that 
                    take storage and return updated one, that can be invoked in newly deployed oracles
            '''
            assert self.isOwner(sp.sender), "BACKED_TOKEN_Factory_NotOwner"

            self.data.implementation = implementation

            
