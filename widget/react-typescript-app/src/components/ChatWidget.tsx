import { useState, useEffect, useRef } from "react";
import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import Composer from "./Composer";
import LeadCaptureForm from "./LeadCaptureForm";
import type { ChatMessage } from "../types";
import { startSession, sendMessage } from "../api/client";
import "../ChatWidget.css";

const SESSION_STORAGE_KEY = "moinsystems_chat_session_id";

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isSessionReady, setIsSessionReady] = useState(false);
  const [leadCaptureRequired, setLeadCaptureRequired] = useState(false);
  const [missingLeadFields, setMissingLeadFields] = useState<string[]>([]);
  const [leadSubmitted, setLeadSubmitted] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(
    null,
  );

  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsOpen(false);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && panelRef.current) {
      panelRef.current.focus();
    }
  }, [isOpen]);

  const ensureSession = async () => {
    const existing = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (existing) {
      setSessionId(existing);
      setIsSessionReady(true);
      return;
    }

    try {
      const res = await startSession(window.location.pathname);
      sessionStorage.setItem(SESSION_STORAGE_KEY, res.session_id);
      setSessionId(res.session_id);
      setIsSessionReady(true);
    } catch (err) {
      setError("Could not start chat session. Please try again.");
      console.error("Session init failed:", err);
    }
  };

  const handleOpen = () => {
    setIsOpen(true);
    setIsMinimized(false);
    if (!isSessionReady) {
      ensureSession();
    }
  };

  const handleSend = async (text: string) => {
    if (!sessionId || isLoading) return;

    setError(null);
    setLastFailedMessage(null);
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await sendMessage(sessionId, text);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.answer,
          timestamp: Date.now(),
        },
      ]);
      if (res.lead_capture_required && !res.lead_submitted) {
        setLeadCaptureRequired(true);
        setMissingLeadFields(res.missing_lead_fields);
      } else {
        setLeadCaptureRequired(false);
      }
      if (res.lead_submitted) {
        setLeadSubmitted(true);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Message could not be sent.",
      );
      setLastFailedMessage(text);
      console.error("Send message failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastFailedMessage) {
      const textToRetry = lastFailedMessage;
      setMessages((prev) =>
        prev.filter((m) => m.content !== textToRetry || m.role !== "user"),
      );
      handleSend(textToRetry);
    }
  };

  if (!isOpen) {
    return (
      <button
        className="chat-launcher"
        onClick={handleOpen}
        aria-label="Open chat"
      >
        Chat
      </button>
    );
  }

  return (
    <div
      ref={panelRef}
      tabIndex={-1}
      className={`chat-panel ${isMinimized ? "chat-panel-minimized" : ""}`}
      role="dialog"
      aria-label="Chat with MoinSystems AI Assistant"
    >
      <ChatHeader
        onMinimize={() => setIsMinimized((m) => !m)}
        onClose={() => setIsOpen(false)}
      />
      {!isMinimized && (
        <>
          <MessageList
            messages={messages}
            isLoading={isLoading}
            error={error}
            onRetry={lastFailedMessage ? handleRetry : undefined}
          />
          <Composer
            onSend={handleSend}
            disabled={isLoading || !isSessionReady}
          />
          {leadCaptureRequired && !leadSubmitted && sessionId && (
            <LeadCaptureForm
              sessionId={sessionId}
              missingFields={missingLeadFields}
              onSuccess={() => {
                setLeadCaptureRequired(false);
                setLeadSubmitted(true);
                setMessages((prev) => [
                  ...prev,
                  {
                    id: crypto.randomUUID(),
                    role: "assistant",
                    content:
                      "Thanks! We've received your details and will be in touch soon.",
                    timestamp: Date.now(),
                  },
                ]);
              }}
            />
          )}
        </>
      )}
    </div>
  );
}
