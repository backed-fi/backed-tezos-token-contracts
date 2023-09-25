import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
from contracts.backed_oracle_forwarder import BackedOracleForwarderModule
from contracts.backed_oracle_factory import BackedOracleFactoryModule

from contracts.utils.ownable import OwnableModule

from contracts.storage.backed_oracle import BackedOracleStorageModule

from contracts.actions.oracle.update_answer import UpdateAnswerModule

@sp.module
def TestModule():
    class Viewer_nat(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.nat])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)

if "templates" not in __name__:
    @sp.add_test(name="backed_oracle_factory")
    def test():
        sc = sp.test_scenario([
            OwnableModule,
            BackedOracleStorageModule,
            UpdateAnswerModule,
            BackedOracleModule,
            BackedOracleForwarderModule,
            BackedOracleFactoryModule,
            TestModule
        ])
        sc.h1("Backed Oracle Factory")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")

        implementation=sp.big_map({
            "updateAnswer": sp.record(action=UpdateAnswerModule.updateAnswer, only_admin=False)
        })

        factory = BackedOracleFactoryModule.BackedOracleFactory(owner=admin.address, implementation=implementation)

        sc += factory

        sc.h1("Deploy Oracle")
        sc.h2("Sender is not admin")

        factory.deployOracle(owner=admin.address, updater=admin.address, decimals="18", description="Backed Oracle").run(sender=alice, valid=False)

        sc.h2("Sender is admin")

        factory.deployOracle(owner=admin.address, updater=admin.address, decimals="18", description="Backed Oracle").run(sender=admin)



