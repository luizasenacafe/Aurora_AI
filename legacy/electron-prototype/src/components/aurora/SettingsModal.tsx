import { useEffect } from "react";
import { X } from "lucide-react";

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
}

export function SettingsModal({ open, onClose }: SettingsModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
      onClick={onClose}
    >
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2 id="settings-title">Configurações</h2>
            <p>Interface visual — nenhuma alteração é aplicada.</p>
          </div>
          <button
            type="button"
            className="icon-btn"
            onClick={onClose}
            aria-label="Fechar configurações"
          >
            <X size={16} />
          </button>
        </div>

        <div className="field">
          <label htmlFor="theme-select">Tema</label>
          <select id="theme-select" defaultValue="dark">
            <option value="dark">Escuro</option>
            <option value="light">Claro</option>
            <option value="system">Sistema</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="model-path">Caminho do modelo</label>
          <input
            id="model-path"
            type="text"
            placeholder="C:\\models\\seu-modelo.gguf"
          />
        </div>

        <div className="info-box">
          <div><span className="strong">Aurora</span> — Assistente de IA local</div>
          <div>Versão 0.1.0</div>
          <div>Executa localmente via backend Python + LM Studio.</div>
        </div>

        <div className="modal-actions">
          <button type="button" className="btn" onClick={onClose}>Cancelar</button>
          <button type="button" className="btn primary" onClick={onClose}>Salvar</button>
        </div>
      </div>
    </div>
  );
}
