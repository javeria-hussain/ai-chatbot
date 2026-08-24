import { useState, type FormEvent } from "react";
import { submitLead } from "../api/client";


interface LeadCaptureFormProps {
  sessionId: string;
  missingFields: string[];
  onSuccess: () => void;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_REGEX = /^[+\d][\d\s-]{6,}$/;

export default function LeadCaptureForm({
  sessionId,
  missingFields,
  onSuccess,
}: LeadCaptureFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);

  const needsName = missingFields.includes("name");
  const needsEmail = missingFields.includes("email");
  const needsPhone = missingFields.includes("phone");

  const validateClientSide = (): Record<string, string> => {
    const errors: Record<string, string> = {};
    if (needsName && name.trim().length < 2) {
      errors.name = "Please enter your full name.";
    }
    if (needsEmail && !EMAIL_REGEX.test(email.trim())) {
      errors.email = "Please enter a valid email address.";
    }
    if (needsPhone && !PHONE_REGEX.test(phone.trim())) {
      errors.phone = "Please enter a valid phone number.";
    }
    return errors;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;

    setFormError(null);
    const clientErrors = validateClientSide();
    if (Object.keys(clientErrors).length > 0) {
      setFieldErrors(clientErrors);
      return;
    }
    setFieldErrors({});
    setIsSubmitting(true);

    try {
      const res = await submitLead({
        session_id: sessionId,
        ...(needsName && { name }),
        ...(needsEmail && { email }),
        ...(needsPhone && { phone }),
      });

      if (res.success) {
        onSuccess();
      } else {
        setFieldErrors(res.errors ?? {});
        setFormError("Please check the highlighted fields and try again.");
      }
    } catch (err) {
      setFormError("Could not submit your details. Please try again.");
      console.error("Lead submit failed:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="lead-form" onSubmit={handleSubmit} noValidate>
      <p className="lead-form-title">
        Share your contact details and we'll follow up:
      </p>

      {needsName && (
        <label className="lead-form-field">
          <span>Name</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={isSubmitting}
            aria-invalid={!!fieldErrors.name}
            aria-describedby={fieldErrors.name ? "lead-name-error" : undefined}
          />
          {fieldErrors.name && (
            <span className="lead-field-error" id="lead-name-error" role="alert">
              {fieldErrors.name}
            </span>
          )}
        </label>
      )}

      {needsEmail && (
        <label className="lead-form-field">
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isSubmitting}
            aria-invalid={!!fieldErrors.email}
            aria-describedby={fieldErrors.email ? "lead-email-error" : undefined}
          />
          {fieldErrors.email && (
            <span className="lead-field-error" id="lead-email-error" role="alert">
              {fieldErrors.email}
            </span>
          )}
        </label>
      )}

      {needsPhone && (
        <label className="lead-form-field">
          <span>Phone</span>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            disabled={isSubmitting}
            aria-invalid={!!fieldErrors.phone}
            aria-describedby={fieldErrors.phone ? "lead-phone-error" : undefined}
          />
          {fieldErrors.phone && (
            <span className="lead-field-error" id="lead-phone-error" role="alert">
              {fieldErrors.phone}
            </span>
          )}
        </label>
      )}

      {formError && (
        <div className="lead-form-error" role="alert">
          {formError}
        </div>
      )}

      <button type="submit" className="lead-form-submit" disabled={isSubmitting}>
        {isSubmitting ? "Submitting..." : "Submit"}
      </button>
    </form>
  );
}