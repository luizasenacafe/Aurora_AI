# Architecture and API

## Responsibilities

Web and desktop are clients. LM Studio owns downloading, loading, and inference. The gateway adds authentication, validation, and scheduling around an OpenAI-compatible upstream API.

The desktop uses Qt widgets, custom spatial visuals, and SQLite. Its profiles are organizational containers, not independently authenticated accounts. The browser holds state in memory and renders model output as plain text.

`panel.py` manages keys locally. `manage.py` supervises the API and optional tunnel process, reports status, and supports Windows-login startup. Administration is not exposed through public HTTP routes.

## Routes

All listed `/v1` routes require `Authorization: Bearer <individual-key>`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Public minimal liveness; not full inference health |
| GET | `/v1/models` | Permitted chat models; known embedding names filtered |
| GET | `/v1/aurora/info` | Job protocol discovery |
| POST | `/v1/aurora/jobs` | Submit and receive job ID |
| GET | `/v1/aurora/jobs/{id}` | Poll caller-owned job |
| POST | `/v1/chat/completions` | Non-streaming compatible chat response |

Historical Aurora route names remain for compatibility. Example request body:

```json
{
  "model": "your-loaded-chat-model",
  "messages": [{"role": "user", "content": "Explain red supergiant stars."}],
  "temperature": 0.7,
  "max_tokens": 256,
  "stream": false
}
```

Jobs move through `queued`, `running`, and `done` or `error`. The web client polls about every two seconds. This avoids a single long HTTPS request; it does not speed up inference. Stopping the browser wait does not cancel server generation.

## Boundaries

Defaults: one concurrent inference, up to eight pending jobs, one pending job per key, and 30 submissions/model-list requests per minute per key. Validation limits body size, message count, aggregate context, temperature, and requested output tokens. A model can impose lower limits.

Completed jobs expire after roughly ten minutes, with periodic cleanup and a count limit. Jobs and rate counters are in-memory. Run one gateway worker: queues are not coordinated across processes or machines.

| Data | Location |
| --- | --- |
| Browser chat, instructions, key | Tab memory |
| Desktop profiles, history, lists | Local SQLite in `%LOCALAPPDATA%\AuroraAI` |
| Key verifiers and administrative labels | Private SQLite in `%LOCALAPPDATA%\AuroraServer` |
| Jobs and responses | Temporary gateway memory |
| Model files | LM Studio |

The tunnel forwards HTTPS to the loopback gateway, which calls local LM Studio. CORS supplements authentication, never replaces it. Explicit `web_origins` replaces the built-in allowlist. Static hosting and inference are independently deployed.
