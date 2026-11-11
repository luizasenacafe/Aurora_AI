# Privacy and security boundaries

Betelgeuse makes inference location explicit. It does not promise absolute privacy or independently audited security.

## Local mode

Chat requests go directly to the selected loopback LM Studio endpoint. They do not pass through the Betelgeuse gateway. Website loading, application downloads, and model downloads involve external infrastructure. Browser extensions, local malware, operating-system access, and LM Studio logging remain outside the app's control.

## Remote mode

The selected server receives prompts, instructions, and included history. Trust that server's operator. HTTPS protects transport, but the tunnel provider participates in transport and the site host serves client code. Remote use should not be described as "100% private."

The gateway does not intentionally log prompt bodies, response bodies, or tokens. Upstream software and infrastructure have their own logging behavior. Jobs and responses are temporarily held in gateway memory.

## Credentials and data

- Gateway keys are random bearer credentials; possession grants their access.
- The server stores SHA-256 verifiers and administrative labels, not raw issued keys.
- Revoke keys through the local panel; never share screenshots containing them.
- Browser keys remain in tab memory. Desktop tokens are session-only; desktop history and profiles persist locally.
- Desktop profiles are not secure accounts. The app does not encrypt local databases.
- Web model output is rendered as text. The app does not offer autonomous tool execution.

## Excluded from Git

Personal keys, environment secrets, active tunnel URLs, private configuration, conversation databases, operational logs, model weights, and hosting credentials are excluded. The configuration example uses placeholders. Public site URLs in source are allowlist entries, not credentials.

The unsigned installer, external dependencies, and model weights have separate trust and licensing considerations. Tests are not a penetration test or production security audit.
