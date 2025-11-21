import React, { useState } from 'react';
import DOMPurify from 'dompurify';

// Safely support simple formatting markers without exposing XSS via innerHTML
// Supported: **bold** and *italic* (minimal by design)
function escapeHtml(str) {
  return str
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function formatToHtml(input) {
  // First, escape all HTML so user-supplied tags/scripts cannot run
  let s = escapeHtml(input || '');
  // Then, allow only our minimal formatting via regex replacements
  // **bold** -> <strong>bold</strong>
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // *italic* -> <em>italic</em>
  s = s.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Optionally convert double newlines to <br/>
  s = s.replace(/\n/g, '<br/>');
  return s;
}

const sanitizeOptions = {
  ALLOWED_TAGS: ['strong', 'em', 'br'],
  ALLOWED_ATTR: []
};

export default function App() {
  const [input, setInput] = useState('');

  const sanitizedHtml = DOMPurify.sanitize(formatToHtml(input), sanitizeOptions);

  return (
    <div style={{ padding: 16 }}>
      <h1>Safe Formatter</h1>
      <p>Type text using **bold** and *italic* markers. HTML/JS will be neutralized.</p>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows={6}
        style={{ width: '100%', fontFamily: 'inherit' }}
        placeholder="Try: Hello **world** and *friends*!"
      />
      <h2>Preview</h2>
      {/* Render sanitized HTML. Avoid direct innerHTML with raw user input. */}
      <div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
    </div>
  );
}

