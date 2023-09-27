import smartpy as sp
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
def TestModule():
    MintParams: type = sp.record(address=sp.address, value=sp.nat)\

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

    @sp.effects()
    def mint(storage, data):
        sp.cast(storage, BackedTokenStorageModule.BackedToken)
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
    @sp.add_test(name="backed_token")
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
            TestModule
        ])
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

        c1 = BackedTokenModule.BackedToken(
            owner=admin.address,
            metadata=contract_metadata,
            token_metadata=token_metadata,
            ledger={},
            implementation=sp.big_map({
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
            }),
            minter=admin.address,
            burner=admin.address,
            pauser=admin.address
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
        c1.updateMetadata(key="", value=sp.bytes("0x00")).run(sender=admin)
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
        view_balance = TestModule.Viewer_nat()
        sc += view_balance
        target = sp.contract(sp.TNat, view_balance.address, "target").open_some()
        c1.getBalance((alice.address, target))
        sc.verify_equal(view_balance.data.last, sp.some(9))

        sc.h2("Administrator")
        view_administrator = TestModule.Viewer_address()
        sc += view_administrator
        target = sp.contract(
            sp.TAddress, view_administrator.address, "target"
        ).open_some()
        c1.getOwner((sp.unit, target))
        sc.verify_equal(view_administrator.data.last, sp.some(admin.address))

        sc.h2("Total Supply")
        view_totalSupply = TestModule.Viewer_nat()
        sc += view_totalSupply
        target = sp.contract(sp.TNat, view_totalSupply.address, "target").open_some()
        c1.getTotalSupply((sp.unit, target))
        sc.verify_equal(view_totalSupply.data.last, sp.some(17))

        sc.h2("Allowance")
        view_allowance = TestModule.Viewer_nat()
        sc += view_allowance
        target = sp.contract(sp.TNat, view_allowance.address, "target").open_some()
        c1.getAllowance((sp.record(owner=alice.address, spender=bob.address), target))
        sc.verify_equal(view_allowance.data.last, sp.some(1))

        sc.h2("Update implementation")
        c1.updateAction(actionName="mint", actionEntry=sp.record(action=TestModule.mint, only_admin=True)).run(sender=admin)

        # Set delegate whitelist
        # TODO: try to delegate without access

        sc.h2("Set delegate whitelist")
        c1.execute(actionName="setDelegateWhitelist", data=sp.pack(sp.record(address=admin.address, status=True))).run(sender=admin)


        # Permit
        sc.h2("Permit")
        nonce = 0
        deadline = sp.timestamp(1571761676)
        permit_message = sp.pack(sp.record(
                    deadline=deadline, spender=bob.address, amount=10, nonce=nonce))

        sig_from_alice = sp.make_signature(
            secret_key=alice.secret_key,
            message=permit_message,
            message_format="Raw",
        )
        c1.execute(actionName="permit", data=sp.pack(sp.record(owner=alice.public_key, spender=bob.address, amount=10, signature=sig_from_alice, deadline=deadline))).run(sender=admin, now=sp.timestamp(1571761674))
        c1.getAllowance((sp.record(owner=alice.address, spender=bob.address), target))
        sc.verify_equal(view_allowance.data.last, sp.some(10))

        sc.h2("Permit - wrong signer")
        nonce = 0
        deadline = sp.timestamp(1571761676)
        permit_message = sp.pack(sp.record(
                    deadline=deadline, spender=alice.address, amount=10, nonce=nonce))

        sig_from_alice = sp.make_signature(
            secret_key=alice.secret_key,
            message=permit_message,
            message_format="Raw",
        )
        c1.execute(actionName="permit", data=sp.pack(sp.record(owner=bob.public_key, spender=alice.address, amount=10, signature=sig_from_alice, deadline=deadline))).run(sender=admin, now=sp.timestamp(1571761674), valid=False)
        c1.getAllowance((sp.record(owner=bob.address, spender=alice.address), target))
        sc.verify_equal(view_allowance.data.last, sp.some(0))

        # TODO: wrong nonce, deadline expired