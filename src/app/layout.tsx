import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Keeper - Turn Your Data Into Revenue',
  description: 'AI-powered business intelligence that finds $3,000+ in hidden revenue opportunities using your Square POS data.',
  keywords: 'Square POS, business intelligence, revenue optimization, AI insights, spa management, salon software',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}