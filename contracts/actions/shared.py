import smartpy as sp

@sp.module
def shared_module():
    ExecuteParams: type = sp.record(address=sp.address, data=sp.bytes)