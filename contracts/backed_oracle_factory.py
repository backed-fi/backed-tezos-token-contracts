import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
from contracts.backed_oracle_forwarder import BackedOracleForwarderModule

from contracts.utils.ownable import OwnableModule
from contracts.utils.pausable import PausableModule

@sp.module
def BackedOracleFactoryModule():
    ##
    # @dev
    #
    # Factory contract, used for creating new oracle contract.
    # 
    # The contract contains one role:
    #  - An owner, which can deploy new tokens
    #
    class BackedOracleFactory(OwnableModule.Ownable):
        ##
        # @param owner - sp.address      The address of the account that will be set as owner of the newly deployed contract
        # @param implementation - sp.big_map    Implementation of the actions in form of lambdas that take storage and return updated one, that can be invoked in newly deployed oracle
        #
        def __init__(self, implementation, owner):
            OwnableModule.Ownable.__init__(self, owner)
            # TODO: lambdas
            self.data.implementation = implementation
        
        ##
        # @dev Deploy and configures new instance of BackedFi Token. Callable only by the factory owner
        # 
        # @param owner - sp.address    The address of the account to which the owner role will be assigned
        # @param updater - sp.address    The address of the account to which the updater role will be assigned
        # @param decimals - sp.srring      The number of decimals that the oracle's token has
        # @param description - sp.string    The description of the oracle
        #
        # Emits a { NewOracle } event
        # Emits a { NewForwarder } event
        @sp.entrypoint
        def deploy_oracle(self, owner, updater, decimals, description):
            sp.cast(decimals, sp.string)
            sp.cast(description, sp.string)
            assert self.isOwner(sp.sender), "BACKED_TOKEN_Factory_NotOwner"

            newOracle = sp.create_contract(
                BackedOracleModule.BackedOracle,
                None,
                sp.mutez(0),
                sp.record(
                    owner=owner,
                    updater=updater,
                    decimals=decimals,
                    description=description,
                    storage=sp.record(
                        latestRoundNumber=0,
                        roundData=sp.big_map()
                    ),
                )
            )
            sp.emit(sp.record(address=newOracle), tag="NewOracle")

            newOracleForwarder = sp.create_contract(
                BackedOracleForwarderModule.BackedOracleForwarder,
                None,
                sp.mutez(0),
                sp.record(
                    owner=owner,
                    upstreamOracle=newOracle,
                )
            )
            sp.emit(sp.record(address=newOracleForwarder), tag="NewForwarder")

        ##
        # @dev Update the implementation for future deployments. Callable only by the factory owner
        # 
        # @param implementation - sp.big_map    New implementation of the actions in form of lambdas that take storage and return updated one, that can be invoked in newly deployed oracles
        #
        # Emits a { NewImplementation } event
        @sp.entrypoint
        def updateImplementation(self, implementation):
            assert self.isOwner(sp.sender), "BACKED_ORACLE_FACTORY_NotOwner"

            self.data.implementation = implementation

            sp.emit(sp.record(implementation=implementation), tag="NewImplementation")

            
