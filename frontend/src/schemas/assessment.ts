/**
 * Zod validation schemas for assessment form data.
 */

import { z } from "zod";

/**
 * Option type enum schema.
 */
export const optionTypeSchema = z.enum(["YES", "NO"]);

/**
 * Single answer input schema.
 */
export const answerInputSchema = z.object({
  question_id: z.string().uuid(),
  selected_option: optionTypeSchema,
  comment: z.string().max(2000).optional().nullable(),
  attachment_ids: z.array(z.string().uuid()).optional().default([]),
});

/**
 * Full assessment submission schema.
 */
export const submitRequestSchema = z.object({
  answers: z.array(answerInputSchema).min(1, "At least one answer is required"),
});

/**
 * Dynamic answer validation based on question options.
 * This validates that required fields are present based on the selected option.
 */
export function createAnswerValidator(options: {
  YES: { require_comment: boolean; require_image: boolean; comment_min_len: number };
  NO: { require_comment: boolean; require_image: boolean; comment_min_len: number };
}) {
  return z
    .object({
      question_id: z.string().uuid(),
      selected_option: optionTypeSchema,
      comment: z.string().max(2000).optional().nullable(),
      attachment_ids: z.array(z.string().uuid()).optional().default([]),
    })
    .superRefine((data, ctx) => {
      const optionConfig = options[data.selected_option];

      // Validate comment requirement
      if (optionConfig.require_comment) {
        if (!data.comment || data.comment.length < optionConfig.comment_min_len) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["comment"],
            message: `Comment required with minimum ${optionConfig.comment_min_len} characters`,
          });
        }
      }

      // Validate image requirement
      if (optionConfig.require_image) {
        if (!data.attachment_ids || data.attachment_ids.length === 0) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["attachment_ids"],
            message: "At least one image is required",
          });
        }
      }
    });
}

/**
 * Form state schema for react-hook-form.
 */
export const assessmentFormSchema = z.object({
  answers: z.record(
    z.string(), // question_id
    z.object({
      selected_option: optionTypeSchema.optional(),
      comment: z.string().max(2000).optional().nullable(),
      attachment_ids: z.array(z.string().uuid()).optional().default([]),
    })
  ),
});

export type OptionType = z.infer<typeof optionTypeSchema>;
export type AnswerInput = z.infer<typeof answerInputSchema>;
export type SubmitRequest = z.infer<typeof submitRequestSchema>;
export type AssessmentFormData = z.infer<typeof assessmentFormSchema>;
