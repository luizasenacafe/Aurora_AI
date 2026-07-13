import { useState } from "react";
import { Header } from "@/components/aurora/Header";
import { ChatArea } from "@/components/aurora/ChatArea";
import { InputBar } from "@/components/aurora/InputBar";
import { Footer } from "@/components/aurora/Footer";
import { SettingsModal } from "@/components/aurora/SettingsModal";
import type { ChatMessage } from "@/components/aurora/Message";

/**
 * Página principal da Aurora.
 * Apenas estado local de interface — a lógica de IA será conectada
 * futuramente a um backend Python + LM Studio.
 */
export function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleSend = (content: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, userMessage]);

    // Placeholder visual — substituir por fetch() ao backend Python futuramente.
    setIsThinking(true);
    window.setTimeout(() => {
      setIsThinking(false);
    }, 1200);
  };

  return (
    <div className="app">
      <Header onOpenSettings={() => setIsSettingsOpen(true)} />
      <main className="main">
        <ChatArea messages={messages} isThinking={isThinking} />
        <InputBar onSend={handleSend} disabled={isThinking} />
      </main>
      <Footer modelStatus="Não conectado" />
      <SettingsModal open={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  );
}
