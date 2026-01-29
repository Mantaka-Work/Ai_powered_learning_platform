'use client'

import { useState, useCallback } from 'react'
import { generateApi, GenerationResponse } from '@/lib/api'

interface UseGenerationOptions {
    courseId: string
    onError?: (error: Error) => void
}

export function useGeneration({ courseId, onError }: UseGenerationOptions) {
    const [result, setResult] = useState<GenerationResponse | null>(null)
    const [history, setHistory] = useState<GenerationResponse[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const generateTheory = useCallback(async (
        topic: string,
        type: string = 'notes',
        useWeb: boolean = false
    ) => {
        try {
            setIsLoading(true)
            setError(null)
            const data = await generateApi.theory(courseId, topic, type, useWeb)
            setResult(data)
            setHistory((prev) => [data, ...prev])
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        } finally {
            setIsLoading(false)
        }
    }, [courseId, onError])

    const generateCode = useCallback(async (
        topic: string,
        language: string,
        type: string = 'example',
        useWeb: boolean = false
    ) => {
        try {
            setIsLoading(true)
            setError(null)
            const data = await generateApi.code(courseId, topic, language, type, useWeb)
            setResult(data)
            setHistory((prev) => [data, ...prev])
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        } finally {
            setIsLoading(false)
        }
    }, [courseId, onError])

    const loadHistory = useCallback(async (type?: string) => {
        try {
            const data = await generateApi.history(courseId, type)
            setHistory(data)
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        }
    }, [courseId, onError])

    const clearResult = useCallback(() => {
        setResult(null)
        setError(null)
    }, [])

    return {
        result,
        history,
        isLoading,
        error,
        generateTheory,
        generateCode,
        loadHistory,
        clearResult,
    }
}
