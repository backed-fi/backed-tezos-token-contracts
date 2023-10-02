import smartpy as sp
from contracts.storage.backed_oracle import BackedOracleStorageModule

@sp.module
def UpdateAnswerModule():
    UpdateAnswerParams: type = sp.record(newAnswer=sp.int, newTimestamp=sp.timestamp)
    
    @sp.effects()
    def updateAnswer(storage, data):
        '''
        Updates BackedOracle answer and sets up new round

        Params:
        storage (BackedOracle storage) - current storage of the BackedOracle contract
        data (sp.bytes) - packed UpdateAnswersParams

        Returs:
        BackedOracle storage: Updated storage object
        '''
        sp.cast(storage, BackedOracleStorageModule.BackedOracle)
        sp.cast(data, sp.bytes)
        params = sp.unpack(data, UpdateAnswerParams).unwrap_some(error="BACKED_Oracle_UpdateAnswer_CannotUnpackParams")

        assert sp.sender == storage.updater, "BACKED_ORACLE_NotUpdater"

        updated_storage = storage

        latestRoundData = updated_storage.roundData.get(updated_storage.latestRoundNumber, default=sp.record(answer=0, timestamp=sp.timestamp(0)))    

        assert params.newTimestamp < sp.now, "Timestamp cannot be in the future"
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
            

        updated_storage.latestRoundNumber += 1

        updated_storage.roundData[updated_storage.latestRoundNumber] = sp.record(answer=newAnswer, timestamp=params.newTimestamp)
        
        return updated_storage
        # sp.emit(sp.record(answer=newAnswer, timestamp=params.newTimestamp), tag="AnswerUpdated")
        # sp.emit(sp.record(roundId=updated_storage.latestRoundNumber, sender=sp.sender), tag="NewRound")