import { useEffect, useRef } from "react";
import { Message, type ChatMessage } from "./Message";
import { ThinkingIndicator } from "./ThinkingIndicator";

interface ChatAreaProps {
  messages: ChatMessage[];
  isThinking: boolean;
}

export function ChatArea({ messages, isThinking }: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isThinking]);

  const isEmpty = messages.length === 0 && !isThinking;

  return (
    <div className="chat">
      <div className="chat-inner">
        {isEmpty ? (
          <div className="empty">
            <h2>Olá, eu sou a Aurora</h2>
            <p>
              Sua assistente de inteligência artificial local. Envie uma mensagem
              abaixo para começar.
            </p>
          </div>
        ) : (
          messages.map((m) => <Message key={m.id} message={m} />)
        )}
        {isThinking && <ThinkingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
