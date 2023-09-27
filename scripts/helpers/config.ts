import * as dotenv from "dotenv";

dotenv.config();

export const getEnv = <T extends any>(key: string, throwErr: boolean = false): T => {
    const value = process.env[key];

    if (!value) {
        console.warn(`Missing value for ${key}!`);

        if (throwErr) {
            throw new Error(`Missing env value: ${key}`);
        }
    }

    return value as T;
};