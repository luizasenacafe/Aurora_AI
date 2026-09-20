# Betelgeuse A.I. — IA local e privada

Aplicação desktop para executar modelos de IA localmente, com foco em privacidade e controle dos dados. O repositório preserva a primeira interface Electron e agora inclui a implementação Python atual, conectada ao LM Studio e preparada para uso local ou por servidor HTTPS privado.

## 📁 Estrutura

```
aurora-ai/
├─ electron/
│  ├─ main.cjs         # Processo principal do Electron
│  └─ preload.cjs      # Ponte segura React ↔ Node
├─ public/
│  └─ aurora.svg       # Ícone
├─ src/
│  ├─ components/aurora/
│  │  ├─ Header.tsx
│  │  ├─ ChatArea.tsx
│  │  ├─ Message.tsx
│  │  ├─ InputBar.tsx
│  │  ├─ ThinkingIndicator.tsx
│  │  ├─ Footer.tsx
│  │  └─ SettingsModal.tsx
│  ├─ pages/
│  │  └─ Home.tsx
│  ├─ styles/
│  │  └─ globals.css
│  └─ main.tsx
├─ index.html
├─ vite.config.ts
├─ tsconfig.json
└─ package.json
```

## 🚀 Como rodar

### 1. Instalar dependências
```bash
npm install
```

### 2. Rodar em modo desenvolvimento (browser)
```bash
npm run dev
```
Abre em http://localhost:5173

### 3. Rodar como app Electron (dev)
```bash
npm run electron:dev
```

### 4. Gerar o executável `.exe` (Windows)
```bash
npm run electron:build
```
O instalador aparecerá em `release/`.

Alternativa mais leve (pasta portátil, sem instalador):
```bash
npm run electron:pack
```
Saída em `release/Aurora-win32-x64/Aurora.exe`.

## 🌐 GitHub Pages (opcional)

Como o Vite está configurado com `base: './'`, os arquivos gerados em
`dist/` também funcionam em **GitHub Pages**. Basta:

```bash
npm run build
```
E publicar o conteúdo de `dist/` na branch `gh-pages` (ou usar uma action).

## 🔌 Próximos passos (backend Python)

Em `src/pages/Home.tsx`, substituir o `setTimeout` dentro de `handleSend`
por uma chamada real ao backend, por exemplo:

```ts
const res = await fetch("http://127.0.0.1:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: content }),
});
const data = await res.json();
setMessages((prev) => [
  ...prev,
  { id: crypto.randomUUID(), role: "assistant", content: data.reply },
]);
setIsThinking(false);
```

## 📝 Licença
MIT


## Betelgeuse A.I. — implementação atual

A pasta [`betelgeuse-python/`](betelgeuse-python/) contém a versão atual do projeto: interface espacial em Python/PySide6, conexão com modelos carregados no LM Studio, perfis de conversa, API Python para servidor privado, autenticação por token e tutorial de primeiro acesso.

A Betelgeuse foi criada para que prompts e conversas possam permanecer no computador da pessoa ou no servidor escolhido, sem depender de APIs de grandes plataformas. Consulte [`betelgeuse-python/LEIA-ME.md`](betelgeuse-python/LEIA-ME.md) para executar a versão local.
