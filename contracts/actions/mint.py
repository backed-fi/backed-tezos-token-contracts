import smartpy as sp
# from contracts.actions.shared import shared_module
# from contracts.shared.error_messages import CANNOT_UNPACK

@sp.module
def mint_module():
    ExecuteParams: type = sp.record(address=sp.address, data=sp.bytes)
    MintParams: type = sp.record(address=sp.address, value=sp.nat)

    @sp.effects(with_operations=True)
    def mint(data):
        sp.cast(data, sp.bytes)
        executeParams = sp.unpack(data, ExecuteParams).unwrap_some(error="CANNOT_UNPACK")
        mintParams= sp.unpack(executeParams.data, MintParams).unwrap_some(error="Cannot UNPACK")
        
        dest = sp.contract(sp.record(value=sp.nat, address=sp.address), executeParams.address, entrypoint="mint")

        sp.transfer(sp.record(value=mintParams.value, address=mintParams.address), sp.tez(0), dest.unwrap_some())