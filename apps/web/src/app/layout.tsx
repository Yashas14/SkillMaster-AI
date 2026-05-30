import type { Metadata, Viewport } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { Toaster } from 'sonner';
import { Providers } from './providers';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'SkillMaster AI - Learn Smarter with AI',
    template: '%s | SkillMaster AI',
  },
  description:
    'World-class AI-native learning platform with personalized tutoring, adaptive learning, and immersive experiences.',
  keywords: [
    'online learning',
    'AI tutor',
    'coding courses',
    'adaptive learning',
    'LMS',
    'education technology',
  ],
  authors: [{ name: 'SkillMaster AI' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://skillmaster.ai',
    siteName: 'SkillMaster AI',
    title: 'SkillMaster AI - Learn Smarter with AI',
    description: 'World-class AI-native learning platform',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SkillMaster AI',
    description: 'Learn Smarter with AI',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans`}>
        <Providers>
          {children}
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  );
}
