import smartpy as sp

@sp.module
def NonceModule():
    class UpgradableInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def execute(self, owner):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""
            return 0
        @sp.private(with_storage="read-write")
        def useNonce(self, owner):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""

    class Upgradable(sp.Contract):
        def __init__(self, implementation, type):
            sp.cast(implementation, 
                    sp.big_map[
                        sp.string,
                        sp.record(
                            action=sp.lambda_[
                                sp.record(storage=BackedTokenStorageModule.BackedToken, data=sp.bytes),
                                BackedTokenStorageModule.BackedToken
                            ],
                            only_admin=sp.bool
            )])

            self.data.implementation = implementation

        ## TODO:
        #
        @sp.private(with_storage='read-write')
        def invoke(self, params):
            sp.cast(params, sp.record(actionName=sp.string, data=sp.bytes))

            updated_storage = self.data.implementation[params.actionName].action(sp.record(storage=self.data.storage, data=params.data))

            self.data.storage = updated_storage

        # TODO:
        #
        @sp.entrypoint
        def execute(self, actionName, data):
            assert not self.isPaused(), "BACKED_TOKEN_Paused"

            actionEntry = self.data.implementation.get(actionName, error="BACKED_TOKEN_UnknownAction")

            if actionEntry.only_admin:
                assert self.isOwner(sp.sender), "BACKED_TOKEN_NotAdmin"

            self.invoke(sp.record(actionName=actionName, data=data))
        