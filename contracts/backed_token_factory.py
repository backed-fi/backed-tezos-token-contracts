import smartpy as sp

from contracts.backed_token import BackedTokenModule

from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule

@sp.module
def BackedTokenFactoryModule():
    BACKED_TERMS = "https://www.backedassets.fi/legal-documentation"
    ##
    # @dev
    #
    # Factory contract, used for creating new, upgradable tokens.
    # 
    # The contract contains one role:
    #  - An owner, which can deploy new tokens
    #
    class BackedFactory(OwnableModule.Ownable):
        ##
        # @param owner - sp.address      The address of the account that will be set as owner of the contract
        # @param implementation - sp.big_map    Implementation of the actions in form of lambdas that take storage and return updated one, that can be invoked in newly deployed token
        #
        def __init__(self, implementation, owner):
            OwnableModule.Ownable.__init__(self, owner)
            self.data.implementation = implementation
        
        ##
        # @dev Deploy and configures new instance of BackedFi Token. Callable only by the factory owner
        # 
        # @param name - sp.bytes          The name that the newly created token will have
        # @param symbol - sp.bytes       The symbol that the newly created token will have
        # @param icon - sp.bytes          The icon that the newly created token will have
        # @param decimals -sp.bytes      The number of decimals that the newly created token will have
        # @param tokenOwner - sp.address    The address of the account to which the owner role will be assigned
        #
        # Emits a { NewToken } event
        @sp.entrypoint
        def deployToken(self, tokenOwner, minter, burner, pauser, metadata, name, symbol, icon, decimals):
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
                    storage=sp.record(
                        balances=balances,
                        metadata=metadata_storage,
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

        ##
        # @dev Update the implementation for future deployments. Callable only by the factory owner
        # 
        # @param implementation - sp.big_map    New implementation of the actions in form of lambdas that take storage and return updated one, that can be invoked in newly deployed token
        @sp.entrypoint
        def updateImplementation(self, implementation):
            assert self.isOwner(sp.sender), "BACKED_TOKEN_Factory_NotOwner"

            self.data.implementation = implementation

            
