import smartpy as sp

from contracts.backed_token import BackedTokenModule

from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule

@sp.module
def BackedOracleModule():
    ##
    # @dev
    #
    # Factory contract, used for creating new, upgradable tokens.
    # 
    # The contract contains one role:
    #  - An owner, which can deploy new tokens
    #
    class BackedOracle(OwnableModule.Ownable):
        def __init__(self, owner, updater, decimals, description):
            OwnableModule.Ownable.__init__(self, owner)

            self.data.updater = updater
            self.data.decimals = decimals
            self.data.description = description

            self.data.storage.latestRoundNumber = 0
            sp.cast(self.data.storage.roundData, sp.big_map[sp.nat, sp.record(answer=sp.int, timestamp=sp.timestamp)])
            self.data.storage.roundData = sp.big_map()

        @sp.onchain_view()
        def decimals(self):
            return self.data.decimals

        @sp.onchain_view()
        def description(self):
            return self.data.description

        @sp.onchain_view()
        def latestAnswer(self):
            assert self.data.storage.latestRoundNumber != 0, "No data present"

            return self.data.storage.roundData[self.data.storage.latestRoundNumber].answer

        @sp.onchain_view()
        def latestTimestamp(self):
            assert self.data.storage.latestRoundNumber != 0, "No data present"

            return self.data.storage.roundData[self.data.storage.latestRoundNumber].timestamp

        @sp.onchain_view()
        def latestRound(self):
            assert self.data.storage.latestRoundNumber != 0, "No data present"

            return self.data.storage.latestRoundNumber

        @sp.onchain_view()
        def latestRoundData(self):
            assert self.data.storage.latestRoundNumber != 0, "No data present"

            return sp.record(
                roundId=self.data.storage.latestRoundNumber,
                answer=self.data.storage.roundData[self.data.storage.latestRoundNumber].answer,
                startedAt=self.data.storage.roundData[self.data.storage.latestRoundNumber].timestamp,
                updatedAt=self.data.storage.roundData[self.data.storage.latestRoundNumber].timestamp,
                answeredInRound=self.data.storage.latestRoundNumber
            )

        @sp.onchain_view()
        def getAnswer(self, roundId):
            assert roundId <= self.data.storage.latestRoundNumber, "No data present"

            return self.data.storage.roundData[roundId].answer

        @sp.onchain_view()
        def getRoundData(self, roundId):
            assert  roundId <= self.data.storage.latestRoundNumber, "No data present"

            return sp.record(
                roundId=roundId,
                answer=self.data.storage.roundData[roundId].answer,
                startedAt=self.data.storage.roundData[roundId].timestamp,
                updatedAt=self.data.storage.roundData[roundId].timestamp,
                answeredInRound=roundId
            )

        @sp.entrypoint
        def updateAnswer(self, params):
            assert sp.sender == self.data.updater, "BACKED_ORACLE_NotUpdater"

            sp.cast(params, sp.record(newAnswer=sp.int, newTimestamp=sp.timestamp))
            latestRoundData = self.data.storage.roundData.get(self.data.storage.latestRoundNumber, default=sp.record(answer=0, timestamp=sp.timestamp(0)))    

            assert params.newTimestamp < sp.now, "Timestamp cannot be in the future"
            # TODO: constants?
            assert sp.now - params.newTimestamp < 300, "Timestamp is too old"
            assert params.newTimestamp > latestRoundData.timestamp, "Timestamp is older than the last update"
            assert params.newTimestamp - latestRoundData.timestamp > 3600, "Timestamp cannot be updated too often"

            newAnswer = params.newAnswer

            if latestRoundData.answer > 0:
                allowedDeviation = latestRoundData.answer * 10 / 100
                if params.newAnswer > latestRoundData.answer + allowedDeviation:
                    newAnswer = latestRoundData.answer + allowedDeviation
                if params.newAnswer < latestRoundData.answer - allowedDeviation:
                    newAnswer = latestRoundData.answer - allowedDeviation
                

            self.data.storage.latestRoundNumber += 1

            self.data.storage.roundData[self.data.storage.latestRoundNumber] = sp.record(answer=newAnswer, timestamp=params.newTimestamp)
            
            sp.emit(sp.record(answer=newAnswer, timestamp=params.newTimestamp), tag="AnswerUpdated")
            sp.emit(sp.record(roundId=self.data.storage.latestRoundNumber, sender=sp.sender), tag="NewRound")
