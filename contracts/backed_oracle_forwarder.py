import smartpy as sp

from contracts.backed_token import BackedTokenModule

from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule

@sp.module
def BackedOracleForwarderModule():
    ##
    # @dev
    #
    # Forwarder contract, used as facade for oracle
    # 
    # The contract contains one role:
    #  - An owner, which can change upstream oracle
    #
    class BackedOracleForwarder(OwnableModule.Ownable):
        def __init__(self, owner, upstreamOracle):
            OwnableModule.Ownable.__init__(self, owner)

            self.data.upstreamOracle = upstreamOracle

        @sp.onchain_view()
        def decimals(self):
            return sp.view(
                "decimals",
                self.data.upstreamOracle,
                (),
                sp.string
            ).unwrap_some(error="Invalid view")

        @sp.onchain_view()
        def description(self):
            return sp.view(
                "description",
                self.data.upstreamOracle,
                (),
                sp.string
            ).unwrap_some(error="Invalid view")

        @sp.onchain_view()
        def latestAnswer(self):
            return sp.view(
                "latestAnswer",
                self.data.upstreamOracle,
                (),
                sp.int
            ).unwrap_some(error="Invalid view")

        @sp.onchain_view()
        def latestTimestamp(self):
           return sp.view(
                "latestTimestamp",
                self.data.upstreamOracle,
                (),
                sp.timestamp
            ).unwrap_some(error="Invalid view")

        @sp.onchain_view()
        def latestRound(self):
            return sp.view(
                "latestRound",
                self.data.upstreamOracle,
                (),
                sp.nat
            ).unwrap_some(error="Invalid view")

        @sp.onchain_view()
        def latestRoundData(self):
            return sp.view(
                "latestRoundData",
                self.data.upstreamOracle,
                (),
                sp.record(
                    roundId=sp.nat,
                    answer=sp.int,
                    startedAt=sp.timestamp,
                    updatedAt=sp.timestamp,
                    answeredInRound=sp.nat
                )
            ).unwrap_some(error="Invalid view")

        @sp.onchain_view()
        def getAnswer(self, roundId):
            sp.cast(roundId, sp.nat)

            return sp.view(
                "getAnswer",
                self.data.upstreamOracle,
                roundId,
                sp.int
            ).unwrap_some(error="Invalid view")


        @sp.onchain_view()
        def getRoundData(self, roundId):
            sp.cast(roundId, sp.nat)

            return sp.view(
                "getRoundData",
                self.data.upstreamOracle,
                roundId,
                sp.record(
                    roundId=sp.nat,
                    answer=sp.int,
                    startedAt=sp.timestamp,
                    updatedAt=sp.timestamp,
                    answeredInRound=sp.nat
                )
            ).unwrap_some(error="Invalid view")

        @sp.entrypoint
        def setUpstreamOracle(self, param):
            assert self.isOwner(sp.sender), "BACKED_ORACLE_FORWARDER_NotOwner"

            self.data.upstreamOracle = param