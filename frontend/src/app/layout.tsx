import './globals.css'
import { Inter } from 'next/font/google'
import { MSALProvider } from '@/lib/auth/msalProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AWS Cognito User Management',
  description: 'Enterprise-grade Cognito user management application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <MSALProvider>
          {children}
        </MSALProvider>
      </body>
    </html>
  )
}

