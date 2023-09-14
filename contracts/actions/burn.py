import smartpy as sp
from contracts.actions.shared import shared_module

@sp.module
def burn_module():
    ExecuteParams: type = sp.record(address=sp.address, data=sp.bytes)
    BurnParams: type = sp.record(address=sp.address, value=sp.nat)

    @sp.effects(with_operations=True)
    def burn(data):
        sp.cast(data, sp.bytes)
        executeParams = sp.unpack(data, ExecuteParams).unwrap_some(error="Cannot UNPACK")
        mintParams= sp.unpack(executeParams.data, BurnParams).unwrap_some(error="Cannot UNPACK")
        
        dest = sp.contract(sp.record(value=sp.nat, address=sp.address), executeParams.address, entrypoint="burn")

        sp.transfer(sp.record(value=mintParams.value, address=mintParams.address), sp.tez(0), dest.unwrap_some())