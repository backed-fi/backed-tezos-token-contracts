import { TezosDeployer } from '../helpers/deployer';

const sourceCode = require('../../originations/backed_oracle_factory/backed_oracle_factory.json')
const storage = require('../../originations/backed_oracle_factory/backed_oracle_factory.storage.json')

const main = async () => {
    const tezosDeployer = new TezosDeployer();
    await tezosDeployer.init()


    await tezosDeployer.deploy(sourceCode, storage)
};

main().then(() => {
    console.log("🌱 Backed Oracle Factory sucessfully deployed");
});