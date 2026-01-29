'use client'

import { useState } from 'react'
import { Search, Loader2, Globe, BookOpen, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'

interface SearchResult {
    id: string
    content: string
    material_id: string
    material_title: string
    file_type: string
    category: string
    relevance_score: number
}

interface WebSearchResult {
    title: string
    url: string
    snippet: string
    source_domain: string
}

interface SearchBoxProps {
    onSearch: (query: string, includeWeb?: boolean) => Promise<void>
    isLoading?: boolean
}

export function SearchBox({ onSearch, isLoading }: SearchBoxProps) {
    const [query, setQuery] = useState('')
    const [includeWeb, setIncludeWeb] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!query.trim() || isLoading) return
        await onSearch(query, includeWeb)
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-3">
            <div className="flex gap-2">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search course materials..."
                        className="pl-10"
                        disabled={isLoading}
                    />
                </div>
                <Button type="submit" disabled={isLoading || !query.trim()}>
                    {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                        'Search'
                    )}
                </Button>
            </div>
            <div className="flex items-center gap-2">
                <Button
                    type="button"
                    variant={includeWeb ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setIncludeWeb(!includeWeb)}
                    className="gap-1"
                >
                    <Globe className="h-4 w-4" />
                    Include Web
                </Button>
                <span className="text-xs text-muted-foreground">
                    {includeWeb
                        ? 'Will search web if course relevance is low'
                        : 'Searching course materials only'}
                </span>
            </div>
        </form>
    )
}

interface SearchResultsProps {
    courseResults: SearchResult[]
    webResults: WebSearchResult[]
    usedWebSearch: boolean
    averageRelevance: number
    tookMs: number
}

export function SearchResults({
    courseResults,
    webResults,
    usedWebSearch,
    averageRelevance,
    tookMs,
}: SearchResultsProps) {
    const hasCourseResults = courseResults.length > 0
    const hasWebResults = webResults.length > 0

    return (
        <div className="space-y-4">
            {/* Stats */}
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>
                    {courseResults.length + webResults.length} results in {tookMs}ms
                </span>
                {usedWebSearch && (
                    <Badge variant="outline" className="gap-1">
                        <Globe className="h-3 w-3" />
                        Web search included
                    </Badge>
                )}
                <span>Relevance: {(averageRelevance * 100).toFixed(0)}%</span>
            </div>

            {/* Tabbed Results */}
            <Tabs defaultValue={hasCourseResults ? 'course' : 'web'}>
                <TabsList>
                    <TabsTrigger value="course" className="gap-1">
                        <BookOpen className="h-4 w-4" />
                        Course ({courseResults.length})
                    </TabsTrigger>
                    {hasWebResults && (
                        <TabsTrigger value="web" className="gap-1">
                            <Globe className="h-4 w-4" />
                            Web ({webResults.length})
                        </TabsTrigger>
                    )}
                </TabsList>

                <TabsContent value="course" className="space-y-3 mt-4">
                    {courseResults.length === 0 ? (
                        <p className="text-muted-foreground text-center py-8">
                            No course results found
                        </p>
                    ) : (
                        courseResults.map((result) => (
                            <CourseResultCard key={result.id} result={result} />
                        ))
                    )}
                </TabsContent>

                {hasWebResults && (
                    <TabsContent value="web" className="space-y-3 mt-4">
                        {webResults.map((result, i) => (
                            <WebResultCard key={i} result={result} />
                        ))}
                    </TabsContent>
                )}
            </Tabs>
        </div>
    )
}

function CourseResultCard({ result }: { result: SearchResult }) {
    return (
        <Card>
            <CardHeader className="py-3 px-4">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">📚</span>
                        <CardTitle className="text-base">{result.material_title}</CardTitle>
                    </div>
                    <Badge variant="secondary">
                        {(result.relevance_score * 100).toFixed(0)}% match
                    </Badge>
                </div>
                <div className="flex gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                        {result.file_type.toUpperCase()}
                    </Badge>
                    <Badge variant="outline" className="text-xs capitalize">
                        {result.category}
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="py-2 px-4">
                <p className="text-sm text-muted-foreground line-clamp-3">
                    {result.content}
                </p>
            </CardContent>
        </Card>
    )
}

function WebResultCard({ result }: { result: WebSearchResult }) {
    return (
        <Card>
            <CardHeader className="py-3 px-4">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🌐</span>
                        <CardTitle className="text-base">{result.title}</CardTitle>
                    </div>
                    <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                    >
                        <ExternalLink className="h-4 w-4" />
                    </a>
                </div>
                <p className="text-xs text-muted-foreground">{result.source_domain}</p>
            </CardHeader>
            <CardContent className="py-2 px-4">
                <p className="text-sm text-muted-foreground line-clamp-3">
                    {result.snippet}
                </p>
            </CardContent>
        </Card>
    )
}
