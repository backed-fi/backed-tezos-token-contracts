import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
from contracts.backed_oracle_forwarder import BackedOracleForwarderModule
from contracts.backed_oracle_factory import BackedOracleFactoryModule

from contracts.utils.ownable import OwnableModule

from contracts.storage.backed_oracle import BackedOracleStorageModule

from contracts.actions.oracle.update_answer import UpdateAnswerModule

@sp.module
def OriginationsModule():
    class Origination(sp.Contract):
        def __init__(self):
            self.data.x = None

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
            OriginationsModule
        ])

        implementation=sp.big_map({
            "updateAnswer": sp.record(action=UpdateAnswerModule.updateAnswer, only_admin=False)
        })

        factory = BackedOracleFactoryModule.BackedOracleFactory(owner=sp.address("tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd"), implementation=implementation)

        sc += factory
