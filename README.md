# Prerequisites

## Install smartpy

```
wget smartpy.io/smartpy
chmod a+x smartpy
```

# Local environment

## Start flextesa sandbox

```
make sandbox-pull
make flextesa-sandbox
```

Sandbox UI is now available at http://localhost:8000

RPC is now available at http://localhost:20000

Accounts to use:

- alice
  - Private key: `edpkvGfYw3LyB1UcCahKQk4rF2tvbMUk8GFiTuMjL75uGXrpvKXhjn`
  - Public hash: `tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb`
  - `unencrypted:edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq`
- bob
  - Private key: `edpkurPsQ8eUApnLUJ9ZPDvu98E8VNj4KtJa1aZr16Cr5ow5VHKnz4`
  - Public hash: `tz1aSkwEot3L2kmUvcoxzjMomb9mvBNuzFK6`
  - `unencrypted:edsk3RFfvaFaxbHx8BMtEW1rKQcPtDML3LXjNqMNLCzC3wLC1bWbAt`

## Stop flextesa sandbox

```
make sandbox-down
make sandbox-clear
```

# Test

- ### Backed Token Factory

```
npm run backed_token_factory:test
```

- ### Backed Token

```
npm run backed_token:test
```

- ### Backed Oracle Factory

```
npm run backed_oracle_factory:test
```

- ### Backed Oracle

```
npm run backed_oracle:test
```

# Origination

### 1. Fill missing data in `.env` file.

- ### Backed Token Factory

  #### NOTE: This step should be done only once

1. Generate Michelson code

```
npm run backed_token_factory:originate
```

2. Move generated Michelson to `originations/backed_token_factory/backed_token_factory.json` and storage to `originations/backed_token_factory/backed_token_factory.storage.json`
3. Originate contract

```
npm run backed_token_factory:deploy
```

- ### Backed Oracle Factory

  #### NOTE: This step should be done only once

1. Generate Michelson code

```
npm run backed_oracle_factory:originate
```

2. Move generated Michelson to `originations/backed_oracle_factory/backed_oracle_factory.json` and storage to `originations/backed_oracle_factory/backed_oracle_factory.storage.json`

3. Originate contract

```
npm run backed_oracle_factory:deploy
```

# Deployment

### 1. Fill missing data in `.env` file.

- ### Backed Token

1. Update related constant values in `scripts/backed_token_factory/deploy_token.ts` file

2. Deploy token

```
npm run backed_token:deploy
```

- ### Backed Oracle

1. Update related constant values in `scripts/backed_oracle_factory/deploy_oracle.ts` file

2. Deploy oracle

```
npm run backed_oracle:deploy
```
