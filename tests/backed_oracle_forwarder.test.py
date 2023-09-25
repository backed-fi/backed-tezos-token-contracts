import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
from contracts.backed_oracle_forwarder import BackedOracleForwarderModule
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
    @sp.add_test(name="backed_oracle_forwarder")
    def test():
        sc = sp.test_scenario([
            OwnableModule,
            BackedOracleModule,
            BackedOracleForwarderModule,
            TestModule
        ])

        sc.h1("Backed Oracle Forwarder")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Robert")

        decimals = "18"
        description = "Backed Oracle contract"
        error = "No data present"

        oracle = BackedOracleModule.BackedOracle(owner=admin.address, updater=admin.address, decimals=decimals, description=description)

        sc += oracle

        oracleForwarder = BackedOracleForwarderModule.BackedOracleForwarder(owner=admin.address, upstreamOracle=oracle.address)
        
        sc += oracleForwarder

        sc.h1("Views - no answer data")
        sc.h2("Decimals")
        decimals_view_result = sc.compute(oracleForwarder.decimals(), source=alice)

        sc.verify(decimals_view_result== decimals)

        sc.h2("Description")
        description_view_result = sc.compute(oracleForwarder.description(), source=alice)

        sc.verify(description_view_result== description)

        sc.h2("Latest Answer")
        e = sp.catch_exception(oracleForwarder.latestAnswer())
        sc.verify(e == sp.some(error))

        sc.h2("Latest Timestamp")
        e = sp.catch_exception(oracleForwarder.latestTimestamp())
        sc.verify(e == sp.some(error))

        sc.h2("Latest Round")
        e = sp.catch_exception(oracleForwarder.latestTimestamp())
        sc.verify(e == sp.some(error))

        sc.h2("Latest Round Data")
        e = sp.catch_exception(oracleForwarder.latestTimestamp())
        sc.verify(e == sp.some(error))

        sc.h2("Get Answer")
        e = sp.catch_exception(oracleForwarder.getAnswer(1))
        sc.verify(e == sp.some(error))

        sc.h2("Get Round Data")
        e = sp.catch_exception(oracleForwarder.getRoundData(1))
        sc.verify(e == sp.some(error))

        time_in_secs = 10000
        time = sp.timestamp(time_in_secs)

        valid_timestamp = sp.timestamp(10000 - 100)
        valid_answer = sp.int(10)
        first_round_answer = valid_answer
        first_round_timestamp = valid_timestamp

        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=valid_timestamp)).run(sender=admin, now=time)

        sc.h1("Views - data available")
        # Reset to initial value

        sc.h2("Latest Answer")
        lastestAnswer_view_result = sc.compute(oracleForwarder.latestAnswer(), source=alice)

        sc.verify(lastestAnswer_view_result == valid_answer)

        sc.h2("Latest Timestamp")
        latestTimestamp_view_result = sc.compute(oracleForwarder.latestTimestamp(), source=alice)

        sc.verify(latestTimestamp_view_result == valid_timestamp)

        sc.h2("Latest Round")
        latestRound_view_result = sc.compute(oracleForwarder.latestRound(), source=alice)

        sc.verify(latestRound_view_result == sp.nat(1))

        sc.h2("Latest Round Data")
        latestRound_view_result = sc.compute(oracleForwarder.latestRoundData(), source=alice)

        sc.verify(latestRound_view_result == sp.record(
            roundId=sp.nat(1),
            answer=valid_answer,
            startedAt=valid_timestamp,
            updatedAt=valid_timestamp,
            answeredInRound=sp.nat(1)
        ))

        sc.h2("Get Answer")
        getAnswer_view_result = sc.compute(oracleForwarder.getAnswer(1), source=alice)

        sc.verify(getAnswer_view_result == first_round_answer)

        sc.h2("Get Round Data")
        getRound_view_result = sc.compute(oracleForwarder.getRoundData(1), source=alice)
        
        sc.verify(getRound_view_result == sp.record(
            roundId=sp.nat(1),
            answer=first_round_answer,
            startedAt=first_round_timestamp,
            updatedAt=first_round_timestamp,
            answeredInRound=sp.nat(1)
        ))

        sc.h1("Set upstream oracle")
        new_oracle = BackedOracleModule.BackedOracle(owner=admin.address, updater=admin.address, decimals=decimals, description=description)

        sc += new_oracle

        sc.h2("Sender has not have Admin role")
        oracleForwarder.setUpstreamOracle(new_oracle.address).run(sender=alice, valid=False)

        sc.h2("Sender has Admin role")
        oracleForwarder.setUpstreamOracle(new_oracle.address).run(sender=admin)
        sc.verify(oracleForwarder.data.upstreamOracle == new_oracle.address)


   


