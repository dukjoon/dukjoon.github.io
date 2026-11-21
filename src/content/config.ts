import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    pubDatetime: z.coerce.date(),
    description: z.string(),
    tags: z.array(z.string()).default(['engineering']),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
