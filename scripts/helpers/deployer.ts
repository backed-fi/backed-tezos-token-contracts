import { TezosToolkit } from "@taquito/taquito";
import { getEnv } from "./config";
import { InMemorySigner } from "@taquito/signer";

export class TezosDeployer {
    private readonly tezos: TezosToolkit

    constructor() {
        this.tezos = new TezosToolkit(getEnv('TEZOS_RPC_URL', true));
    }

    async init() {
        this.tezos.setProvider({ signer: await InMemorySigner.fromSecretKey(getEnv("TEZOS_DEPLOYER_PRIVATE_KEY")) });
    }

    async deploy(sourceCode: any, storage: string) {
        try {
            const origination = await this.tezos.contract
                .originate({
                    code: sourceCode,
                    init: storage
                });

            await origination.confirmation();

            const contract = await origination.contract();
            console.log(`Operation Hash: ${origination.hash}`);
            console.log(`Contract Address: ${contract.address}`);
        } catch (err) {
            console.log(err)
        }
    }
}