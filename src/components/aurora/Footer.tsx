interface FooterProps {
  modelStatus?: string;
}

export function Footer({ modelStatus = "Não conectado" }: FooterProps) {
  return (
    <footer className="footer">
      <span>
        Modelo: <span className="status">{modelStatus}</span>
      </span>
      <span>Aurora v0.1</span>
    </footer>
  );
}
