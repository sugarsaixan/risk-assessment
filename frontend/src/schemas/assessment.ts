/**
 * Zod validation schemas for assessment form data.
 */

import { z } from "zod";

/**
 * Option type enum schema.
 */
export const optionTypeSchema = z.enum(["YES", "NO"]);

/**
 * Submission contact input schema for form validation.
 * Validates contact info: Овог, Нэр, email, phone, Албан тушаал
 */
export const submissionContactInputSchema = z.object({
  last_name: z
    .string()
    .min(1, "Овог оруулна уу")
    .max(100, "Овог 100-с илүүгүй тэмдэгт байх ёстой"),
  first_name: z
    .string()
    .min(1, "Нэр оруулна уу")
    .max(100, "Нэр 100-с илүүгүй тэмдэгт байх ёстой"),
  email: z
    .string()
    .min(1, "И-мэйл оруулна уу")
    .email("И-мэйл хаяг буруу байна"),
  phone: z
    .string()
    .min(1, "Утасны дугаар оруулна уу")
    .max(50, "Утасны дугаар 50-с илүүгүй тэмдэгт байх ёстой"),
  position: z
    .string()
    .min(1, "Албан тушаал оруулна уу")
    .max(200, "Албан тушаал 200-с илүүгүй тэмдэгт байх ёстой"),
});

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
 * Full assessment submission schema with contact info.
 */
export const submitRequestSchema = z.object({
  contact: submissionContactInputSchema,
  answers: z.array(answerInputSchema).min(1, "Дор хаяж нэг асуултанд хариулна уу"),
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
            message: `Тайлбар дор хаяж ${optionConfig.comment_min_len} тэмдэгт байх ёстой`,
          });
        }
      }

      // Validate image requirement
      if (optionConfig.require_image) {
        if (!data.attachment_ids || data.attachment_ids.length === 0) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["attachment_ids"],
            message: "Дор хаяж нэг зураг оруулна уу",
          });
        }
      }
    });
}

/**
 * Form state schema for react-hook-form.
 * Includes both contact info and answers.
 */
export const assessmentFormSchema = z.object({
  contact: submissionContactInputSchema,
  answers: z.record(
    z.string(), // question_id
    z.object({
      selected_option: optionTypeSchema.optional(),
      comment: z.string().max(2000).optional().nullable(),
      attachment_ids: z.array(z.string().uuid()).optional().default([]),
    })
  ),
});

// Type exports
export type OptionType = z.infer<typeof optionTypeSchema>;
export type SubmissionContactInput = z.infer<typeof submissionContactInputSchema>;
export type AnswerInput = z.infer<typeof answerInputSchema>;
export type SubmitRequest = z.infer<typeof submitRequestSchema>;
export type AssessmentFormData = z.infer<typeof assessmentFormSchema>;
