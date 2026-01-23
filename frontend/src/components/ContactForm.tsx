/**
 * ContactForm component for collecting submission contact information.
 * Fields: Овог, Нэр, email, phone, Албан тушаал
 */

import type { SubmissionContactInput } from "../types/api";

interface ContactFormProps {
  /** Current contact data */
  value: Partial<SubmissionContactInput>;
  /** Callback when contact data changes */
  onChange: (field: keyof SubmissionContactInput, value: string) => void;
  /** Validation errors by field */
  errors?: Partial<Record<keyof SubmissionContactInput, string>>;
  /** Optional CSS class names */
  className?: string;
}

export function ContactForm({
  value,
  onChange,
  errors = {},
  className = "",
}: ContactFormProps) {
  return (
    <div className={`surface-card p-6 ${className}`}>
      <h2 className="text-lg font-medium text-[var(--foreground)] mb-6">
        Хариулагчийн мэдээлэл
      </h2>

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
            value={value.last_name || ""}
            onChange={(e) => onChange("last_name", e.target.value)}
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
            value={value.first_name || ""}
            onChange={(e) => onChange("first_name", e.target.value)}
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
            value={value.email || ""}
            onChange={(e) => onChange("email", e.target.value)}
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
            value={value.phone || ""}
            onChange={(e) => onChange("phone", e.target.value)}
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
            value={value.position || ""}
            onChange={(e) => onChange("position", e.target.value)}
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
  );
}

export default ContactForm;
