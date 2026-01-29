import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'sonner'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'AI Learning Platform',
    description: 'AI-powered supplementary learning platform for university courses',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={inter.className}>
                {children}
                <Toaster position="bottom-right" richColors />
            </body>
        </html>
    )
}
