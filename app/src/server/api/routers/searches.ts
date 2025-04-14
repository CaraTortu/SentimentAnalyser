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
                    saved: true,
                },
                orderBy: desc(searchQuery.createdAt),
                limit: input.limit,
            });

            return {
                sucess: true,
                data: queries.map((v) => ({
                    ...v.payload,
                    id: v.id,
                    saved: v.saved,
                })),
            };
        }),
    getSavedSearches: protectedProcedure
        .input(
            z.object({
                datasetName: z.string().min(1),
            }),
        )
        .query(async ({ ctx: { db, session }, input }) => {
            const queries = await db.query.searchQuery.findMany({
                where: and(
                    eq(searchQuery.userId, session.user.id),
                    eq(searchQuery.datasetName, input.datasetName),
                    eq(searchQuery.saved, true),
                ),
                columns: {
                    id: true,
                    payload: true,
                    saved: true,
                },
                orderBy: desc(searchQuery.savedAt),
            });

            return {
                sucess: true,
                data: queries.map((v) => ({
                    ...v.payload,
                    id: v.id,
                    saved: v.saved,
                })),
            };
        }),
    saveSearch: protectedProcedure
        .input(
            z.object({
                saved: z.boolean(),
                id: z.uuid(),
            }),
        )
        .mutation(async ({ ctx: { session, db }, input }) => {
            const result = await db
                .update(searchQuery)
                .set({
                    saved: input.saved,
                    savedAt: new Date(),
                })
                .where(
                    and(
                        eq(searchQuery.userId, session.user.id),
                        eq(searchQuery.id, input.id),
                    ),
                );

            const updatedValue = result.count === 1;

            return {
                success: updatedValue,
                reason: !updatedValue
                    ? "Query with that ID does not exist"
                    : undefined,
            };
        }),
});
