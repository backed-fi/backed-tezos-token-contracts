import smartpy as sp
from contracts.backed_token import backed_token_module

@sp.module
def backed_token_proxy_module():
    class BackedTokenProxy(sp.Contract):
        def __init__(self, backed_token):
            self.data.backed_token = backed_token

        @sp.entrypoint
        def mint(self, param):
            dest = sp.contract(sp.record(address=sp.address, value=sp.nat), self.data.backed_token, entrypoint="mint")
            sp.transfer(param, sp.tez(0), dest.unwrap_some())

        @sp.entrypoint
        def burn(self, param):
            dest = sp.contract(sp.record(address=sp.address, value=sp.nat), self.data.backed_token, entrypoint="burn")
            sp.transfer(param, sp.tez(0), dest.unwrap_some())

        @sp.entrypoint
        def transfer(self, param):
            dest = sp.contract(sp.record(from_=sp.address, to_=sp.address, value=sp.nat).layout(
                    ("from_ as from", ("to_ as to", "value"))
                ), self.data.backed_token, entrypoint="transfer")
            sp.transfer(param, sp.tez(0), dest.unwrap_some())


            