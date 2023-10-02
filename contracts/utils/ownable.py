import smartpy as sp

@sp.module
def OwnableModule():
    class OwnableInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def isOwner(self, sender):
            sp.cast(sp.sender, sp.address)
            """Not standard, may be re-defined through inheritance."""
            return True

    class Ownable(sp.Contract):
        ##
        # @dev Initializes the contract setting the address provided by the deployer as the initial owner.
        #
        # @param owner - sp.address     initial owner
        def __init__(self, owner):
            self.data.owner = owner
        ##
        # @dev Verifies sender as contract owner. Returns True if sender is owner and False if not.
        #
        # @param sender - sp.address    address that will be checked
        @sp.private(with_storage="read-only")
        def isOwner(self, sender):
            return sender == self.data.owner

        ##
        # @dev Transfers ownership of the contract to a new account.
        # Can only be called by the current owner.
        #
        # @param param - sp.address     new owner account
        #
        # Emits a { OwnershipTransferred } event
        @sp.entrypoint
        def transferOwnership(self, param):
            sp.cast(param, sp.address)
            assert self.isOwner(sp.sender), "Ownable_NotOwner"
            
            self._transferOwnership(param)
        ##
        # @dev Leaves the contract without owner. It will not be possible to call
        # functions that only owner can call. Can only be called by the current owner.
        #
        # Emits a { OwnershipTransferred } event
        #
        # NOTE: Renouncing ownership will leave the contract without an owner,
        # thereby disabling any functionality that is only available to the owner.
        @sp.entrypoint
        def renounceOwnership(self):
            assert self.isOwner(sp.sender), "Ownable_NotOwner"

            # null address
            self._transferOwnership(sp.address("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU")  )

        ##
        # @dev Transfers ownership of the contract to a new account.
        # Internal function without access restriction.
        #
        # @param param - sp.address - new owner account
        #
        @sp.private(with_storage="read-write", with_operations=True)
        def _transferOwnership(self, param):
            self.data.owner = param

            sp.emit(sp.record(address=self.data.owner), tag="OwnershipTransferred")

        @sp.entrypoint()
        def getOwner(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.address]])
            sp.transfer(self.data.owner, sp.tez(0), sp.snd(param))

        @sp.onchain_view()
        def get_owner(self):
            return self.data.owner
