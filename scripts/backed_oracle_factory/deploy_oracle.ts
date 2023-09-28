import { InMemorySigner } from '@taquito/signer';
import { char2Bytes } from '@taquito/utils'

import { TezosToolkit } from '@taquito/taquito';

import { getEnv } from "../helpers/config"

const ADMIN_ADDRESS = 'tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd'
const UPDATER_ADDRESS = 'tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd'
const ORACLE_DECIMALS = "18"
const ORACLE_DESCRIPTION = "Backed Oracle"

const main = async () => {
    const Tezos = new TezosToolkit(getEnv('TEZOS_RPC_URL', true));

    Tezos.setProvider({ signer: await InMemorySigner.fromSecretKey(getEnv("BACKED_ORACLE_FACTORY_ADMIN_PRIVATE_KEY")) });

    const oracle_metadata = {
        "decimals": ORACLE_DECIMALS,
        "description": ORACLE_DESCRIPTION,
    }

    try {
        const contract = await Tezos.contract
            .at(getEnv('BACKED_ORACLE_FACTORY'))

        const operation = await contract.methodsObject.deployOracle({
            owner: ADMIN_ADDRESS,
            updater: UPDATER_ADDRESS,
            description: oracle_metadata.description,
            decimals: oracle_metadata.decimals
        }).send();


        console.log(`Waiting for ${operation.hash} to be confirmed...`);
        await operation.confirmation(1);

        console.log(`Operation injected: https://ghost.tzstats.com/${operation.hash}`)

    } catch (error) {
        console.log(`Error: ${JSON.stringify(error)}`)
    }
};

main().then(() => {
    console.log(`🌱 Backed Oracle sucessfully deployed`);
});