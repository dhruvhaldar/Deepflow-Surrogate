'use client';

import { useState, useRef, useEffect } from 'react';

export default function CopyButton({ text, ariaLabel = "Copy to clipboard" }: { text: string; ariaLabel?: string }) {
  const [copied, setCopied] = useState(false);
  const [hasError, setHasError] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleCopy = async () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setHasError(false);

      timeoutRef.current = setTimeout(() => {
        setCopied(false);
        timeoutRef.current = null;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      setHasError(true);
      setCopied(false);

      timeoutRef.current = setTimeout(() => {
        setHasError(false);
        timeoutRef.current = null;
      }, 2000);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={handleCopy}
        className="button ghost"
        aria-label={ariaLabel}
        title={hasError ? "Failed to copy" : copied ? "Copied!" : ariaLabel}
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
        {hasError ? (
          <>
            <span aria-hidden="true">✕</span> Error
          </>
        ) : copied ? (
          <>
            <span aria-hidden="true">✓</span> Copied
          </>
        ) : (
          <>
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            Copy
          </>
        )}
      </button>
      <span aria-live="polite" style={{ position: 'absolute', width: 1, height: 1, padding: 0, margin: -1, overflow: 'hidden', clip: 'rect(0, 0, 0, 0)', whiteSpace: 'nowrap', borderWidth: 0 }}>
        {hasError ? "Failed to copy to clipboard" : copied ? (ariaLabel.startsWith("Copy") ? ariaLabel.replace("Copy", "Copied") : "Copied to clipboard") : ""}
      </span>
    </>
  );
}
