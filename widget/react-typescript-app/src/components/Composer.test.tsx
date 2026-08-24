import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Composer from "./Composer";

describe("Composer", () => {
  it("calls onSend with typed text when submitted", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<Composer onSend={onSend} disabled={false} />);

    const input = screen.getByLabelText("Chat message");
    await user.type(input, "Hello there");
    await user.click(screen.getByRole("button", { name: "Send message" }));

    expect(onSend).toHaveBeenCalledWith("Hello there");
  });

  it("clears the input after sending", async () => {
    const user = userEvent.setup();
    render(<Composer onSend={vi.fn()} disabled={false} />);

    const input = screen.getByLabelText("Chat message") as HTMLInputElement;
    await user.type(input, "test message");
    await user.click(screen.getByRole("button", { name: "Send message" }));

    expect(input.value).toBe("");
  });

  it("does not call onSend when input is empty", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<Composer onSend={onSend} disabled={false} />);

    await user.click(screen.getByRole("button", { name: "Send message" }));

    expect(onSend).not.toHaveBeenCalled();
  });

  it("disables input and button when disabled prop is true", () => {
    render(<Composer onSend={vi.fn()} disabled={true} />);

    expect(screen.getByLabelText("Chat message")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Send message" })).toBeDisabled();
  });
});
