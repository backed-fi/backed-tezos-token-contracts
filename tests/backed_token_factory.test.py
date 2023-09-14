import smartpy as sp
from contracts.backed_token_factory import backed_token_factory_module
from contracts.backed_token_proxy import backed_token_proxy_module
from contracts.backed_token import backed_token_module
from contracts.utils.admin import admin_module 
from contracts.utils.pause import pause_module 

from contracts.actions.mint import mint_module
from contracts.actions.burn import burn_module

@sp.module
def test_module():
     class Viewer_nat(sp.Contract):
        def __init__(self):
            self.data.last = sp.cast(None, sp.option[sp.nat])

        @sp.entrypoint
        def target(self, params):
            self.data.last = sp.Some(params)

if "templates" not in __name__:
    @sp.add_test(name="backed_token_factory")
    def test():
        sc = sp.test_scenario([
            admin_module,
            pause_module,
            mint_module,
            burn_module,
            backed_token_proxy_module,
            backed_token_module,
            backed_token_factory_module,
            test_module])
        sc.h1("Backed Token Factory")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Robert")


        f = backed_token_factory_module.BackedFactory(admin.address)

        sc+= f

        sc.h1("Attempt to update metadata")
