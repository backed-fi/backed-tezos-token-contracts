import smartpy as sp
from contracts.backed_token_factory import BackedTokenFactoryModule
from contracts.backed_token import BackedTokenModule 
from contracts.utils.ownable import OwnableModule 
from contracts.utils.pausable import PausableModule 

from contracts.actions.mint import MintModule 
from contracts.actions.set_minter import SetMinterModule 
from contracts.actions.burn import BurnModule 
from contracts.actions.set_burner import SetBurnerModule 
from contracts.actions.approve import ApproveModule
from contracts.actions.transfer import TransferModule
from contracts.actions.increase_allowance import IncreaseAllowanceModule
from contracts.actions.decrease_allowance import DecreaseAllowanceModule
from contracts.actions.set_terms import SetTermsModule

from contracts.shared.storage import StorageModule

@sp.module
def TestModule():
    MintParams: type = sp.record(address=sp.address, value=sp.nat)

    class Viewer_nat(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.nat])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)

    @sp.effects()
    def mint(storage, data):
        sp.cast(storage, StorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        mintParams = sp.unpack(data, MintParams).unwrap_some(error="BACKED_TOKEN_Mint_CannotUnpackParams")
        
        updated_storage = storage

        receiver_balance = updated_storage.balances.get(
            mintParams.address, default=sp.record(balance=0, approvals={})
        )
        receiver_balance.balance += mintParams.value * 2
        updated_storage.balances[mintParams.address] = receiver_balance
        updated_storage.total_supply += mintParams.value * 2

        return updated_storage

if "templates" not in __name__:
    @sp.add_test(name="backed_token_factory")
    def test():
        sc = sp.test_scenario([
            OwnableModule,
            PausableModule,
            StorageModule,
            MintModule,
            SetMinterModule,
            BurnModule,
            SetBurnerModule,
            ApproveModule,
            TransferModule,
            SetTermsModule,
            IncreaseAllowanceModule,
            DecreaseAllowanceModule,
            BackedTokenModule,
            BackedTokenFactoryModule,
            TestModule
        ])
        sc.h1("Backed Token Factory")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Robert")

        implementation = sp.big_map({
            "mint": sp.record(action=MintModule.mint, only_admin=True),
            "burn": sp.record(action=BurnModule.burn, only_admin=True),
            "approve": sp.record(action=ApproveModule.approve, only_admin=False),
            "transfer": sp.record(action=TransferModule.transfer, only_admin=False),
            "setMinter": sp.record(action=SetMinterModule.setMinter, only_admin=True),
            "setBurner": sp.record(action=SetBurnerModule.setBurner, only_admin=True),
            "setTerms": sp.record(action=SetTermsModule.setTerms, only_admin=True),
            "increaseAllowance": sp.record(action=IncreaseAllowanceModule.increaseAllowance, only_admin=False),
            "decreaseAllowance": sp.record(action=DecreaseAllowanceModule.decreaseAllowance, only_admin=False),
        })

        factory = BackedTokenFactoryModule.BackedFactory(owner=admin.address, implementation=implementation)

        sc+= factory

        sc.h1("Attempt to deploy token")

        factory.deploy_token(
            tokenOwner=admin.address,
            minter=admin.address,
            burner=admin.address,
            pauser=admin.address,
            # TODO:
            # metadata=sp.utils.metadata_of_url(
            # "ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"
            # ),
            metadata=sp.utils.bytes_of_string(
            "ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"
            ),
            name=sp.utils.bytes_of_string("Backed IB01 $ Treasury Bond 0-1yr"),
            symbol=sp.utils.bytes_of_string("bIB01"),
            icon=sp.utils.bytes_of_string(
                "https://assets.website-files.com/6418671e8e48de1967843312/64e39beb6a4b261e47c6c763_bIB01.svg"
            ),
            decimals=sp.utils.bytes_of_string("18")
        ).run(sender=admin)


        updated_implementation = sp.big_map({
            "mint": sp.record(action=TestModule.mint, only_admin=True),
            "burn": sp.record(action=BurnModule.burn, only_admin=True),
            "approve": sp.record(action=ApproveModule.approve, only_admin=False),
            "transfer": sp.record(action=TransferModule.transfer, only_admin=False),
            "setMinter": sp.record(action=SetMinterModule.setMinter, only_admin=True),
            "setBurner": sp.record(action=SetBurnerModule.setBurner, only_admin=True),
            "setTerms": sp.record(action=SetTermsModule.setTerms, only_admin=True),
            "increaseAllowance": sp.record(action=IncreaseAllowanceModule.increaseAllowance, only_admin=False),
            "decreaseAllowance": sp.record(action=DecreaseAllowanceModule.decreaseAllowance, only_admin=False),
        })

        factory.updateImplementation(updated_implementation).run(sender=admin)
        
