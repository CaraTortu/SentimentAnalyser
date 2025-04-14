import { type Integer, routing } from "neo4j-driver";
import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

const GET_GRAPHS_QUERY = `
MATCH (p:Project) RETURN p.datasetName as name
`;

const GET_SENTIMENT_QUERY = `
MATCH (p:Project { datasetName: $datasetName }),
      (p)-[:OWNS]->(u:User)-[r:SENTIMENT]-(u2:User)<-[:OWNS]-(p)
WHERE u.email STARTS WITH $email AND u2.email ENDS WITH $endsWith
RETURN u.email, r.emailsSent, r.sentiment, u2.email
`;

const GET_SENTIMENT_DISTRIBUTION_QUERY = `
MATCH (:User)-[r:SENTIMENT]-(:User)
WITH DISTINCT r
WITH 
  count(r) AS total,
  count(CASE WHEN r.sentiment > 0.75 THEN 1 END) AS positive,
  count(CASE WHEN r.sentiment >= 0.3 AND r.sentiment <= 0.75 THEN 1 END) AS neutral,
  count(CASE WHEN r.sentiment < 0.3 THEN 1 END) AS negative
RETURN
  round(toFloat(positive) / total * 100, 2) AS positivePercent,
  round(toFloat(neutral) / total * 100, 2) AS neutralPercent,
  round(toFloat(negative) / total * 100, 2) AS negativePercent
`;

const GET_TOTAL_EMAILS_QUERY = `
MATCH (:User)-[r:SENTIMENT]-(:User)
WITH DISTINCT r
RETURN sum(r.emailsSent) AS totalEmailsSent
`;

const GET_USERS_WHO_SENT_MANY = `
MATCH (u:User)-[r:SENTIMENT]-(u2:User)
WITH u, sum(r.emailsSent) AS totalEmails
WHERE totalEmails > 250
RETURN count(DISTINCT u) AS chatters 
`;

const GET_LARGEST_CHATTERS = `
MATCH (p:Project)-[:OWNS]->(u:User)
MATCH (u)-[r:SENTIMENT]-(:User)
WITH u.email AS userName, p.datasetName AS dataset, sum(r.emailsSent) AS totalEmails
ORDER BY totalEmails DESC
LIMIT 5
RETURN userName, totalEmails, dataset
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

    getSentimentStats: publicProcedure.query(async ({ ctx: { neoDriver } }) => {
        // Get sentiment distribution
        const { records: distributionRecords } = await neoDriver.executeQuery(
            GET_SENTIMENT_DISTRIBUTION_QUERY,
            {},
            { routing: routing.READ },
        );

        let results = distributionRecords[0]!;
        const sentimentDistribution = {
            positive: results.get("positivePercent") as number,
            neutral: results.get("neutralPercent") as number,
            negative: results.get("negativePercent") as number,
        };

        // Get emails analysed
        const { records: totalEmailRecords } = await neoDriver.executeQuery(
            GET_TOTAL_EMAILS_QUERY,
            {},
            { routing: routing.READ },
        );

        results = totalEmailRecords[0]!;
        const emailsAnalysed = results.get("totalEmailsSent") as Integer;

        // Get chatters
        const { records: chattersRecords } = await neoDriver.executeQuery(
            GET_USERS_WHO_SENT_MANY,
            {},
            { routing: routing.READ },
        );

        results = chattersRecords[0]!;
        const chatters = results.get("chatters") as Integer;

        return {
            sentimentDistribution,
            emailsAnalysed: emailsAnalysed.toInt(),
            chatters: chatters.toInt(),
        };
    }),

    getTopCommunicators: publicProcedure.query(
        async ({ ctx: { neoDriver } }) => {
            const { records } = await neoDriver.executeQuery(
                GET_LARGEST_CHATTERS,
                {},
                { routing: routing.READ },
            );

            return records.map((rec) => ({
                name: rec.get("userName") as string,
                emails: (rec.get("totalEmails") as Integer).toInt(),
                dataset: rec.get("dataset") as string,
            }));
        },
    ),
});
