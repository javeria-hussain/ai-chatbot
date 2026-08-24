import { useState, type SubmitEvent } from "react";

interface ComposerProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

export default function Composer({ onSend, disabled }: ComposerProps) {
  const [text, setText] = useState("");

  const handleSubmit = (e: SubmitEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <input
        type="text"
        className="composer-input"
        placeholder="Type a message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        aria-label="Chat message"
      />
      <button
        type="submit"
        className="composer-send"
        disabled={disabled || !text.trim()}
        aria-label="Send message"
      >
        Send
      </button>
    </form>
  );
}