import { InMemorySigner } from '@taquito/signer';
import { packDataBytes } from "@taquito/michel-codec"

import { TezosToolkit } from '@taquito/taquito';

import { getEnv } from "../helpers/config"

const RECIPIENT = "tz1gMzsf2SUKeKbzKgLjDYxpMye6eRD17uco"

const messageType = {
    "prim": "pair",
    "args": [
        { prim: 'int' },
        {
            prim: 'pair', args: [
                { prim: 'timestamp' }, { prim: 'pair', args: [{ prim: 'int' }, { prim: 'address' }] }
            ]
        }]

}

const MESSAGE_MICHELSON_CODE = (address: string, amount: string, expiration: string) => ({
    "prim": "Pair",
    "args": [
        { "int": amount },
        {
            "prim": "Pair", "args": [
                { "string": expiration }, { "prim": "Pair", "args": [{ "int": "0" }, { "string": address }] }
            ]
        }
    ]
})

const delegatedTransferType = {
    "prim": "pair",
    "args": [
        { "prim": "nat", "annots": ["%amount"] },
        {
            "prim": "pair",
            "args": [
                { "prim": "timestamp", "annots": ["%deadline"] },
                {
                    "prim": "pair",
                    "args": [
                        { "prim": "key", "annots": ["%owner"] },
                        { "prim": "pair", "args": [{ "prim": "signature", "annots": ["%signature"] }, { "prim": "address", "annots": ["%spender"] }] }
                    ]
                }
            ]
        }
    ],
}

const MICHELSON_CODE = (key: string, sig: string, address: string, amount: string, expiration: string) => ({
    "prim": "Pair",
    "args": [
        { "int": amount },
        {
            "prim": "Pair",
            "args": [
                { "string": expiration },
                {
                    "prim": "Pair",
                    "args": [
                        { "string": key },
                        {
                            "prim": "Pair",
                            "args": [
                                { "string": sig },
                                { "string": address }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
})

const main = async () => {
    const Tezos = new TezosToolkit(getEnv('TEZOS_RPC_URL', true));
    const signer = await InMemorySigner.fromSecretKey(getEnv("BACKED_TOKEN_ADMIN_PRIVATE_KEY"))

    const deadline = "2023-10-05T16:27:56Z"
    const value = "100"

    Tezos.setProvider({ signer });

    const { bytes: messageBytes } = packDataBytes(MESSAGE_MICHELSON_CODE(RECIPIENT, value, deadline) as any, messageType as any)

    const signature = await signer.sign(messageBytes);
    const key = await signer.publicKey();

    const { bytes } = packDataBytes(MICHELSON_CODE(key, signature.sig, RECIPIENT, value, deadline) as any, delegatedTransferType as any)

    try {
        const contract = await Tezos.contract
            .at(getEnv('BACKED_TOKEN'))

        const operation = await contract.methodsObject.execute({
            actionName: "delegatedTransfer",
            data: bytes
        }).send();

        console.log(`Waiting for ${operation.hash} to be confirmed...`);
        await operation.confirmation(1);

        console.log(`Operation injected: https://ghost.tzstats.com/${operation.hash}`)

    } catch (error) {
        console.log(`Error: ${JSON.stringify(error)}`)
    }
};

main().then(() => {
    console.log(`🌱 Backed Token implementation sucessfully updated`);
});