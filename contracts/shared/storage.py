import smartpy as sp

@sp.module
def StorageModule():
    BackedToken: type = sp.record(
        balances=sp.big_map[sp.address, sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat)],
        total_supply=sp.nat,
        token_metadata=sp.big_map[sp.nat, sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes])],
        metadata=sp.big_map[sp.string, sp.bytes],
        terms=sp.string,
        roles=sp.record(minter=sp.address, burner=sp.address),
        nonce=sp.big_map[sp.address, sp.nat],
        delegateMode=sp.bool,
        delegateWhitelist=sp.big_map[sp.address, sp.bool]
    )