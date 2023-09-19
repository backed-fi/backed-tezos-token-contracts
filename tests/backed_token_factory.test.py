import smartpy as sp
from contracts.backed_token_factory import backed_token_factory_module
from contracts.backed_token import backed_token_module
from contracts.utils.admin import admin_module 
from contracts.utils.pause import pause_module 

from contracts.actions.mint import mint_module
from contracts.actions.burn import burn_module
from contracts.actions.approve import approve_module
from contracts.actions.transfer import transfer_module

from contracts.shared.storage import storage_module

@sp.module
def test_module():
     class Viewer_nat(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.nat])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)

if "templates" not in __name__:
    @sp.add_test(name="backed_token_factory")
    def test():
        sc = sp.test_scenario([
            admin_module,
            pause_module,
            storage_module,
            mint_module,
            burn_module,
            approve_module,
            transfer_module,
            backed_token_module,
            backed_token_factory_module,
            test_module])
        sc.h1("Backed Token Factory")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Robert")

        implementation = sp.big_map({
            "mint": sp.record(action=mint_module.mint, only_admin=True),
            "burn": sp.record(action=burn_module.burn, only_admin=True),
            "approve": sp.record(action=approve_module.approve, only_admin=False),
            "transfer": sp.record(action=transfer_module.transfer, only_admin=False),
        })

        factory = backed_token_factory_module.BackedFactory(administrator=admin.address, implementation=implementation)

        sc+= factory

        sc.h1("Attempt to deploy token")

        factory.deploy_token(
            tokenOwner=admin.address,
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
        
