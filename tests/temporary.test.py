import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
from contracts.storage.backed_oracle import BackedOracleStorageModule
from contracts.utils.ownable import OwnableModule
from contracts.utils.timelock_controller import TimelockControllerModule

from contracts.actions.oracle.update_answer import UpdateAnswerModule

@sp.module
def TestModule():
    @sp.effects(with_operations=True)
    def update_answer(target, data):
        sp.cast(data, sp.bytes)

        dest = sp.contract(sp.record(actionName=sp.string, data=sp.bytes), target, entrypoint="updateAnswer")
        sp.transfer(sp.record(actionName="updateAnswer", data=data), sp.tez(0), dest.unwrap_some())

        return True

    class Viewer_nat(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.nat])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)

        

if "templates" not in __name__:
    @sp.add_test(name="backed_oracle")
    def test():
        sc = sp.test_scenario([
            OwnableModule,
            TimelockControllerModule,
            BackedOracleStorageModule,
            UpdateAnswerModule,
            BackedOracleModule,
            TestModule
        ])
        sc.h1("Backed Oracle")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")

        decimals = "18"
        description = "Backed Oracle contract"
        error = "No data present"

        proposers = sp.set([admin.address])
        executors = sp.set([admin.address])

        timelockController = TimelockControllerModule.TimelockController(
            proposers = proposers,
            executors = executors
        )

        sc += timelockController

        oracle = BackedOracleModule.BackedOracle(
            owner=admin.address,
            implementation=sp.big_map({
                "updateAnswer": sp.record(action=UpdateAnswerModule.updateAnswer, only_admin=False)
            }),
            updater=timelockController.address,
            decimals=decimals,
            description=description
        )

        sc += oracle

        sc.h1("Update answer")
        time_in_secs = 10000
        time = sp.timestamp(time_in_secs)

        valid_timestamp = sp.timestamp(10000 - 100)
        valid_answer = sp.int(10)
        first_round_answer = valid_answer
        first_round_timestamp = valid_timestamp

        data = sp.pack(sp.record(newAnswer=valid_answer, newTimestamp=valid_timestamp))

        oracle.execute(actionName="updateAnswer", data=data).run(sender=admin, now=time, valid=False)

        timelockController.schedule(TestModule.update_answer, data, 1000).run(sender=alice, valid=False)

        sc.verify(sc.compute(oracle.latestAnswer(), source=alice) == valid_answer)



