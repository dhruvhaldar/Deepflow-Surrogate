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
    <button
      onClick={handleCopy}
      className="button ghost"
      aria-label={copied ? "Copied" : "Copy to clipboard"}
      aria-live="polite"
      style={{
        padding: '0.3rem 0.6rem',
        fontSize: '0.8rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.3rem'
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
  );
}
