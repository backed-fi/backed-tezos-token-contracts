import { InMemorySigner } from '@taquito/signer';

import { TezosToolkit } from '@taquito/taquito';

import { updateImplementationSchema } from './schemas/update_implementation.schema'
import { getEnv } from "../helpers/config"

const MICHELSON_CODE: any[] = []

const main = async () => {
    const Tezos = new TezosToolkit(getEnv('TEZOS_RPC_URL', true));

    Tezos.setProvider({ signer: await InMemorySigner.fromSecretKey(getEnv("BACKED_TOKEN_FACTORY_ADMIN_PRIVATE_KEY")) });

    const data = updateImplementationSchema.Execute(MICHELSON_CODE);

    debugger
    try {
        const contract = await Tezos.contract
            .at(getEnv('BACKED_TOKEN_FACTORY'))

        const operation = await contract.methods.updateImplementation(data).send();


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