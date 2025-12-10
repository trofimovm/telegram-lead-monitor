import type { Metadata } from 'next'
import '@/styles/globals.css'
import { Providers } from '@/components/Providers'

export const metadata: Metadata = {
  title: 'Telegram Lead Monitor',
  description: 'Monitor Telegram channels and find relevant leads with LLM analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
