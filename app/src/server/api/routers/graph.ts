import { type Integer, routing } from "neo4j-driver";
import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

const GET_GRAPHS_QUERY = `
MATCH (p:Project) RETURN p.datasetName as name
`;

const GET_SENTIMENT_QUERY = `
MATCH (p:Project { datasetName: $datasetName }),
      (p)-[:OWNS]->(u:User)-[r:SENTIMENT]-(u2:User)<-[:OWNS]-(p)
WHERE u.email CONTAINS $email AND u2.email ENDS WITH $endsWith
RETURN u.email, r.emailsSent, r.sentiment, u2.email
`;

type SentimentLink = {
    emailsSent: number;
    sentiment: number;
};

export const graphRouter = createTRPCRouter({
    getGraphs: publicProcedure.query(async ({ ctx: { neoDriver } }) => {
        const { records } = await neoDriver.executeQuery(
            GET_GRAPHS_QUERY,
            {},
            { routing: routing.READ },
        );

        return records.map((r) => r.get("name") as string);
    }),
    getRelationships: publicProcedure
        .input(
            z.object({
                datasetName: z.string().min(1),
                email: z.string(),
                endsWith: z.string(),
            }),
        )
        .mutation(async ({ ctx: { neoDriver }, input }) => {
            const info: [string, SentimentLink, string][] = [];

            const { records } = await neoDriver.executeQuery(
                GET_SENTIMENT_QUERY,
                input,
                { routing: routing.READ },
            );

            for (const record of records) {
                const sender = record.get("u.email") as string;
                const receiver = record.get("u2.email") as string;
                const sentiment = record.get("r.sentiment") as number;
                const emailsSent = record.get("r.emailsSent") as Integer;

                info.push([
                    sender,
                    {
                        sentiment: Math.round(sentiment * 100) / 100,
                        emailsSent: emailsSent.toInt(),
                    },
                    receiver,
                ]);
            }

            return info;
        }),
});
