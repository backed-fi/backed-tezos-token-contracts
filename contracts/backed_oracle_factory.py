import smartpy as sp

from contracts.backed_oracle import BackedOracleModule
from contracts.backed_oracle_forwarder import BackedOracleForwarderModule

from contracts.utils.ownable import OwnableModule

@sp.module
def BackedOracleFactoryModule():
    class BackedOracleFactory(OwnableModule.Ownable):
        '''
        Factory contract, used for creating new oracle contract.

        The contract contains one role:
        - An owner, which can deploy new tokens
        '''
        def __init__(self, implementation, owner, metadata):
            '''
            Params:
            owner (sp.address) - the address of the account that will be set as owner of the newly deployed contract
            implementation (sp.big_map) - New implementation of the actions in form of lambdas that 
                        take storage and return updated one, that can be invoked in newly deployed oracles
            '''
            OwnableModule.Ownable.__init__(self, owner)
            self.data.metadata=metadata
            self.data.implementation = implementation
        
        @sp.entrypoint
        def deployOracle(self, owner, updater, decimals, description, metadata):
            '''
            Deploy and configures new instance of BackedFi Token. Callable only by the factory owner

            Params:
            owner (sp.address) - the address of the account to which the owner role will be assigned
            updater (sp.address) - the address of the account to which the updater role will be assigned
            decimals (sp.string) - the number of decimals that the oracle's token has
            description (sp.string) - the description of the oracle

            Emits:
            NewOracle event
            NewForwarder event
            '''
            sp.cast(decimals, sp.string)
            sp.cast(description, sp.string)
            assert self.isOwner(sp.sender), "BACKED_TOKEN_Factory_NotOwner"

            metadata_storage = sp.big_map({"" : metadata})

            newOracle = sp.create_contract(
                BackedOracleModule.BackedOracle,
                None,
                sp.mutez(0),
                sp.record(
                    owner=owner,
                    storage=sp.record(
                        latestRoundNumber=0,
                        roundData=sp.big_map(),
                        updater=updater,
                        decimals=decimals,
                        description=description,
                    ),
                    metadata=metadata_storage,
                    implementation=self.data.implementation
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

        @sp.entrypoint
        def updateMetadata(self, key, value):
            '''
            An entrypoint to allow the contract metadata to be updated

            Params:
            key (sp.string) - metadata's key for entry that will be changed
            value (sp.bytes) - updated metadata data
            '''
            assert self.isOwner(sp.sender), "BACKED_ORACLE_NotOwner"
            self.data.metadata[key] = value

        @sp.entrypoint
        def updateImplementation(self, implementation):
            '''
            Update the implementation for future deployments. Callable only by the factory owner

            Params:
            implementation (sp.big_map) - New implementation of the actions in form of lambdas that 
                    take storage and return updated one, that can be invoked in newly deployed oracles
            '''
            assert self.isOwner(sp.sender), "BACKED_ORACLE_FACTORY_NotOwner"

            self.data.implementation = implementation

            
