# Fungible Assets - FA12
# Inspired by https://gitlab.com/tzip/tzip/blob/master/A/FA1.2.md

import smartpy as sp
from contracts.utils.admin import admin_module
from contracts.utils.pause import pause_module

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
def backed_token_module():
    class CommonInterface(admin_module.AdminInterface):
        def __init__(self):
            admin_module.AdminInterface.__init__(self)
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

    class Mint(CommonInterface):
        def __init__(self):
            CommonInterface.__init__(self)

        @sp.entrypoint
        def mint(self, param):
            sp.cast(param, sp.record(address=sp.address, value=sp.nat))
            # assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
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

    class BackedToken(admin_module.Admin, pause_module.Pause, Fa1_2, Mint, Burn, ChangeMetadata):
        def __init__(self, administrator, metadata, ledger, token_metadata):
            ChangeMetadata.__init__(self)
            Burn.__init__(self)
            Mint.__init__(self)
            Fa1_2.__init__(self, metadata, ledger, token_metadata)
            pause_module.Pause.__init__(self)
            admin_module.Admin.__init__(self, administrator)
  