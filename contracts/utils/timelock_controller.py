import smartpy as sp

@sp.module
def TimelockControllerModule():
    # class TimelockControllerInterface(sp.Contract):
    #     @sp.entrypoint
    #     def schedule(self, action, value, delay):
    #         """Not standard, may be re-defined through inheritance."""
    #         return 0
    #     @sp.entrypoint
    #     def execute(self, operationId):
    #         """Not standard, may be re-defined through inheritance."""

    class TimelockController(sp.Contract):
        def __init__(self, proposers, executors):
            sp.cast(proposers, sp.set[sp.address])
            sp.cast(executors, sp.set[sp.address])

            self.data.proposers = proposers
            self.data.executors = executors

            sp.cast(self.data.timelock, sp.big_map[sp.bytes, sp.timestamp])
            
            self.data.timelock = sp.big_map()


        @sp.entrypoint
        def schedule(self, action, data, delay):
            sp.cast(action, sp.lambda_(sp.record(target=sp.address, data=sp.bytes), sp.bool, [with_operations="true"|"false"]))
            sp.cast(data, sp.bytes)
            sp.cast(delay, sp.int)

            assert self.data.proposers.contains(sp.sender), "NOT_PROPOSER"

            operationId = sp.keccak(sp.pack(sp.record(action=action, data=data, delay=delay)))

            self.data.timelock[operationId] = sp.add_seconds(sp.now, delay)
            
        @sp.entrypoint
        def execute(self, action, data, delay):
            # sp.cast(action, sp.lambda_[sp.bytes, sp.bool])
            sp.cast(data, sp.bytes)
            sp.cast(delay, sp.int)

            assert self.data.executors.contains(sp.sender), "NOT_EXECUTOR"

            operationId = sp.keccak(sp.pack(sp.record(action=action, data=data, delay=delay)))

            assert self.data.timelock[operationId] >= sp.now, "TOO_EARLY"

            success = action(data)
            
        