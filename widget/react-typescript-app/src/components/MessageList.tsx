import ReactMarkdown from "react-markdown";
import type{ ChatMessage } from "../types";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  onRetry?: () => void;
}

function formatTime(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function MessageList({
  messages,
  isLoading,
  error,
  onRetry,
}: MessageListProps) {
  return (
    <div className="message-list" role="log" aria-live="polite">
      {messages.length === 0 && !isLoading && (
        <div className="empty-state">Send a message to get started.</div>
      )}

      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`message message-${msg.role}`}
          aria-label={msg.role === "user" ? "You said" : "Assistant said"}
        >
          <div className="message-bubble">
            {msg.role === "assistant" ? (
              <div className="markdown-content">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            ) : (
              msg.content
            )}
            <span className="message-time">{formatTime(msg.timestamp)}</span>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message message-assistant">
          <div className="message-bubble message-loading">Typing...</div>
        </div>
      )}

      {error && (
        <div className="message-error" role="alert">
          <span>{error}</span>
          {onRetry && (
            <button className="retry-btn" onClick={onRetry}>
              Retry
            </button>
          )}
        </div>
      )}
    </div>
  );
}
