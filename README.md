## Prerequisites

# Install smartpy

```
wget smartpy.io/smartpy
chmod a+x smartpy
```

start
make sandbox-pull
make flextesa-sandbox

## Local

# Start flextesa sandbox

```
make sandbox-pull
make flextesa-sandbox
```

Sandbox UI is now available at http://localhost:8000

- alice
  - edpkvGfYw3LyB1UcCahKQk4rF2tvbMUk8GFiTuMjL75uGXrpvKXhjn
  - tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
  - unencrypted:edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq
- bob
  - edpkurPsQ8eUApnLUJ9ZPDvu98E8VNj4KtJa1aZr16Cr5ow5VHKnz4
  - tz1aSkwEot3L2kmUvcoxzjMomb9mvBNuzFK6
  - unencrypted:edsk3RFfvaFaxbHx8BMtEW1rKQcPtDML3LXjNqMNLCzC3wLC1bWbAt

# Stop flextesa sandbox

```
make sandbox-down
make sandbox-clear
```

## Test

```
./smartpy test tests/backed_token.test.py output
```

## Origination

TODO:
