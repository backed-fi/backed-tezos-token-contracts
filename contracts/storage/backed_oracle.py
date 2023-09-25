import smartpy as sp

@sp.module
def BackedOracleStorageModule():
    BackedOracle: type = sp.record(
        updater=sp.address,
        decimals=sp.string,
        description=sp.string,
        latestRoundNumber=sp.nat,
        roundData=sp.big_map[sp.nat, sp.record(answer=sp.int, timestamp=sp.timestamp)]
    )