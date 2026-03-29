// src/lib/api.js
// All HTTP calls to the AI microservice go through here.
// Reads the AI service URL from environment variables.

const AI_BASE = import.meta.env.VITE_AI_SERVICE_URL;

// Send handwriting image, get back raw recognized text
export async function recognizeHandwriting(base64Image) {
  const res = await fetch(`${AI_BASE}/api/handwriting`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_base64: base64Image }),
  });
  const data = await res.json();
  return data.raw_text;
}

// Send raw text, get back corrected text + language
export async function correctText(rawText) {
  const res = await fetch(`${AI_BASE}/api/correct`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: rawText }),
  });
  return res.json(); // { corrected_text, language }
}
