# Betelgeuse web client

This directory is the complete static website snapshot, including artwork and installer download parts. There is no npm build step. Serve it over HTTP with the command in the root README; do not open `index.html` as a local file.

`app.js` handles local/remote connections and tab-only conversations. `style.css` contains base layout, `stellar.css` adds the red-star background and translucent surfaces, and `download.js` checks and combines installer parts from `downloads/manifest.json`.

The application UI is Brazilian Portuguese. English project documentation is in `../docs/`. Credentials are entered at runtime, never bundled. The website's origin must be allowed by the remote gateway. Hosting-account configuration is intentionally excluded from this public snapshot.
