import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
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
    @sp.add_test(name="backed_oracle")
    def test():
        sc = sp.test_scenario([
            OwnableModule,
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

        oracle = BackedOracleModule.BackedOracle(owner=admin.address, updater=admin.address, decimals=decimals, description=description)

        sc += oracle

        sc.h1("Views - no answer data")
        sc.h2("Decimals")
        decimals_view_result = sc.compute(oracle.decimals(), source=alice)

        sc.verify(decimals_view_result== decimals)

        sc.h2("Description")
        description_view_result = sc.compute(oracle.description(), source=alice)

        sc.verify(description_view_result== description)

        sc.h2("Latest Answer")
        e = sp.catch_exception(oracle.latestAnswer())
        sc.verify(e == sp.some(error))

        sc.h2("Latest Timestamp")
        e = sp.catch_exception(oracle.latestTimestamp())
        sc.verify(e == sp.some(error))

        sc.h2("Latest Round")
        e = sp.catch_exception(oracle.latestTimestamp())
        sc.verify(e == sp.some(error))

        sc.h2("Latest Round Data")
        e = sp.catch_exception(oracle.latestTimestamp())
        sc.verify(e == sp.some(error))
        
        sc.h2("Get Answer")
        e = sp.catch_exception(oracle.getAnswer(1))
        sc.verify(e == sp.some(error))

        sc.h2("Get Round Data")
        e = sp.catch_exception(oracle.getRoundData(1))
        sc.verify(e == sp.some(error))
   
        sc.h1("Update answer")
        time_in_secs = 10000
        time = sp.timestamp(time_in_secs)

        valid_timestamp = sp.timestamp(10000 - 100)
        valid_answer = sp.int(10)
        first_round_answer = valid_answer
        first_round_timestamp = valid_timestamp

        sc.h2("Sender has not have an Updater role")
        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=valid_timestamp)).run(sender=alice, valid=False)
        
        sc.h2("Timestamp in the future")
        timestamp = time.add_seconds(60)
        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=timestamp)).run(sender=admin, valid=False, now=time)
        
        sc.h2("Timestamp too old")
        timestamp = sp.timestamp(time_in_secs - 301)
        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=timestamp)).run(sender=admin, valid=False, now=time)
        
        sc.h2("Too frequent update")
        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=valid_timestamp)).run(sender=admin, now=time)

        timestamp = sp.timestamp(time_in_secs - 50)
        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=timestamp)).run(sender=admin, valid=False, now=time)

        sc.h2("Answer is older than last updated")
        timestamp = sp.timestamp(time_in_secs - 150)
        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=timestamp)).run(sender=admin, valid=False, now=time)

        sc.h2("Answer difference is past allowed deviation")
        new_answer = valid_answer + (valid_answer * 20 / 100)
        
        time = time.add_seconds(3601)
        valid_timestamp = valid_timestamp.add_seconds(3601)
        oracle.updateAnswer(sp.record(newAnswer=new_answer, newTimestamp=valid_timestamp)).run(sender=admin, now=time)

        sc.verify(sc.compute(oracle.latestAnswer(), source=alice) == valid_answer + (valid_answer * 10 / 100))

        # Reset to initial value

        time = time.add_seconds(3601)
        valid_timestamp = valid_timestamp.add_seconds(3601)
        oracle.updateAnswer(sp.record(newAnswer=valid_answer, newTimestamp=valid_timestamp)).run(sender=admin, now=time)

        # Test with decreased answer

        new_answer = valid_answer - (valid_answer * 20 / 100)
        
        time = time.add_seconds(3601)
        valid_timestamp = valid_timestamp.add_seconds(3601)
        oracle.updateAnswer(sp.record(newAnswer=new_answer, newTimestamp=valid_timestamp)).run(sender=admin, now=time)

        sc.verify(sc.compute(oracle.latestAnswer(), source=alice) == valid_answer - (valid_answer * 10 / 100))


        sc.h1("Views - data available")
        # Reset to initial value

        valid_answer = valid_answer - (valid_answer * 10 / 100)

        sc.h2("Latest Answer")
        lastestAnswer_view_result = sc.compute(oracle.latestAnswer(), source=alice)

        sc.verify(lastestAnswer_view_result == valid_answer)

        sc.h2("Latest Timestamp")
        latestTimestamp_view_result = sc.compute(oracle.latestTimestamp(), source=alice)

        sc.verify(latestTimestamp_view_result == valid_timestamp)

        sc.h2("Latest Round")
        latestRound_view_result = sc.compute(oracle.latestRound(), source=alice)

        sc.verify(latestRound_view_result == sp.nat(4))

        sc.h2("Latest Round Data")
        latestRound_view_result = sc.compute(oracle.latestRoundData(), source=alice)

        sc.verify(latestRound_view_result == sp.record(
            roundId=sp.nat(4),
            answer=valid_answer,
            startedAt=valid_timestamp,
            updatedAt=valid_timestamp,
            answeredInRound=sp.nat(4)
        ))

        sc.h2("Get Answer")
        getAnswer_view_result = sc.compute(oracle.getAnswer(1), source=alice)

        sc.verify(getAnswer_view_result == first_round_answer)

        sc.h2("Get Round Data")
        getRound_view_result = sc.compute(oracle.getRoundData(1), source=alice)
        
        sc.verify(getRound_view_result == sp.record(
            roundId=sp.nat(1),
            answer=first_round_answer,
            startedAt=first_round_timestamp,
            updatedAt=first_round_timestamp,
            answeredInRound=sp.nat(1)
        ))


