import smartpy as sp
from contracts.shared.storage import StorageModule

@sp.module
def BurnModule():
    BurnParams: type = sp.record(address=sp.address, value=sp.nat)

    ##
    # @dev Function to burn tokens. Allowed only for burner. The burned tokens
    # must be from the burner (msg.sender), or from the contract itself
    #
    # @param account   The account from which the tokens will be burned
    # @param amount    The amount of tokens to be burned
    #
    @sp.effects()
    def burn(storage, data):
        assert sp.sender == storage.roles.burner, "BACKED_TOKEN_Burn_NotBurner"

        sp.cast(storage, StorageModule.BackedToken)
        sp.cast(data, sp.bytes)
        burnParams = sp.unpack(data, BurnParams).unwrap_some(error="BACKED_TOKEN_Burn_CannotUnpackParams")

        updated_storage = storage
        
        receiver_balance = updated_storage.balances.get(
            burnParams.address, default=sp.record(balance=0, approvals={})
        )
        receiver_balance.balance = sp.as_nat(
            receiver_balance.balance - burnParams.value,
            error="BACKED_TOKEN_Burn_InsufficientBalance",
        )
        updated_storage.balances[burnParams.address] = receiver_balance
        updated_storage.total_supply = sp.as_nat(updated_storage.total_supply - burnParams.value)

        return updated_storage