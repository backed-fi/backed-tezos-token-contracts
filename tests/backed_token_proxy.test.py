import smartpy as sp
from contracts.backed_token_proxy import backed_token_proxy_module
from contracts.backed_token import backed_token_module 
from contracts.utils.admin import admin_module 
from contracts.utils.pause import pause_module 

@sp.module
def test_module():
     class Viewer_nat(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.nat])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)

if "templates" not in __name__:
    @sp.add_test(name="backed_proxy")
    def test():
        sc = sp.test_scenario([admin_module, pause_module, backed_token_module, backed_token_proxy_module, test_module])
        sc.h1("Backed Token Implementation")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Robert")

        # Let's display the accounts:
        sc.h1("Accounts")
        sc.show([admin, alice, bob])

        sc.h1("Contract")
        token_metadata = {
            "decimals": sp.utils.bytes_of_string("18"),  # Mandatory by the spec
            "name": sp.utils.bytes_of_string("Backed IB01 $ Treasury Bond 0-1yr"),  # Recommended
            "symbol": sp.utils.bytes_of_string("bIB01"),  # Recommended
            # Extra fields
            "icon": sp.utils.bytes_of_string(
                "https://assets.website-files.com/6418671e8e48de1967843312/64e39beb6a4b261e47c6c763_bIB01.svg"
            ),
        }
        token_metadata2 = sp.big_map(
                {0: sp.record(token_id=0, token_info=token_metadata)}
            )
        contract_metadata = sp.utils.metadata_of_url(
            "ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"
        )

        c1 = backed_token_module.BackedToken(
            administrator=admin.address,
            metadata=contract_metadata,
            token_metadata=token_metadata,
            ledger={},
        )
        sc += c1

        proxy = backed_token_proxy_module.BackedTokenProxy(backed_token = c1.address)

        sc += proxy

        sc.h1("Entrypoints")
        sc.h1("Entrypoints")
        sc.h2("Admin mints a few coins")
        proxy.mint(address=alice.address, value=12).run(sender=admin)
        proxy.mint(address=alice.address, value=3).run(sender=admin)
        proxy.mint(address=alice.address, value=3).run(sender=admin)
        sc.h2("Alice transfers to Bob")
        proxy.transfer(from_=alice.address, to_=bob.address, value=4).run(sender=alice)
        sc.verify(c1.data.balances[alice.address].balance == 14)
        sc.h2("Bob tries to transfer from Alice but he doesn't have her approval")
        proxy.transfer(from_=alice.address, to_=bob.address, value=4).run(
            sender=bob, valid=False
        )


