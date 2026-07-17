import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const projects = defineCollection({
  loader: glob({ pattern: "**/*.json", base: "./src/data/projects" }),
  schema: z.object({
    order: z.number().int().positive(),
    title: z.string().min(1),
    client: z.string().optional().default(""),
    year: z.number().int().min(2000).max(2100).default(2026),
    type: z.string().min(1),
    description: z.string().min(1),
    visual: z.enum(["brand", "signal", "story"]).default("brand"),
    mediaFit: z.enum(["cover", "contain"]).default("cover"),
    published: z.boolean().default(true),
    image: z.string().optional().default(""),
    video: z.string().optional().default(""),
    poster: z.string().optional().default(""),
    clips: z.array(z.object({
      title: z.string().min(1),
      video: z.string().min(1),
      poster: z.string().optional().default(""),
      alt: z.string().optional().default(""),
    })).max(6).optional().default([]),
    showcase: z.array(z.object({
      title: z.string().min(1),
      label: z.string().optional().default(""),
      image: z.string().optional().default(""),
      video: z.string().optional().default(""),
      poster: z.string().optional().default(""),
      alt: z.string().optional().default(""),
    })).max(8).optional().default([]),
    alt: z.string().optional().default(""),
    link: z.string().optional().default(""),
  }),
});

export const collections = { projects };
