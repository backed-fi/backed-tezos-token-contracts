import smartpy as sp
from contracts.backed_token_factory import module 

@sp.module
def test_module():
     class Viewer_nat(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.nat])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)

if "templates" not in __name__:
    sc = sp.test_scenario([module, test_module])
    sc.h1("Backed Token Factory")

    # sp.test_account generates ED25519 key-pairs deterministically:
    admin = sp.test_account("Administrator")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Robert")


    f = module.BackedFactory(admin.address)

    sc+= f
