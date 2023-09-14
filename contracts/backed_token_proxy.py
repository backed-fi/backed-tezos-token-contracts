import smartpy as sp
from contracts.backed_token import backed_token_module
from contracts.utils.admin import admin_module as admin

@sp.module
def backed_token_proxy_module():
    NOT_ADMIN_ERROR = "BackedTokenProxy_NotAdmin"


    class BackedTokenProxy(admin_module.Admin):
        def __init__(self, administrator, implementation, registry):
            admin_module.Admin.__init__(self, administrator)
            self.data.implementation = implementation
            self.data.registry = registry

        @sp.entrypoint
        def execute(self, params):
            sp.cast(params, sp.record(action=sp.string, data=sp.bytes))
            data = sp.pack(sp.record(address=self.data.implementation, data=params.data))

            self.data.registry[params.action](data)

        @sp.entrypoint
        def update(self, params):
            assert self.is_administrator_(sp.sender), NOT_ADMIN_ERROR

            self.data.implementation = params.implementation
            self.data.registry = params.registry

        @sp.entrypoint
        def update_action(self, params):
            assert self.is_administrator_(sp.sender), NOT_ADMIN_ERROR
            self.data.registry[params.action]=params.implementation



            