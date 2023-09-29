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
                                        {
                                            "prim": "big_map",
                                            "args": [
                                                { "prim": "address" },
                                                {
                                                    "prim": "pair",
                                                    "args": [
                                                        { "prim": "map", "args": [{ "prim": "address" }, { "prim": "nat" }], "annots": ["%approvals"] },
                                                        { "prim": "nat", "annots": ["%balance"] }
                                                    ]
                                                }
                                            ],
                                            "annots": ["%balances"]
                                        },
                                        {
                                            "prim": "pair",
                                            "args": [
                                                { "prim": "bool", "annots": ["%delegateMode"] },
                                                {
                                                    "prim": "pair",
                                                    "args": [
                                                        { "prim": "big_map", "args": [{ "prim": "address" }, { "prim": "bool" }], "annots": ["%delegateWhitelist"] },
                                                        {
                                                            "prim": "pair",
                                                            "args": [
                                                                { "prim": "big_map", "args": [{ "prim": "string" }, { "prim": "bytes" }], "annots": ["%metadata"] },
                                                                {
                                                                    "prim": "pair",
                                                                    "args": [
                                                                        { "prim": "big_map", "args": [{ "prim": "address" }, { "prim": "nat" }], "annots": ["%nonce"] },
                                                                        {
                                                                            "prim": "pair",
                                                                            "args": [
                                                                                {
                                                                                    "prim": "pair",
                                                                                    "args": [{ "prim": "address", "annots": ["%burner"] }, { "prim": "address", "annots": ["%minter"] }],
                                                                                    "annots": ["%roles"]
                                                                                },
                                                                                {
                                                                                    "prim": "pair",
                                                                                    "args": [
                                                                                        { "prim": "string", "annots": ["%terms"] },
                                                                                        {
                                                                                            "prim": "pair",
                                                                                            "args": [
                                                                                                {
                                                                                                    "prim": "big_map",
                                                                                                    "args": [
                                                                                                        { "prim": "nat" },
                                                                                                        {
                                                                                                            "prim": "pair",
                                                                                                            "args": [
                                                                                                                { "prim": "nat", "annots": ["%token_id"] },
                                                                                                                { "prim": "map", "args": [{ "prim": "string" }, { "prim": "bytes" }], "annots": ["%token_info"] }
                                                                                                            ]
                                                                                                        }
                                                                                                    ],
                                                                                                    "annots": ["%token_metadata"]
                                                                                                },
                                                                                                { "prim": "nat", "annots": ["%total_supply"] }
                                                                                            ]
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
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
                                {
                                    "prim": "big_map",
                                    "args": [
                                        { "prim": "address" },
                                        {
                                            "prim": "pair",
                                            "args": [
                                                { "prim": "map", "args": [{ "prim": "address" }, { "prim": "nat" }], "annots": ["%approvals"] }, { "prim": "nat", "annots": ["%balance"] }
                                            ]
                                        }
                                    ],
                                    "annots": ["%balances"]
                                },
                                {
                                    "prim": "pair",
                                    "args": [
                                        { "prim": "bool", "annots": ["%delegateMode"] },
                                        {
                                            "prim": "pair",
                                            "args": [
                                                { "prim": "big_map", "args": [{ "prim": "address" }, { "prim": "bool" }], "annots": ["%delegateWhitelist"] },
                                                {
                                                    "prim": "pair",
                                                    "args": [
                                                        { "prim": "big_map", "args": [{ "prim": "string" }, { "prim": "bytes" }], "annots": ["%metadata"] },
                                                        {
                                                            "prim": "pair",
                                                            "args": [
                                                                { "prim": "big_map", "args": [{ "prim": "address" }, { "prim": "nat" }], "annots": ["%nonce"] },
                                                                {
                                                                    "prim": "pair",
                                                                    "args": [
                                                                        {
                                                                            "prim": "pair",
                                                                            "args": [{ "prim": "address", "annots": ["%burner"] }, { "prim": "address", "annots": ["%minter"] }],
                                                                            "annots": ["%roles"]
                                                                        },
                                                                        {
                                                                            "prim": "pair",
                                                                            "args": [
                                                                                { "prim": "string", "annots": ["%terms"] },
                                                                                {
                                                                                    "prim": "pair",
                                                                                    "args": [
                                                                                        {
                                                                                            "prim": "big_map",
                                                                                            "args": [
                                                                                                { "prim": "nat" },
                                                                                                {
                                                                                                    "prim": "pair",
                                                                                                    "args": [
                                                                                                        { "prim": "nat", "annots": ["%token_id"] },
                                                                                                        { "prim": "map", "args": [{ "prim": "string" }, { "prim": "bytes" }], "annots": ["%token_info"] }
                                                                                                    ]
                                                                                                }
                                                                                            ],
                                                                                            "annots": ["%token_metadata"]
                                                                                        },
                                                                                        { "prim": "nat", "annots": ["%total_supply"] }
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        }
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