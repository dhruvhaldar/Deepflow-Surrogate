import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Deepflow-Surrogate',
  description: 'Vercel-ready showcase for the Deepflow-Surrogate project capabilities.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
