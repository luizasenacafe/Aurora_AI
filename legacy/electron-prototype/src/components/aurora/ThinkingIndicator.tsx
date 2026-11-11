export function ThinkingIndicator() {
  return (
    <div className="msg-row assistant" aria-live="polite">
      <div className="thinking">
        <span>Aurora está pensando</span>
        <span className="dots">
          <span className="dot" />
          <span className="dot" />
          <span className="dot" />
        </span>
      </div>
    </div>
  );
}
