import { and, desc, eq } from "drizzle-orm";
import z from "zod";
import { searchSchema } from "~/lib/types";
import { createTRPCRouter, protectedProcedure } from "~/server/api/trpc";
import { searchQuery } from "~/server/db/schema";

export const searchRouter = createTRPCRouter({
    addSearch: protectedProcedure
        .input(
            searchSchema.extend(
                z.object({
                    datasetName: z.string().min(1),
                }),
            ),
        )
        .mutation(async ({ ctx: { db, session }, input }) => {
            const { datasetName, ...payload } = input;

            const result = await db.insert(searchQuery).values({
                datasetName: datasetName,
                userId: session.user.id,
                payload,
            });

            return { success: result.count === 1 };
        }),
    getSearches: protectedProcedure
        .input(
            z.object({
                datasetName: z.string().min(1),
                limit: z.number().min(1).optional(),
            }),
        )
        .query(async ({ ctx: { db, session }, input }) => {
            const queries = await db.query.searchQuery.findMany({
                where: and(
                    eq(searchQuery.userId, session.user.id),
                    eq(searchQuery.datasetName, input.datasetName),
                ),
                columns: {
                    id: true,
                    payload: true,
                },
                orderBy: desc(searchQuery.createdAt),
                limit: input.limit,
            });

            return { sucess: true, data: queries };
        }),
});
