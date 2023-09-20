import smartpy as sp

from contracts.backed_token import BackedTokenModule

from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule

from contracts.actions.mint import MintModule
from contracts.actions.burn import BurnModule
from contracts.actions.approve import ApproveModule 
from contracts.actions.transfer import TransferModule 

@sp.module
def BackedTokenFactoryModule():
    # @dev
    #
    # Factory contract, used for creating new, upgradable tokens.
    # 
    # The contract contains one role:
    #  - An administrator, which can deploy new tokens
    #
    class BackedFactory(OwnableModule.Ownable):
        #
        # @param administrator The address of the account that will be set as owner of the contract
        #
        def __init__(self, implementation, administrator):
            OwnableModule.Ownable.__init__(self, administrator)
            self.data.implementation = implementation
        
        #
        # @dev Deploy and configures new instance of BackedFi Token. Callable only by the factory owner
        # Emits a { NewToken } event
        # 
        # @param name          The name that the newly created token will have
        # @param symbol        The symbol that the newly created token will have
        # @param icon          The icon that the newly created token will have
        # @param decimals      The number of decimals that the newly created token will have
        # @param tokenOwner    The address of the account to which the owner role will be assigned
        #
        @sp.entrypoint
        def deploy_token(self, tokenOwner, minter, burner, pauser, metadata, name, symbol, icon, decimals):
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
                        roles=sp.record(minter=minter, burner=burner)
                    ),
                    registry=self.data.implementation
                )
            )
            # sp.emit(sp.record(address=address, name=name, symbol=symbol), tag="NewToken")

        @sp.entrypoint
        def updateImplementation(self, implementation):
            assert self.isOwner(sp.sender), "BACKED_TOKEN_Factory_NotOwner"

            self.data.implementation = implementation

            
