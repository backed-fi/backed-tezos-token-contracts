import smartpy as sp

from contracts.storage.backed_oracle import BackedOracleStorageModule

from contracts.utils.ownable import OwnableModule

@sp.module
def BackedOracleModule():
    class BackedOracle(OwnableModule.Ownable):
        '''
        Factory contract, used for creating new, upgradable tokens.

        The contract contains one role:
        - An owner, which can deploy new tokens
        '''
        def __init__(self, owner, implementation, updater, decimals, description):
            OwnableModule.Ownable.__init__(self, owner)

            self.data.storage.updater = updater
            self.data.storage.decimals = decimals
            self.data.storage.description = description

            sp.cast(self.data.storage, BackedOracleStorageModule.BackedOracle)

            self.data.storage.latestRoundNumber = 0
            self.data.storage.roundData = sp.big_map()

            sp.cast(implementation, sp.big_map[
                sp.string,
                sp.record(
                    action=sp.lambda_[
                        sp.record(storage=BackedOracleStorageModule.BackedOracle, data=sp.bytes),
                        BackedOracleStorageModule.BackedOracle
                    ],
                    only_admin=sp.bool
            )])

            self.data.implementation = implementation

        @sp.onchain_view()
        def decimals(self):
            return self.data.storage.decimals

        @sp.onchain_view()
        def description(self):
            return self.data.storage.description

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
        def execute(self, params):
            sp.cast(params, sp.record(actionName=sp.string, data=sp.bytes))

            actionEntry = self.data.implementation.get(params.actionName, error="BACKED_ORACLE_UnknownAction")

            if actionEntry.only_admin:
                assert self.isOwner(sp.sender), "BACKED_ORACLE_NotAdmin"

            updated_storage = self.data.implementation[params.actionName].action(sp.record(storage=self.data.storage, data=params.data))

            self.data.storage = updated_storage
 
        @sp.entrypoint
        def updateImplementation(self, implementation):
            '''
            Update the implementation. Callable only by the owner

            Params:
            implementation (sp.big_map) - New implementation of the actions in form of lambdas that take storage and return updated one
            '''
            assert self.isOwner(sp.sender), "BACKED_TOKEN_NotOwner"

            self.data.implementation = implementation

            
