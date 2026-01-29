'use client'

import { useState, useCallback } from 'react'
import { searchApi, SearchResponse } from '@/lib/api'

interface UseSearchOptions {
    courseId: string
    onError?: (error: Error) => void
}

export function useSearch({ courseId, onError }: UseSearchOptions) {
    const [results, setResults] = useState<SearchResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const searchSemantic = useCallback(async (query: string, limit?: number) => {
        try {
            setIsLoading(true)
            setError(null)
            const data = await searchApi.semantic(courseId, query, limit)
            setResults(data)
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        } finally {
            setIsLoading(false)
        }
    }, [courseId, onError])

    const searchHybrid = useCallback(async (
        query: string,
        includeWeb?: boolean,
        limit?: number
    ) => {
        try {
            setIsLoading(true)
            setError(null)
            const data = await searchApi.hybrid(courseId, query, includeWeb, limit)
            setResults(data)
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        } finally {
            setIsLoading(false)
        }
    }, [courseId, onError])

    const searchWeb = useCallback(async (query: string, limit?: number) => {
        try {
            setIsLoading(true)
            setError(null)
            const data = await searchApi.web(query, limit)
            setResults(data)
            return data
        } catch (err) {
            const error = err as Error
            setError(error)
            onError?.(error)
        } finally {
            setIsLoading(false)
        }
    }, [onError])

    const clearResults = useCallback(() => {
        setResults(null)
        setError(null)
    }, [])

    return {
        results,
        isLoading,
        error,
        searchSemantic,
        searchHybrid,
        searchWeb,
        clearResults,
    }
}
