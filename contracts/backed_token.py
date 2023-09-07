# Fungible Assets - FA12
# Inspired by https://gitlab.com/tzip/tzip/blob/master/A/FA1.2.md

import smartpy as sp

# The metadata below is just an example, it serves as a base,
# the contents are used to build the metadata JSON that users
# can copy and upload to IPFS.
TZIP16_Metadata_Base = {
    "name": "SmartPy FA1.2 Token Template",
    "description": "Example Template for an FA1.2 Contract from SmartPy",
    "authors": ["SmartPy Dev Team <email@domain.com>"],
    "homepage": "https://smartpy.io",
    "interfaces": ["TZIP-007-2021-04-17", "TZIP-016-2021-04-17"],
}


@sp.module
def m():
    class AdminInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def is_administrator_(self, sender):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""
            return True

    class CommonInterface(AdminInterface):
        def __init__(self):
            AdminInterface.__init__(self)
            self.data.balances = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.address,
                    sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat),
                ],
            )
            self.data.total_supply = 0
            self.data.token_metadata = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.nat,
                    sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes]),
                ],
            )
            self.data.metadata = sp.cast(
                sp.big_map(),
                sp.big_map[sp.string, sp.bytes],
            )
            self.data.balances = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.address,
                    sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat),
                ],
            )
            self.data.total_supply = 0
            self.data.token_metadata = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.nat,
                    sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes]),
                ],
            )
            self.data.metadata = sp.cast(
                sp.big_map(),
                sp.big_map[sp.string, sp.bytes],
            )

        @sp.private(with_storage="read-only")
        def is_paused_(self):
            """Not standard, may be re-defined through inheritance."""
            return False

    class Fa1_2(CommonInterface):
        def __init__(self, metadata, ledger, token_metadata):
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
            CommonInterface.__init__(self)
            self.data.metadata = metadata
            self.data.token_metadata = sp.big_map(
                {0: sp.record(token_id=0, token_info=token_metadata)}
            )

            for owner in ledger.items():
                self.data.balances[owner.key] = owner.value
                self.data.total_supply += owner.value.balance

            # TODO: Activate when this feature is implemented.
            # self.init_metadata("metadata", metadata)

        @sp.entrypoint
        def transfer(self, param):
            sp.cast(
                param,
                sp.record(from_=sp.address, to_=sp.address, value=sp.nat).layout(
                    ("from_ as from", ("to_ as to", "value"))
                ),
            )
            balance_from = self.data.balances.get(
                param.from_, default=sp.record(balance=0, approvals={})
            )
            balance_to = self.data.balances.get(
                param.to_, default=sp.record(balance=0, approvals={})
            )
            balance_from.balance = sp.as_nat(
                balance_from.balance - param.value, error="FA1.2_InsufficientBalance"
            )
            balance_to.balance += param.value
            if not self.is_administrator_(sp.sender):
                assert not self.is_paused_(), "FA1.2_Paused"
                if param.from_ != sp.sender:
                    balance_from.approvals[sp.sender] = sp.as_nat(
                        balance_from.approvals[sp.sender] - param.value,
                        error="FA1.2_NotAllowed",
                    )
            self.data.balances[param.from_] = balance_from
            self.data.balances[param.to_] = balance_to

        @sp.entrypoint
        def approve(self, param):
            sp.cast(
                param,
                sp.record(spender=sp.address, value=sp.nat).layout(
                    ("spender", "value")
                ),
            )
            assert not self.is_paused_(), "FA1.2_Paused"
            spender_balance = self.data.balances.get(
                sp.sender, default=sp.record(balance=0, approvals={})
            )
            alreadyApproved = spender_balance.approvals.get(param.spender, default=0)
            assert (
                alreadyApproved == 0 or param.value == 0
            ), "FA1.2_UnsafeAllowanceChange"
            spender_balance.approvals[param.spender] = param.value
            self.data.balances[sp.sender] = spender_balance

        @sp.entrypoint
        def getBalance(self, param):
            (address, callback) = param
            result = self.data.balances.get(
                address, default=sp.record(balance=0, approvals={})
            ).balance
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getAllowance(self, param):
            (args, callback) = param
            result = self.data.balances.get(
                args.owner, default=sp.record(balance=0, approvals={})
            ).approvals.get(args.spender, default=0)
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getTotalSupply(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.nat]])
            sp.transfer(self.data.total_supply, sp.tez(0), sp.snd(param))

        @sp.offchain_view()
        def token_metadata(self, token_id):
            """Return the token-metadata URI for the given token. (token_id must be 0)."""
            sp.cast(token_id, sp.nat)
            return self.data.token_metadata[token_id]

    ##########
    # Mixins #
    ##########

    class Admin(sp.Contract):
        def __init__(self, administrator):
            self.data.administrator = administrator

        @sp.private(with_storage="read-only")
        def is_administrator_(self, sender):
            return sender == self.data.administrator

        @sp.entrypoint
        def setAdministrator(self, params):
            sp.cast(params, sp.address)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.administrator = params

        @sp.entrypoint()
        def getAdministrator(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.address]])
            sp.transfer(self.data.administrator, sp.tez(0), sp.snd(param))

        @sp.onchain_view()
        def get_administrator(self):
            return self.data.administrator

    class Pause(AdminInterface):
        def __init__(self):
            AdminInterface.__init__(self)
            self.data.paused = False

        @sp.private(with_storage="read-only")
        def is_paused_(self):
            return self.data.paused

        @sp.entrypoint
        def setPause(self, param):
            sp.cast(param, sp.bool)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.paused = param

    class Mint(CommonInterface):
        def __init__(self):
            CommonInterface.__init__(self)

        @sp.entrypoint
        def mint(self, param):
            sp.cast(param, sp.record(address=sp.address, value=sp.nat))
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            receiver_balance = self.data.balances.get(
                param.address, default=sp.record(balance=0, approvals={})
            )
            receiver_balance.balance += param.value
            self.data.balances[param.address] = receiver_balance
            self.data.total_supply += param.value

    class Burn(CommonInterface):
        def __init__(self):
            CommonInterface.__init__(self)

        @sp.entrypoint
        def burn(self, param):
            sp.cast(param, sp.record(address=sp.address, value=sp.nat))
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            receiver_balance = self.data.balances.get(
                param.address, default=sp.record(balance=0, approvals={})
            )
            receiver_balance.balance = sp.as_nat(
                receiver_balance.balance - param.value,
                error="FA1.2_InsufficientBalance",
            )
            self.data.balances[param.address] = receiver_balance
            self.data.total_supply = sp.as_nat(self.data.total_supply - param.value)

    class ChangeMetadata(CommonInterface):
        def __init__(self):
            CommonInterface.__init__(self)

        @sp.entrypoint
        def update_metadata(self, key, value):
            """An entrypoint to allow the contract metadata to be updated."""
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.metadata[key] = value

    ##########
    # Tests #
    ##########

    class Fa1_2TestFull(Admin, Pause, Fa1_2, Mint, Burn, ChangeMetadata):
        def __init__(self, administrator, metadata, ledger, token_metadata):
            ChangeMetadata.__init__(self)
            Burn.__init__(self)
            Mint.__init__(self)
            Fa1_2.__init__(self, metadata, ledger, token_metadata)
            Pause.__init__(self)
            Admin.__init__(self, administrator)
    
    #################################
    # TODO: Backed_Token_Factory.py #
    #################################
    class Factory(sp.Contract):
        def __init__(self):
            self.data.c1 = None

        @sp.entrypoint
        def deploy_token(self, administrator, metadata, name, symbol, icon, decimals):
            # TODO: string input, convert to bytes
            token_metadata = {
                "decimals": decimals,  # Mandatory by the spec
                "name": name,  # Recommended
                "symbol": symbol,  # Recommended
                # Extra fields
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

            self.data.c1 = sp.Some(
                sp.create_contract(Fa1_2Full, None, sp.mutez(0), sp.record(administrator=administrator, paused = False, balances = balances, metadata = metadata_storage, total_supply = 0, token_metadata = token_metadata_storage))
            )

    ##########
    # Tests #
    ##########

   

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
        sc = sp.test_scenario(m)
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
        contract_metadata = sp.utils.metadata_of_url(
            "ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"
        )

        c1 = m.Fa1_2TestFull(
            administrator=admin.address,
            metadata=contract_metadata,
            token_metadata=token_metadata,
            ledger={},
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
            c1.data.metadata[""]
            == sp.utils.bytes_of_string(
                "ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"
            )
        )
        c1.update_metadata(key="", value=sp.bytes("0x00")).run(sender=admin)
        sc.verify(c1.data.metadata[""] == sp.bytes("0x00"))

        sc.h1("Entrypoints")
        sc.h2("Admin mints a few coins")
        c1.mint(address=alice.address, value=12).run(sender=admin)
        c1.mint(address=alice.address, value=3).run(sender=admin)
        c1.mint(address=alice.address, value=3).run(sender=admin)
        sc.h2("Alice transfers to Bob")
        c1.transfer(from_=alice.address, to_=bob.address, value=4).run(sender=alice)
        sc.verify(c1.data.balances[alice.address].balance == 14)
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
        c1.burn(address=bob.address, value=1).run(sender=admin)
        sc.verify(c1.data.balances[alice.address].balance == 10)
        sc.h2("Alice tries to burn Bob token")
        c1.burn(address=bob.address, value=1).run(sender=alice, valid=False)
        sc.h2("Admin pauses the contract and Alice cannot transfer anymore")
        c1.setPause(True).run(sender=admin)
        c1.transfer(from_=alice.address, to_=bob.address, value=4).run(
            sender=alice, valid=False
        )
        sc.verify(c1.data.balances[alice.address].balance == 10)
        sc.h2("Admin transfers while on pause")
        c1.transfer(from_=alice.address, to_=bob.address, value=1).run(sender=admin)
        sc.h2("Admin unpauses the contract and transfers are allowed")
        c1.setPause(False).run(sender=admin)
        sc.verify(c1.data.balances[alice.address].balance == 9)
        c1.transfer(from_=alice.address, to_=bob.address, value=1).run(sender=alice)

        sc.verify(c1.data.total_supply == 17)
        sc.verify(c1.data.balances[alice.address].balance == 8)
        sc.verify(c1.data.balances[bob.address].balance == 9)

        sc.h1("Views")
        sc.h2("Balance")
        view_balance = m.Viewer_nat()
        sc += view_balance
        target = sp.contract(sp.TNat, view_balance.address, "target").open_some()
        c1.getBalance((alice.address, target))
        sc.verify_equal(view_balance.data.last, sp.some(8))

        sc.h2("Administrator")
        view_administrator = m.Viewer_address()
        sc += view_administrator
        target = sp.contract(
            sp.TAddress, view_administrator.address, "target"
        ).open_some()
        c1.getAdministrator((sp.unit, target))
        sc.verify_equal(view_administrator.data.last, sp.some(admin.address))

        sc.h2("Total Supply")
        view_totalSupply = m.Viewer_nat()
        sc += view_totalSupply
        target = sp.contract(sp.TNat, view_totalSupply.address, "target").open_some()
        c1.getTotalSupply((sp.unit, target))
        sc.verify_equal(view_totalSupply.data.last, sp.some(17))

        sc.h2("Allowance")
        view_allowance = m.Viewer_nat()
        sc += view_allowance
        target = sp.contract(sp.TNat, view_allowance.address, "target").open_some()
        c1.getAllowance((sp.record(owner=alice.address, spender=bob.address), target))
        sc.verify_equal(view_allowance.data.last, sp.some(1))
