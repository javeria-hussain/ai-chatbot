interface ChatHeaderProps {
  onMinimize: () => void;
  onClose: () => void;
}

export default function ChatHeader({ onMinimize, onClose }: ChatHeaderProps) {
  return (
    <div className="chat-header">
      <span className="chat-header-title">MoinSystems AI Assistant</span>
      <div className="chat-header-actions">
        <button
          className="icon-btn"
          onClick={onMinimize}
          aria-label="Minimize chat"
        >
          &#8211;
        </button>
        <button className="icon-btn" onClick={onClose} aria-label="Close chat">
          &times;
        </button>
      </div>
    </div>
  );
}