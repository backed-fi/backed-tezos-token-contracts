import smartpy as sp
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

    class Viewer_address(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.address])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)


if "templates" not in __name__:
    @sp.add_test(name="backed_token")
    def test():
        sc = sp.test_scenario([admin_module, pause_module, storage_module, mint_module, burn_module, approve_module, transfer_module, backed_token_module, test_module])
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
            registry=sp.big_map({
                "mint": sp.record(action=mint_module.mint, only_admin=True),
                "burn": sp.record(action=burn_module.burn, only_admin=True),
                "approve": sp.record(action=approve_module.approve, only_admin=False),
                "transfer": sp.record(action=transfer_module.transfer, only_admin=False),
            })

        )
        sc += c1

        sc.h1("Offchain view - token_metadata")
        sc.verify_equal(
            sp.View(c1, "token_metadata")(0),
            sp.record(
                token_id=0,
                token_info=sp.map(
                    {
                        "decimals": sp.utils.bytes_of_string("18"),  # Mandatory by the spec
                        "name": sp.utils.bytes_of_string("Backed IB01 $ Treasury Bond 0-1yr"),  # Recommended
                        "symbol": sp.utils.bytes_of_string("bIB01"),  # Recommended
                        # Extra fields
                        "icon": sp.utils.bytes_of_string(
                            "https://assets.website-files.com/6418671e8e48de1967843312/64e39beb6a4b261e47c6c763_bIB01.svg"
                        ),
                    }
                ),
            ),
        )

        sc.h1("Attempt to update metadata")
        sc.verify(
            c1.data.storage.metadata[""]
            == sp.utils.bytes_of_string(
                "ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"
            )
        )
        c1.update_metadata(key="", value=sp.bytes("0x00")).run(sender=admin)
        sc.verify(c1.data.storage.metadata[""] == sp.bytes("0x00"))

        sc.h1("Entrypoints")
        sc.h2("Admin mints a few coins")
        c1.execute(actionName="mint", data=sp.pack(sp.record(address=alice.address, value=12))).run(sender=admin)
        c1.execute(actionName="mint", data=sp.pack(sp.record(address=alice.address, value=3))).run(sender=admin)
        c1.execute(actionName="mint", data=sp.pack(sp.record(address=alice.address, value=3))).run(sender=admin)

        sc.h2("Alice transfers to Bob")
        c1.transfer(from_=alice.address, to_=bob.address, value=4).run(sender=alice)
        sc.verify(c1.data.storage.balances[alice.address].balance == 14)
        sc.h2("Bob tries to transfer from Alice but he doesn't have her approval")
        c1.transfer(from_=alice.address, to_=bob.address, value=4).run(
            sender=bob, valid=False
        )
        sc.h2("Alice approves Bob and Bob transfers")
        c1.approve(spender=bob.address, value=5).run(sender=alice)
        c1.transfer(from_=alice.address, to_=bob.address, value=4).run(sender=bob)
        sc.h2("Bob tries to over-transfer from Alice")
        c1.transfer(from_=alice.address, to_=bob.address, value=4).run(
            sender=bob, valid=False
        )
        sc.h2("Admin burns Bob token")
        c1.execute(actionName="burn", data=sp.pack(sp.record(address=bob.address, value=1))).run(sender=admin)
        sc.verify(c1.data.storage.balances[alice.address].balance == 10)
        sc.h2("Alice tries to burn Bob token")
        c1.execute(actionName="burn", data=sp.pack(sp.record(address=bob.address, value=1))).run(sender=alice, valid=False)
        sc.h2("Admin pauses the contract and Alice cannot transfer anymore")
        c1.setPause(True).run(sender=admin)
        c1.transfer(from_=alice.address, to_=bob.address, value=4).run(
            sender=alice, valid=False
        )
        sc.verify(c1.data.storage.balances[alice.address].balance == 10)
        sc.h2("Admin unpauses the contract and transfers are allowed")
        c1.setPause(False).run(sender=admin)
        sc.verify(c1.data.storage.balances[alice.address].balance == 10)
        c1.transfer(from_=alice.address, to_=bob.address, value=1).run(sender=alice)

        sc.verify(c1.data.storage.total_supply == 17)
        sc.verify(c1.data.storage.balances[alice.address].balance == 9)
        sc.verify(c1.data.storage.balances[bob.address].balance == 8)

        sc.h1("Views")
        sc.h2("Balance")
        view_balance = test_module.Viewer_nat()
        sc += view_balance
        target = sp.contract(sp.TNat, view_balance.address, "target").open_some()
        c1.getBalance((alice.address, target))
        sc.verify_equal(view_balance.data.last, sp.some(9))

        sc.h2("Administrator")
        view_administrator = test_module.Viewer_address()
        sc += view_administrator
        target = sp.contract(
            sp.TAddress, view_administrator.address, "target"
        ).open_some()
        c1.getAdministrator((sp.unit, target))
        sc.verify_equal(view_administrator.data.last, sp.some(admin.address))

        sc.h2("Total Supply")
        view_totalSupply = test_module.Viewer_nat()
        sc += view_totalSupply
        target = sp.contract(sp.TNat, view_totalSupply.address, "target").open_some()
        c1.getTotalSupply((sp.unit, target))
        sc.verify_equal(view_totalSupply.data.last, sp.some(17))

        sc.h2("Allowance")
        view_allowance = test_module.Viewer_nat()
        sc += view_allowance
        target = sp.contract(sp.TNat, view_allowance.address, "target").open_some()
        c1.getAllowance((sp.record(owner=alice.address, spender=bob.address), target))
        sc.verify_equal(view_allowance.data.last, sp.some(1))
