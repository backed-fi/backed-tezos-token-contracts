import smartpy as sp
from contracts.backed_token_factory import BackedTokenFactoryModule
from contracts.backed_token import BackedTokenModule 
from contracts.utils.ownable import OwnableModule 
from contracts.utils.pausable import PausableModule
from contracts.utils.nonce import NonceModule

from contracts.actions.token.mint import MintModule 
from contracts.actions.token.set_minter import SetMinterModule 
from contracts.actions.token.burn import BurnModule 
from contracts.actions.token.set_burner import SetBurnerModule 
from contracts.actions.token.approve import ApproveModule
from contracts.actions.token.transfer import TransferModule
from contracts.actions.token.delegated_transfer import DelegatedTransferModule
from contracts.actions.token.permit import PermitModule
from contracts.actions.token.increase_allowance import IncreaseAllowanceModule
from contracts.actions.token.decrease_allowance import DecreaseAllowanceModule
from contracts.actions.token.set_terms import SetTermsModule
from contracts.actions.token.set_delegate_mode import SetDelegateModeModule
from contracts.actions.token.set_delegate_whitelist import SetDelegateWhitelistModule

from contracts.storage.backed_token import BackedTokenStorageModule

@sp.module
def OriginationsModule():
    class Origination(sp.Contract):
        def __init__(self):
            self.data.x = None

if "templates" not in __name__:
    @sp.add_test(name="backed_token_factory")
    def test():
        sc = sp.test_scenario([
            OwnableModule,
            PausableModule,
            NonceModule,
            BackedTokenStorageModule,
            MintModule,
            SetMinterModule,
            BurnModule,
            SetBurnerModule,
            ApproveModule,
            TransferModule,
            DelegatedTransferModule,
            PermitModule,
            SetTermsModule,
            IncreaseAllowanceModule,
            DecreaseAllowanceModule,
            SetDelegateModeModule,
            SetDelegateWhitelistModule,
            BackedTokenModule,
            BackedTokenFactoryModule,
            OriginationsModule
        ])
       
        implementation = sp.big_map({
            "mint": sp.record(action=MintModule.mint, only_admin=False),
            "burn": sp.record(action=BurnModule.burn, only_admin=False),
            "approve": sp.record(action=ApproveModule.approve, only_admin=False),
            "transfer": sp.record(action=TransferModule.transfer, only_admin=False),
            # "delegatedTransfer": sp.record(action=DelegatedTransferModule.delegatedTransfer, only_admin=False),
            # "permit": sp.record(action=PermitModule.permit, only_admin=False),
            "setMinter": sp.record(action=SetMinterModule.setMinter, only_admin=True),
            "setBurner": sp.record(action=SetBurnerModule.setBurner, only_admin=True),
            "setTerms": sp.record(action=SetTermsModule.setTerms, only_admin=True),
            "increaseAllowance": sp.record(action=IncreaseAllowanceModule.increaseAllowance, only_admin=False),
            "decreaseAllowance": sp.record(action=DecreaseAllowanceModule.decreaseAllowance, only_admin=False),
            # "setDelegateMode": sp.record(action=SetDelegateModeModule.setDelegateMode, only_admin=True),
            # "setDelegateWhitelist": sp.record(action=SetDelegateWhitelistModule.setDelegateWhitelist, only_admin=True),
        })

        factory = BackedTokenFactoryModule.BackedFactory(owner=sp.address("tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd"), implementation=implementation)

        sc += factory
        
