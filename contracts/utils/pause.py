import smartpy as sp
from contracts.utils.admin import admin_module

@sp.module
def pause_module():
    class Pause(admin_module.AdminInterface):
        def __init__(self):
            admin_module.AdminInterface.__init__(self)
            self.data.paused = False

        @sp.private(with_storage="read-only")
        def is_paused_(self):
            return self.data.paused

        @sp.entrypoint
        def setPause(self, param):
            sp.cast(param, sp.bool)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.paused = param