import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
from contracts.backed_oracle_forwarder import BackedOracleForwarderModule
from contracts.backed_oracle_factory import BackedOracleFactoryModule
from contracts.utils.ownable import OwnableModule

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
            BackedOracleModule,
            BackedOracleForwarderModule,
            BackedOracleFactoryModule,
            TestModule
        ])
        sc.h1("Backed Oracle Factory")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Robert")

        factory = BackedOracleFactoryModule.BackedOracleFactory(owner=admin.address, implementation=1)

        sc += factory



