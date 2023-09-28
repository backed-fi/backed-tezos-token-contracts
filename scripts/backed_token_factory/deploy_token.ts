import { InMemorySigner } from '@taquito/signer';
import { char2Bytes } from '@taquito/utils'

import { TezosToolkit } from '@taquito/taquito';

import { getEnv } from "../helpers/config"

const ADMIN_ADDRESS = 'tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd'
const MINTER_ADDRESS = 'tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd'
const BURNER_ADDRESS = 'tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd'
const PAUSER_ADDRESS = 'tz1exRAv3HPgWEm89BDZarhY9A6AYFXoxxxd'
const TOKEN_NAME = "Backed IB01 $ Treasury Bond 0-1yr"
const TOKEN_SYMBOL = "bIB01"
const TOKEN_DECIMALS = "18"
const TOKEN_ICON = "https://assets.website-files.com/6418671e8e48de1967843312/64e39beb6a4b261e47c6c763_bIB01.svg"

const main = async () => {
    const Tezos = new TezosToolkit(getEnv('TEZOS_RPC_URL', true));

    Tezos.setProvider({ signer: await InMemorySigner.fromSecretKey(getEnv("BACKED_TOKEN_FACTORY_ADMIN_PRIVATE_KEY")) });

    const token_metadata = {
        "decimals": char2Bytes(TOKEN_DECIMALS),
        "name": char2Bytes(TOKEN_NAME),
        "symbol": char2Bytes(TOKEN_SYMBOL),
        "icon": char2Bytes(TOKEN_ICON),
    }

    try {
        const contract = await Tezos.contract
            .at(getEnv('BACKED_TOKEN_FACTORY'))

        const operation = await contract.methodsObject.deployToken({
            burner: BURNER_ADDRESS,
            decimals: token_metadata.decimals,
            icon: token_metadata.icon,
            metadata: char2Bytes("ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"), // TODO
            tokenOwner: ADMIN_ADDRESS,
            name: token_metadata.name,
            minter: MINTER_ADDRESS,
            symbol: token_metadata.symbol,
            pauser: PAUSER_ADDRESS
        }).send();


        console.log(`Waiting for ${operation.hash} to be confirmed...`);
        await operation.confirmation(1);

        console.log(`Operation injected: https://ghost.tzstats.com/${operation.hash}`)

    } catch (error) {
        console.log(`Error: ${JSON.stringify(error, null, 2)}`)
    }
};

main().then(() => {
    console.log(`🌱 ${TOKEN_NAME}(${TOKEN_SYMBOL}) sucessfully deployed`);
});