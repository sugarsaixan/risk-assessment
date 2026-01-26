/**
 * ContactPage component - separate page for collecting contact information
 * after questionnaire completion.
 * Fields: Овог, Нэр, email, phone, Албан тушаал
 */

import { useCallback, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useAssessmentContext } from "../contexts/AssessmentContext";
import { ThemeToggle } from "../hooks/useTheme";
import { submitAssessment } from "../services/assessment";
import type { SubmissionContactInput } from "../types/api";

interface ContactFormErrors {
  last_name?: string;
  first_name?: string;
  email?: string;
  phone?: string;
  position?: string;
}

export function ContactPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();

  // Get answers and attachments from shared context
  const { answers, getAttachmentIdsForQuestion, resetState } = useAssessmentContext();

  const [contact, setContact] = useState<Partial<SubmissionContactInput>>({});
  const [errors, setErrors] = useState<ContactFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Handle field change
  const handleChange = useCallback(
    (field: keyof SubmissionContactInput, value: string) => {
      setContact((prev) => ({ ...prev, [field]: value }));
      // Clear error when user starts typing
      if (errors[field]) {
        setErrors((prev) => ({ ...prev, [field]: undefined }));
      }
    },
    [errors]
  );

  // Validate contact fields
  const validateContact = useCallback((): boolean => {
    const newErrors: ContactFormErrors = {};

    if (!contact.last_name?.trim()) {
      newErrors.last_name = "Овог оруулна уу";
    }
    if (!contact.first_name?.trim()) {
      newErrors.first_name = "Нэр оруулна уу";
    }
    if (!contact.email?.trim()) {
      newErrors.email = "И-мэйл оруулна уу";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email)) {
      newErrors.email = "И-мэйл хаяг буруу байна";
    }
    if (!contact.phone?.trim()) {
      newErrors.phone = "Утасны дугаар оруулна уу";
    } else if (!/^\d{8,15}$/.test(contact.phone.trim().replace(/[\s\-+()]/g, ""))) {
      newErrors.phone = "Утасны дугаар буруу байна";
    }
    if (!contact.position?.trim()) {
      newErrors.position = "Албан тушаал оруулна уу";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [contact]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) return;

    if (!validateContact()) {
      setSubmitError("Хариулагчийн мэдээллийг бүрэн бөглөнө үү");
      return;
    }

    // Check if we have answers from context
    const questionIds = Object.keys(answers);
    if (questionIds.length === 0) {
      setSubmitError("Асуултын хариултууд олдсонгүй. Буцаж асуултуудад хариулна уу.");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    // Build submission data with contact and answers from context
    const submitData = {
      contact: {
        last_name: contact.last_name!.trim(),
        first_name: contact.first_name!.trim(),
        email: contact.email!.trim(),
        phone: contact.phone!.trim(),
        position: contact.position!.trim(),
      },
      answers: questionIds.map((questionId) => {
        const answer = answers[questionId];
        const commentValue = answer?.comment?.trim();
        return {
          question_id: questionId,
          selected_option: answer?.selected_option || "NO",
          ...(commentValue ? { comment: commentValue } : {}),
          attachment_ids: getAttachmentIdsForQuestion(questionId),
        };
      }),
    };

    const result = await submitAssessment(token, submitData);

    setIsSubmitting(false);

    if (result.success) {
      // Clear context state after successful submission
      resetState();

      // Navigate to results page with data
      navigate(`/a/${token}/results`, {
        state: { results: result.data },
        replace: true,
      });
    } else {
      setSubmitError(result.message);

      // Handle specific errors
      if (result.error === "expired") {
        navigate("/expired", { replace: true });
      } else if (result.error === "already_completed") {
        navigate("/used", { replace: true });
      }
    }
  };

  // Handle back navigation
  const handleBack = () => {
    navigate(`/a/${token}`);
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="container-app max-w-2xl mx-auto">
        {/* Header */}
        <div className="surface-card p-6 sm:p-8 mb-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="pill mb-4">
                <svg
                  className="h-3.5 w-3.5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                Хариулагчийн мэдээлэл
              </div>
              <h1 className="text-2xl sm:text-3xl font-semibold text-[var(--foreground)]">
                Хариулагчийн мэдээлэл
              </h1>
              <p className="mt-2 text-sm label-muted">
                Үнэлгээг дуусгахын тулд доорх мэдээллийг бөглөнө үү
              </p>
            </div>
            <ThemeToggle />
          </div>
        </div>

        {/* Contact Form */}
        <form onSubmit={handleSubmit}>
          <fieldset disabled={isSubmitting} className="contents">
          <div className="surface-card p-6 mb-6">
            {isSubmitting && (
              <div className="flex items-center gap-2 mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <span className="spinner spinner-sm" />
                <span className="text-sm text-blue-400">Илгээж байна...</span>
              </div>
            )}
            <div className="grid gap-4 sm:grid-cols-2">
              {/* Last name (Овог) */}
              <div>
                <label
                  htmlFor="contact-last-name"
                  className="block text-sm font-medium text-[var(--foreground)] mb-1.5"
                >
                  Овог <span className="text-red-500">*</span>
                </label>
                <input
                  id="contact-last-name"
                  type="text"
                  value={contact.last_name || ""}
                  onChange={(e) => handleChange("last_name", e.target.value)}
                  placeholder="Овог"
                  className={`input-field ${errors.last_name ? "input-field--error" : ""}`}
                  maxLength={100}
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-500">{errors.last_name}</p>
                )}
              </div>

              {/* First name (Нэр) */}
              <div>
                <label
                  htmlFor="contact-first-name"
                  className="block text-sm font-medium text-[var(--foreground)] mb-1.5"
                >
                  Нэр <span className="text-red-500">*</span>
                </label>
                <input
                  id="contact-first-name"
                  type="text"
                  value={contact.first_name || ""}
                  onChange={(e) => handleChange("first_name", e.target.value)}
                  placeholder="Нэр"
                  className={`input-field ${errors.first_name ? "input-field--error" : ""}`}
                  maxLength={100}
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-500">{errors.first_name}</p>
                )}
              </div>

              {/* Email */}
              <div>
                <label
                  htmlFor="contact-email"
                  className="block text-sm font-medium text-[var(--foreground)] mb-1.5"
                >
                  И-мэйл <span className="text-red-500">*</span>
                </label>
                <input
                  id="contact-email"
                  type="email"
                  value={contact.email || ""}
                  onChange={(e) => handleChange("email", e.target.value)}
                  placeholder="example@mail.com"
                  className={`input-field ${errors.email ? "input-field--error" : ""}`}
                  maxLength={255}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-500">{errors.email}</p>
                )}
              </div>

              {/* Phone */}
              <div>
                <label
                  htmlFor="contact-phone"
                  className="block text-sm font-medium text-[var(--foreground)] mb-1.5"
                >
                  Утасны дугаар <span className="text-red-500">*</span>
                </label>
                <input
                  id="contact-phone"
                  type="tel"
                  value={contact.phone || ""}
                  onChange={(e) => handleChange("phone", e.target.value)}
                  placeholder="99001122"
                  className={`input-field ${errors.phone ? "input-field--error" : ""}`}
                  maxLength={50}
                />
                {errors.phone && (
                  <p className="mt-1 text-sm text-red-500">{errors.phone}</p>
                )}
              </div>

              {/* Position (Албан тушаал) - Full width */}
              <div className="sm:col-span-2">
                <label
                  htmlFor="contact-position"
                  className="block text-sm font-medium text-[var(--foreground)] mb-1.5"
                >
                  Албан тушаал <span className="text-red-500">*</span>
                </label>
                <input
                  id="contact-position"
                  type="text"
                  value={contact.position || ""}
                  onChange={(e) => handleChange("position", e.target.value)}
                  placeholder="Албан тушаал"
                  className={`input-field ${errors.position ? "input-field--error" : ""}`}
                  maxLength={200}
                />
                {errors.position && (
                  <p className="mt-1 text-sm text-red-500">{errors.position}</p>
                )}
              </div>
            </div>
          </div>

          {/* Submit error */}
          {submitError && (
            <div className="surface-card border border-[var(--risk-high)]/40 p-4 mb-6">
              <p className="text-red-400">{submitError}</p>
            </div>
          )}

          </fieldset>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              type="button"
              onClick={handleBack}
              disabled={isSubmitting}
              className="btn-secondary flex-1 sm:flex-none"
            >
              Буцах
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-cta flex-1"
            >
              {isSubmitting ? "Илгээж байна..." : "Баталгаажуулах"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ContactPage;
