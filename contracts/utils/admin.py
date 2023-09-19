import smartpy as sp

@sp.module
def admin_module():
    class AdminInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def is_administrator_(self, sender):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""
            return True

    class Admin(sp.Contract):
        def __init__(self, administrator):
            self.data.administrator = administrator

        @sp.private(with_storage="read-only")
        def is_administrator_(self, sender):
            return sender == self.data.administrator

        @sp.entrypoint
        def setAdministrator(self, params):
            sp.cast(params, sp.address)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.administrator = params

        @sp.entrypoint()
        def getAdministrator(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.address]])
            sp.transfer(self.data.administrator, sp.tez(0), sp.snd(param))

        @sp.onchain_view()
        def get_administrator(self):
            return self.data.administrator
