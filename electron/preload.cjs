// Preload script — ponte segura entre o processo principal e o React.
// Por enquanto vazio; será usado futuramente para expor o backend Python.
const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("aurora", {
  version: "0.1.0",
});
