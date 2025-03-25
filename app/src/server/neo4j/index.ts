import neo4j from "neo4j-driver";
import { env } from "~/env";

export const neoDriver = neo4j.driver(
    env.NEO4J_URL,
    neo4j.auth.basic(env.NEO4J_USER, env.NEO4J_PASSWORD),
);
