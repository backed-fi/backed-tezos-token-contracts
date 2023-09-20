# Fungible Assets - FA12
# Inspired by https://gitlab.com/tzip/tzip/blob/master/A/FA1.2.md

import smartpy as sp
from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule
from contracts.shared.storage import StorageModule

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
def BackedTokenModule():
    class CommonInterface(OwnableModule.OwnableInterface, PausableModule.PausableInterface):
        def __init__(self, minter, burner):
            OwnableModule.OwnableInterface.__init__(self)
            PausableModule.PausableInterface.__init__(self)
            sp.cast(self.data.storage, StorageModule.BackedToken)
            self.data.storage.balances = sp.big_map()
            self.data.storage.total_supply = 0
            self.data.storage.token_metadata = sp.big_map()
            self.data.storage.metadata = sp.big_map()
            self.data.storage.roles = sp.record(minter=minter, burner=burner)
           
    class Fa1_2(CommonInterface):
        def __init__(self, metadata, ledger, token_metadata, registry, minter, burner):
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
            CommonInterface.__init__(self, minter, burner)
            sp.cast(registry, sp.big_map[sp.string, sp.record(action=sp.lambda_[sp.record(storage=StorageModule.BackedToken, data=sp.bytes), StorageModule.BackedToken], only_admin=sp.bool)])

            self.data.registry = registry
            self.data.storage.metadata = metadata
            self.data.storage.token_metadata = sp.big_map(
                {0: sp.record(token_id=0, token_info=token_metadata)}
            )

            for owner in ledger.items():
                self.data.storage.balances[owner.key] = owner.value
                self.data.storage.total_supply += owner.value.balance

            # TODO: Activate when this feature is implemented.
            # self.init_metadata("metadata", metadata)


        @sp.private(with_storage='read-write')
        def invoke(self, params):
            sp.cast(params, sp.record(actionName=sp.string, data=sp.bytes))

            updated_storage = self.data.registry[params.actionName].action(sp.record(storage=self.data.storage, data=params.data))

            self.data.storage = updated_storage

        @sp.entrypoint
        def execute(self, actionName, data):
            assert not self.isPaused(), "BACKED_TOKEN_Paused"

            actionEntry = self.data.registry.get(actionName, error="BACKED_TOKEN_UnknownAction")

            if actionEntry.only_admin:
                assert self.isOwner(sp.sender), "BACKED_TOKEN_NotAdmin"

            self.invoke(sp.record(actionName=actionName, data=data))
  

        @sp.entrypoint
        def transfer(self, param):
            assert not self.isPaused(), "BACKED_TOKEN_Paused"

            sp.cast(
                param,
                sp.record(from_=sp.address, to_=sp.address, value=sp.nat).layout(
                    ("from_ as from", ("to_ as to", "value"))
                ),
            )
            data = sp.pack(param)

            self.invoke(sp.record(actionName='transfer', data=data))


        @sp.entrypoint
        def approve(self, param):
            assert not self.isPaused(), "BACKED_TOKEN_Paused"

            sp.cast(
                param,
                sp.record(spender=sp.address, value=sp.nat).layout(
                    ("spender", "value")
                ),
            )
            data = sp.pack(param)
            self.invoke(sp.record(actionName='approve', data=data))

        @sp.entrypoint
        def getBalance(self, param):
            (address, callback) = param
            result = self.data.storage.balances.get(
                address, default=sp.record(balance=0, approvals={})
            ).balance
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getAllowance(self, param):
            (args, callback) = param
            result = self.data.storage.balances.get(
                args.owner, default=sp.record(balance=0, approvals={})
            ).approvals.get(args.spender, default=0)
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getTotalSupply(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.nat]])
            sp.transfer(self.data.storage.total_supply, sp.tez(0), sp.snd(param))

        @sp.offchain_view()
        def token_metadata(self, token_id):
            """Return the token-metadata URI for the given token. (token_id must be 0)."""
            sp.cast(token_id, sp.nat)
            return self.data.storage.token_metadata[token_id]
    ##########
    # Mixins #
    ##########

    class BackedToken(OwnableModule.Ownable, PausableModule.Pausable, Fa1_2):
        def __init__(self, owner, metadata, ledger, token_metadata, registry, minter, burner, pauser):
            OwnableModule.Ownable.__init__(self, owner)
            PausableModule.Pausable.__init__(self, pauser)
            Fa1_2.__init__(self, metadata, ledger, token_metadata, registry, minter, burner)

        @sp.entrypoint
        def updateMetadata(self, key, value):
            """An entrypoint to allow the contract metadata to be updated."""
            assert self.isOwner(sp.sender), "BACKED_TOKEN_NotOwner"
            self.data.storage.metadata[key] = value

        @sp.entrypoint
        def updateAction(self, actionName, actionEntry):
            assert self.isOwner(sp.sender), "BACKED_TOKEN_NotOwner"
            
            self.data.registry[actionName] = actionEntry

  
