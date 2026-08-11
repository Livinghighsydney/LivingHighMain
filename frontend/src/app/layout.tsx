import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Living High',
  description: 'Co-living and shared accommodation in Sydney.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
