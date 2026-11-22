import { defineCollection, z } from 'astro:content';
import { CATEGORY_IDS } from '../constants/categories';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    pubDatetime: z.coerce.date(),
    description: z.string(),
    category: z.enum(CATEGORY_IDS).default('ai-engineering'),
    tags: z.array(z.string()).default(['engineering']),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
