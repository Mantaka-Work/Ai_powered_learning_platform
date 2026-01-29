'use client'

import { useState, useCallback } from 'react'
import { chatApi, ChatMessage, ChatSession } from '@/lib/api'

interface UseChatOptions {
    courseId: string
    sessionId?: string
    onError?: (error: Error) => void
}

export function useChat({ courseId, sessionId: initialSessionId, onError }: UseChatOptions) {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [sessions, setSessions] = useState<ChatSession[]>([])
    const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const loadSessions = useCallback(async () => {
        try {
            const data = await chatApi.getSessions(courseId)
            setSessions(data)
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
            return []
        }
    }, [courseId, onError])

    const loadSession = useCallback(async (sessionId: string) => {
        try {
            setIsLoading(true)
            const data = await chatApi.getHistory(sessionId)
            setCurrentSession(data.session as unknown as ChatSession)
            setMessages(data.messages)
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        } finally {
            setIsLoading(false)
        }
    }, [onError])

    const createSession = useCallback(async (title?: string) => {
        try {
            const session = await chatApi.createSession(courseId, title)
            setCurrentSession(session)
            setMessages([])
            setSessions((prev) => [session, ...prev])
            return session
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        }
    }, [courseId, onError])

    const sendMessage = useCallback(async (content: string, includeWebSearch?: boolean) => {
        if (!currentSession) {
            // Create a new session if none exists
            const session = await createSession()
            if (!session) return
        }

        const sessionId = currentSession!.id

        // Add user message immediately for optimistic UI
        const userMessage: ChatMessage = {
            id: `temp-${Date.now()}`,
            role: 'user',
            content,
            created_at: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, userMessage])

        try {
            setIsLoading(true)
            const response = await chatApi.sendMessage(
                sessionId,
                courseId,
                content,
                includeWebSearch
            )

            // Replace temp message and add assistant response
            setMessages((prev) => {
                const filtered = prev.filter((m) => !m.id.startsWith('temp-'))
                return [
                    ...filtered,
                    { ...userMessage, id: `user-${Date.now()}` },
                    response.message,
                ]
            })

            return response
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
            // Remove optimistic message on error
            setMessages((prev) => prev.filter((m) => !m.id.startsWith('temp-')))
        } finally {
            setIsLoading(false)
        }
    }, [currentSession, courseId, createSession, onError])

    const deleteSession = useCallback(async (sessionId: string) => {
        try {
            await chatApi.deleteSession(sessionId)
            setSessions((prev) => prev.filter((s) => s.id !== sessionId))
            if (currentSession?.id === sessionId) {
                setCurrentSession(null)
                setMessages([])
            }
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        }
    }, [currentSession, onError])

    const clearError = useCallback(() => setError(null), [])

    return {
        messages,
        sessions,
        currentSession,
        isLoading,
        error,
        loadSessions,
        loadSession,
        createSession,
        sendMessage,
        deleteSession,
        clearError,
    }
}
