import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import MessageList from "./MessageList";
import type{ ChatMessage } from "../types";

const sampleMessages: ChatMessage[] = [
  { id: "1", role: "user", content: "Hi there", timestamp: Date.now() },
  {
    id: "2",
    role: "assistant",
    content: "**Hello!** How can I help?",
    timestamp: Date.now(),
  },
];

describe("MessageList", () => {
  it("shows empty state when there are no messages", () => {
    render(<MessageList messages={[]} isLoading={false} error={null} />);
    expect(
      screen.getByText("Send a message to get started."),
    ).toBeInTheDocument();
  });

  it("renders user and assistant messages", () => {
    render(
      <MessageList messages={sampleMessages} isLoading={false} error={null} />,
    );
    expect(screen.getByText("Hi there")).toBeInTheDocument();
    expect(screen.getByText("Hello!")).toBeInTheDocument();
  });

  it("shows typing indicator when isLoading is true", () => {
    render(<MessageList messages={[]} isLoading={true} error={null} />);
    expect(screen.getByText("Typing...")).toBeInTheDocument();
  });

  it("shows error message and retry button when error and onRetry are provided", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(
      <MessageList
        messages={[]}
        isLoading={false}
        error="Network error. Please check your connection."
        onRetry={onRetry}
      />,
    );

    expect(
      screen.getByText("Network error. Please check your connection."),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("does not show retry button when onRetry is not provided", () => {
    render(
      <MessageList messages={[]} isLoading={false} error="Something failed" />,
    );
    expect(
      screen.queryByRole("button", { name: "Retry" }),
    ).not.toBeInTheDocument();
  });
});
