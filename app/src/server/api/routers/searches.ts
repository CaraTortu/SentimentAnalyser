import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

export const searchRouter = createTRPCRouter({
    example: publicProcedure.query(({}) => {
        return "Hello!";
    }),
});
