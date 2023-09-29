import { Schema } from "@taquito/michelson-encoder";

const updateImplementationType = {
    "prim": "big_map",
    "args": [
        { "prim": "string" },
        {
            "prim": "pair",
            "args": [
                {
                    "prim": "lambda",
                    "args": [
                        {
                            "prim": "pair",
                            "args": [
                                { "prim": "bytes", "annots": ["%data"] },
                                {
                                    "prim": "pair",
                                    "args": [
                                        { "prim": "string", "annots": ["%decimals"] },
                                        {
                                            "prim": "pair",
                                            "args": [
                                                { "prim": "string", "annots": ["%description"] },
                                                {
                                                    "prim": "pair",
                                                    "args": [
                                                        { "prim": "nat", "annots": ["%latestRoundNumber"] },
                                                        {
                                                            "prim": "pair",
                                                            "args": [
                                                                {
                                                                    "prim": "big_map",
                                                                    "args": [
                                                                        { "prim": "nat" },
                                                                        {
                                                                            "prim": "pair",
                                                                            "args": [{ "prim": "int", "annots": ["%answer"] }, { "prim": "timestamp", "annots": ["%timestamp"] }]
                                                                        }
                                                                    ],
                                                                    "annots": ["%roundData"]
                                                                },
                                                                { "prim": "address", "annots": ["%updater"] }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ],
                                    "annots": ["%storage"]
                                }
                            ]
                        },
                        {
                            "prim": "pair",
                            "args": [
                                { "prim": "string", "annots": ["%decimals"] },
                                {
                                    "prim": "pair",
                                    "args": [
                                        { "prim": "string", "annots": ["%description"] },
                                        {
                                            "prim": "pair",
                                            "args": [
                                                { "prim": "nat", "annots": ["%latestRoundNumber"] },
                                                {
                                                    "prim": "pair",
                                                    "args": [
                                                        {
                                                            "prim": "big_map",
                                                            "args": [
                                                                { "prim": "nat" },
                                                                { "prim": "pair", "args": [{ "prim": "int", "annots": ["%answer"] }, { "prim": "timestamp", "annots": ["%timestamp"] }] }
                                                            ],
                                                            "annots": ["%roundData"]
                                                        },
                                                        { "prim": "address", "annots": ["%updater"] }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "annots": ["%action"]
                },
                { "prim": "bool", "annots": ["%only_admin"] }
            ]
        }
    ]
}
const updateImplementationSchema = new Schema(updateImplementationType);

export { updateImplementationSchema };