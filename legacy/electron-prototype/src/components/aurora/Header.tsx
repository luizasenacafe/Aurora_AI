import { Settings } from "lucide-react";

interface HeaderProps {
  onOpenSettings: () => void;
}

export function Header({ onOpenSettings }: HeaderProps) {
  return (
    <header className="header">
      <div>
        <h1>Aurora</h1>
        <div className="subtitle">Assistente Local</div>
      </div>
      <button
        type="button"
        className="icon-btn"
        onClick={onOpenSettings}
        aria-label="Abrir configurações"
      >
        <Settings size={20} />
      </button>
    </header>
  );
}
