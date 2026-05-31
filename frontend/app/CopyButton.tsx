'use client';

import { useState } from 'react';

export default function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={handleCopy}
        className="button ghost"
        aria-label="Copy to clipboard"
        title="Copy to clipboard"
        style={{
          padding: '0.3rem 0.6rem',
          fontSize: '0.8rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.3rem',
          minWidth: '5.5rem'
        }}
      >
        {copied ? (
          <>
            <span aria-hidden="true">✓</span> Copied
          </>
        ) : (
          'Copy'
        )}
      </button>
      <span aria-live="polite" style={{ position: 'absolute', width: 1, height: 1, padding: 0, margin: -1, overflow: 'hidden', clip: 'rect(0, 0, 0, 0)', whiteSpace: 'nowrap', borderWidth: 0 }}>
        {copied ? "Copied to clipboard" : ""}
      </span>
    </>
  );
}
