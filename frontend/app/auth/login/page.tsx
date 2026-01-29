'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { signIn, signUp } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Loader2, BookOpen } from 'lucide-react'

export default function LoginPage() {
    const router = useRouter()
    const [isLogin, setIsLogin] = useState(true)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [fullName, setFullName] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')
    const [message, setMessage] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setMessage('')
        setIsLoading(true)

        try {
            if (isLogin) {
                const { data, error } = await signIn(email, password)
                if (error) {
                    setError(error.message)
                } else {
                    router.push('/courses')
                }
            } else {
                const { data, error } = await signUp(email, password, fullName)
                if (error) {
                    setError(error.message)
                } else {
                    setMessage('Account created! Please check your email to verify your account.')
                }
            }
        } catch (err: any) {
            setError(err.message || 'An error occurred')
        }

        setIsLoading(false)
    }

    return (
        <main className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted p-4">
            <Card className="w-full max-w-md p-8">
                {/* Logo */}
                <div className="flex flex-col items-center mb-8">
                    <div className="p-3 rounded-full bg-primary/10 text-primary mb-4">
                        <BookOpen className="h-8 w-8" />
                    </div>
                    <h1 className="text-2xl font-bold">AI Learning Platform</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        {isLogin ? 'Sign in to continue' : 'Create your account'}
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLogin && (
                        <div>
                            <label className="text-sm font-medium mb-2 block">Full Name</label>
                            <Input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                placeholder="John Doe"
                            />
                        </div>
                    )}
                    <div>
                        <label className="text-sm font-medium mb-2 block">Email</label>
                        <Input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@example.com"
                            required
                        />
                    </div>
                    <div>
                        <label className="text-sm font-medium mb-2 block">Password</label>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    {error && (
                        <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
                            {error}
                        </div>
                    )}

                    {message && (
                        <div className="p-3 rounded-lg bg-green-500/10 text-green-600 text-sm">
                            {message}
                        </div>
                    )}

                    <Button type="submit" className="w-full" disabled={isLoading}>
                        {isLoading ? (
                            <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                {isLogin ? 'Signing in...' : 'Creating account...'}
                            </>
                        ) : (
                            isLogin ? 'Sign In' : 'Create Account'
                        )}
                    </Button>
                </form>

                {/* Toggle */}
                <div className="mt-6 text-center text-sm">
                    {isLogin ? (
                        <p className="text-muted-foreground">
                            Don't have an account?{' '}
                            <button
                                onClick={() => setIsLogin(false)}
                                className="text-primary hover:underline font-medium"
                            >
                                Sign up
                            </button>
                        </p>
                    ) : (
                        <p className="text-muted-foreground">
                            Already have an account?{' '}
                            <button
                                onClick={() => setIsLogin(true)}
                                className="text-primary hover:underline font-medium"
                            >
                                Sign in
                            </button>
                        </p>
                    )}
                </div>

                {/* Back to Home */}
                <div className="mt-4 text-center">
                    <Link href="/" className="text-sm text-muted-foreground hover:text-primary">
                        ← Back to Home
                    </Link>
                </div>
            </Card>
        </main>
    )
}
