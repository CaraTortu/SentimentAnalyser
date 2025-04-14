import z from "zod";

export const searchSchema = z.object({
    limit: z.number().min(1),
    emailSearch: z.string().min(4),
    emailsEndWith: z.string(),
});

export type QueryPayload = z.infer<typeof searchSchema>;
