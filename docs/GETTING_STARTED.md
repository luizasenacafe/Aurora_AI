# Getting started

## Requirements

Python 3.11+ (local checks use 3.13), LM Studio with a chat model for real inference, and Windows 10/11 x64 for the packaged desktop and Windows supervisor. Node.js is only needed for JavaScript checks or the archived Electron prototype. The current web client has no npm build step.

Model weights are not included. Download and load a model in LM Studio and start its local API. Examples use `http://127.0.0.1:1234/v1`.

## Web interface

From the repository root:

```sh
python -m http.server 8766 --bind 127.0.0.1 --directory web
```

Open `http://127.0.0.1:8766`, rather than opening the HTML file directly.

**Local mode (experimental):** Run LM Studio on the browser's computer, enable its CORS support, configure authentication, and keep LAN serving disabled for same-computer use. Choose **Seu PC. Suas regras.**, enter the loopback endpoint and required key, test, select a model, and confirm. Browser local-network permissions and HTTPS-to-local restrictions vary. If blocked, use the desktop client; there is no automatic fallback to remote inference.

**Remote mode:** Obtain the current HTTPS endpoint and individual key from the operator. Choose **Servidor da Betelgeuse**, paste the endpoint ending in `/v1` and the key, test, select a model, and confirm. The gateway must allow the website's exact origin. Reloading the page clears its connection and conversation.

## Desktop from source

In PowerShell, from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r betelgeuse-python/source/requirements.txt
.\.venv\Scripts\python.exe betelgeuse-python/source/aurora.py
```

Configure a local LM Studio endpoint or authenticated gateway in settings. The included CMD launchers use `pythonw` from PATH; the explicit commands above select the virtual environment reliably.

The Windows 0.4.0 installer is in GitHub Releases and the website's desktop download page. It includes the desktop runtime but no models. It is unsigned; Windows can warn or block according to policy. Do not disable system protections to run it.

## Gateway and control panel

Install the desktop requirements above for the graphical panel, then:

```powershell
.\.venv\Scripts\python.exe -m pip install -r betelgeuse-python/server/requirements.txt
.\.venv\Scripts\python.exe betelgeuse-python/server/panel.py
```

Click **Ligar API + HTTPS**. The supervisor downloads the official Windows `cloudflared` binary and verifies its published SHA-256 digest. Create one access per client; raw keys are shown only when issued. Copy the current HTTPS endpoint, appending `/v1` if needed. Revoke keys in the panel.

For API-only development without a tunnel:

```powershell
.\.venv\Scripts\python.exe betelgeuse-python/server/api.py
```

The gateway binds to configured loopback, normally port 8787. Do not expose the LM Studio port to the internet. The supervisor is Windows-oriented. For API-only development elsewhere, set `AURORA_SERVER_DATA` to a private writable directory.

### Configuration

The gateway creates `%LOCALAPPDATA%\AuroraServer\config.json`. See [the non-secret example](../examples/server-config.example.json). Set `web_origins` to exact website origins, without `/v1`, and restart after editing.

If LM Studio requires authentication, supply `AURORA_LM_TOKEN` in the gateway environment. It is separate from client gateway keys. `AURORA_SERVER_DATA` overrides the state directory. Do not commit either credentials or local state.

Optional auto-start runs after Windows login; it is not a system service. Closing the panel leaves the supervisor running; use **Parar servidor** to stop it. Sleep, power loss, network outages, and model availability interrupt access. Temporary tunnels do not provide an uptime guarantee.

## Windows build

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --distpath build/desktop --workpath build/pyinstaller betelgeuse-python/source/Aurora.spec
```

Install Inno Setup and compile `packaging/Betelgeuse.iss` using `ISCC.exe`. It reads `build/desktop/BetelgeuseAI.exe` and writes `build/installer/Betelgeuse-Setup.exe`. The archived 0.4.0 installer predates this repository refresh; rebuilding is not guaranteed to be byte-identical.

## Web hosting

Publish the contents of `web/`, including assets and downloads. The bundled installer is split into parts for the host's per-file limits; `download.js` verifies and combines them. Those parts are included for a complete static snapshot.

The website URL and inference endpoint are independent. After changing the website domain, update the gateway's `web_origins`. A website URL is not an API endpoint.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Unauthorized / 401 | Correct gateway key, not revoked |
| Browser fails but desktop works | Exact origin in `web_origins`; restart API |
| Empty model list | Chat model available; embeddings are filtered |
| Slow response | Hardware, model size, queue position |
| Old HTTPS link stops working | Current tunnel address after restart |
| Local browser connection blocked | CORS and local-network permissions |
| Chat disappears on refresh | Expected tab-only browser history |
