export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
}

interface MessageProps {
  message: ChatMessage;
}

export function Message({ message }: MessageProps) {
  return (
    <div className={`msg-row ${message.role}`}>
      <div className={`bubble ${message.role}`}>{message.content}</div>
    </div>
  );
}
