import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LeadCaptureForm from "./LeadCaptureForm";
import * as apiClient from "../api/client";

vi.mock("../api/client", () => ({
  submitLead: vi.fn(),
}));

describe("LeadCaptureForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows validation errors and does not call the API when fields are empty", async () => {
    const user = userEvent.setup();
    render(
      <LeadCaptureForm
        sessionId="test-session"
        missingFields={["name", "email", "phone"]}
        onSuccess={vi.fn()}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Submit" }));

    expect(
      screen.getByText("Please enter your full name."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Please enter a valid email address."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Please enter a valid phone number."),
    ).toBeInTheDocument();
    expect(apiClient.submitLead).not.toHaveBeenCalled();
  });

  it("shows an error for invalid email format only", async () => {
    const user = userEvent.setup();
    render(
      <LeadCaptureForm
        sessionId="test-session"
        missingFields={["email"]}
        onSuccess={vi.fn()}
      />,
    );

    await user.type(screen.getByLabelText("Email"), "notanemail");
    await user.click(screen.getByRole("button", { name: "Submit" }));

    expect(
      screen.getByText("Please enter a valid email address."),
    ).toBeInTheDocument();
    expect(apiClient.submitLead).not.toHaveBeenCalled();
  });

  it("calls submitLead and onSuccess when submission succeeds", async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    vi.mocked(apiClient.submitLead).mockResolvedValue({
      success: true,
      status: "complete",
      errors: {},
    });

    render(
      <LeadCaptureForm
        sessionId="test-session"
        missingFields={["email"]}
        onSuccess={onSuccess}
      />,
    );

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Submit" }));

    expect(apiClient.submitLead).toHaveBeenCalledWith({
      session_id: "test-session",
      email: "test@example.com",
    });
    expect(onSuccess).toHaveBeenCalledOnce();
  });

  it("shows backend field errors when submission fails", async () => {
    const user = userEvent.setup();
    vi.mocked(apiClient.submitLead).mockResolvedValue({
      success: false,
      status: "draft",
      errors: { email: "This email is already registered." },
    });

    render(
      <LeadCaptureForm
        sessionId="test-session"
        missingFields={["email"]}
        onSuccess={vi.fn()}
      />,
    );

    await user.type(screen.getByLabelText("Email"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Submit" }));

    expect(
      await screen.findByText("This email is already registered."),
    ).toBeInTheDocument();
  });
});
