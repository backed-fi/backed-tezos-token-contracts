import { InMemorySigner } from '@taquito/signer';
import { packDataBytes } from "@taquito/michel-codec"

import { TezosToolkit } from '@taquito/taquito';

import { getEnv } from "../helpers/config"

const mintType = {
    "prim": "pair",
    "args": [{ prim: 'int' }, { prim: 'string' }]

}

const RECIPIENT = "tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd"

const MICHELSON_CODE = (address: string, amount: string) => ({ "prim": "Pair", "args": [{ "string": address }, { "int": amount }] })

const main = async () => {
    const Tezos = new TezosToolkit(getEnv('TEZOS_RPC_URL', true));

    Tezos.setProvider({ signer: await InMemorySigner.fromSecretKey(getEnv("BACKED_TOKEN_ADMIN_PRIVATE_KEY")) });

    const data = packDataBytes(MICHELSON_CODE(RECIPIENT, "100") as any, mintType as any)

    debugger
    try {
        const contract = await Tezos.contract
            .at(getEnv('BACKED_TOKEN'))

        const operation = await contract.methodsObject.execute({
            actionName: "mint",
            data: data.bytes
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