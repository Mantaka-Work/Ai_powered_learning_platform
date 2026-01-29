'use client'

import React, { useState, useRef } from 'react'
import { Sparkles, Loader2, Globe, Copy, Check, BookOpen, Code, Download, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { getValidationEmoji } from '@/lib/utils'

interface GenerationFormProps {
    onGenerate: (
        topic: string,
        type: 'theory' | 'code',
        options: {
            genType?: string
            language?: string
            useWeb?: boolean
        }
    ) => Promise<void>
    isLoading?: boolean
}

export function GenerationForm({ onGenerate, isLoading }: GenerationFormProps) {
    const [topic, setTopic] = useState('')
    const [activeTab, setActiveTab] = useState<'theory' | 'code'>('theory')
    const [theoryType, setTheoryType] = useState('notes')
    const [codeType, setCodeType] = useState('example')
    const [language, setLanguage] = useState('python')
    const [useWeb, setUseWeb] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!topic.trim() || isLoading) return

        if (activeTab === 'theory') {
            await onGenerate(topic, 'theory', { genType: theoryType, useWeb })
        } else {
            await onGenerate(topic, 'code', { genType: codeType, language, useWeb })
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Generate Content
                </CardTitle>
                <CardDescription>
                    Generate notes, summaries, or code examples using AI
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'theory' | 'code')}>
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="theory" className="gap-1">
                                <BookOpen className="h-4 w-4" />
                                Theory
                            </TabsTrigger>
                            <TabsTrigger value="code" className="gap-1">
                                <Code className="h-4 w-4" />
                                Code
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="theory" className="space-y-3 mt-4">
                            <div>
                                <label className="text-sm font-medium">Generation Type</label>
                                <div className="flex gap-2 mt-1">
                                    {['notes', 'summary', 'study_guide'].map((type) => (
                                        <Button
                                            key={type}
                                            type="button"
                                            variant={theoryType === type ? 'default' : 'outline'}
                                            size="sm"
                                            onClick={() => setTheoryType(type)}
                                        >
                                            {type.replace('_', ' ')}
                                        </Button>
                                    ))}
                                </div>
                            </div>
                        </TabsContent>

                        <TabsContent value="code" className="space-y-3 mt-4">
                            <div>
                                <label className="text-sm font-medium">Code Type</label>
                                <div className="flex gap-2 mt-1">
                                    {['example', 'solution', 'explanation'].map((type) => (
                                        <Button
                                            key={type}
                                            type="button"
                                            variant={codeType === type ? 'default' : 'outline'}
                                            size="sm"
                                            onClick={() => setCodeType(type)}
                                        >
                                            {type}
                                        </Button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="text-sm font-medium">Language</label>
                                <div className="flex gap-2 mt-1 flex-wrap">
                                    {['python', 'javascript', 'java', 'cpp', 'typescript'].map((lang) => (
                                        <Button
                                            key={lang}
                                            type="button"
                                            variant={language === lang ? 'default' : 'outline'}
                                            size="sm"
                                            onClick={() => setLanguage(lang)}
                                        >
                                            {lang}
                                        </Button>
                                    ))}
                                </div>
                            </div>
                        </TabsContent>
                    </Tabs>

                    <div>
                        <label className="text-sm font-medium">Topic</label>
                        <Textarea
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder={
                                activeTab === 'theory'
                                    ? 'Enter the topic for notes/summary...'
                                    : 'Describe the code you need...'
                            }
                            className="mt-1"
                        />
                    </div>

                    <div className="flex items-center justify-between">
                        <Button
                            type="button"
                            variant={useWeb ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setUseWeb(!useWeb)}
                            className="gap-1"
                        >
                            <Globe className="h-4 w-4" />
                            {useWeb ? 'Web Enabled' : 'Add Web Context'}
                        </Button>

                        <Button type="submit" disabled={isLoading || !topic.trim()}>
                            {isLoading ? (
                                <>
                                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="h-4 w-4 mr-2" />
                                    Generate
                                </>
                            )}
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    )
}

interface GeneratedContentProps {
    content: string
    type: string
    topic: string
    validationStatus?: string
    validationScore?: number
    sources?: {
        course?: { title: string; type: string; relevance: number }[]
        web?: { title: string; url: string; domain?: string }[]
        note?: string
        web_error?: string
    }
    usedWebSearch: boolean
    language?: string
}

export function GeneratedContent({
    content,
    type,
    topic,
    validationStatus,
    validationScore,
    sources,
    usedWebSearch,
    language,
}: GeneratedContentProps) {
    const [copied, setCopied] = useState(false)
    const [isDownloading, setIsDownloading] = useState(false)
    const contentRef = useRef<HTMLDivElement>(null)

    // Check if this is code content (but NOT explanation which should be rendered as markdown)
    const isCodeContent = type.startsWith('code_') && type !== 'code_explanation'
    const isExplanation = type === 'code_explanation'

    const handleCopy = async () => {
        await navigator.clipboard.writeText(content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const handleDownloadCode = () => {
        const extension = language || 'txt'
        const filename = `${topic.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${extension}`
        const blob = new Blob([content], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
    }

    const handleDownloadPDF = async () => {
        if (!contentRef.current) return

        setIsDownloading(true)
        try {
            // Dynamically import html2pdf to avoid SSR issues
            const html2pdf = (await import('html2pdf.js')).default

            const filename = `${topic.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`

            const opt = {
                margin: [10, 10, 10, 10] as [number, number, number, number],
                filename: filename,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' as const }
            }

            await html2pdf().set(opt).from(contentRef.current).save()
        } catch (error) {
            console.error('PDF download failed:', error)
        } finally {
            setIsDownloading(false)
        }
    }

    return (
        <Card>
            <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2 mb-10">
                            {isCodeContent ? <Code className="h-5 w-5" /> : <BookOpen className="h-5 w-5" />}
                            {/* {isExplanation ? 'Explanation of your code' : topic} */}
                        </CardTitle>
                        <CardDescription className="flex items-center gap-2 mt-1">
                            <Badge variant="secondary">{type.replace('_', ' ')}</Badge>
                            {language && <Badge variant="outline">{language}</Badge>}
                            {usedWebSearch && (
                                <Badge variant="outline" className="gap-1">
                                    <Globe className="h-3 w-3" />
                                    Web included
                                </Badge>
                            )}
                        </CardDescription>
                    </div>

                    <div className="flex items-center gap-2">
                        {validationStatus && (
                            <Badge
                                variant={
                                    validationStatus === 'validated'
                                        ? 'success'
                                        : validationStatus === 'warning'
                                            ? 'warning'
                                            : 'destructive'
                                }
                            >
                                {getValidationEmoji(validationStatus)} {validationScore?.toFixed(0)}%
                            </Badge>
                        )}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={isCodeContent ? handleDownloadCode : handleDownloadPDF}
                            disabled={isDownloading}
                            title={isCodeContent ? "Download Code" : "Download PDF"}
                        >
                            {isDownloading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Download className="h-4 w-4" />
                            )}
                        </Button>
                        <Button variant="outline" size="sm" onClick={handleCopy}>
                            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </Button>
                    </div>
                </div>
            </CardHeader>

            <CardContent>
                {isCodeContent ? (
                    <SyntaxHighlighter
                        language={language || 'text'}
                        style={oneDark}
                        customStyle={{ borderRadius: '0.5rem', fontSize: '0.875rem' }}
                    >
                        {content}
                    </SyntaxHighlighter>
                ) : (
                    <div ref={contentRef} className="markdown-content prose prose-sm dark:prose-invert max-w-none p-4 bg-white dark:bg-gray-900">
                        {/* Don't show topic for explanations since it contains the code being explained */}
                        {!isExplanation && <h1 className="text-xl font-bold mb-4">{topic}</h1>}
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                )}

                {/* Sources */}
                {sources && (sources.course?.length || sources.web?.length || sources.note || sources.web_error) && (
                    <div className="mt-4 pt-4 border-t">
                        <p className="text-sm font-medium mb-2">Sources</p>

                        {/* Note about limited course materials */}
                        {sources.note && (
                            <p className="text-xs text-amber-600 dark:text-amber-400 mb-2 flex items-center gap-1">
                                ⚠️ {sources.note}
                            </p>
                        )}

                        {/* Web search error */}
                        {sources.web_error && usedWebSearch && (
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1">
                                ℹ️ {sources.web_error}
                            </p>
                        )}

                        <div className="flex flex-wrap gap-2">
                            {sources.course?.map((s, i) => (
                                <Badge key={`course-${i}`} variant="secondary" className="text-xs">
                                    📚 {s.title} {s.relevance < 0.3 && <span className="opacity-60">(low match)</span>}
                                </Badge>
                            ))}
                            {sources.web?.map((s, i) => (
                                <Badge key={`web-${i}`} variant="outline" className="text-xs">
                                    {s.url ? (
                                        <a href={s.url} target="_blank" rel="noopener noreferrer" className="hover:underline flex items-center gap-1">
                                            🌐 {s.title || s.domain || 'Web Source'}
                                        </a>
                                    ) : (
                                        <span>🌐 {s.title || 'Web Source'}</span>
                                    )}
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

// Main GenerationInterface component that combines GenerationForm and GeneratedContent
interface GenerationInterfaceProps {
    courseId: string
}

export function GenerationInterface({ courseId }: GenerationInterfaceProps) {
    const [isLoading, setIsLoading] = useState(false)
    const [generatedContent, setGeneratedContent] = useState<{
        content: string
        type: string
        topic: string
        validationStatus?: string
        validationScore?: number
        sources?: any
        usedWebSearch: boolean
        language?: string
    } | null>(null)
    const [error, setError] = useState<string | null>(null)

    const handleGenerate = async (
        topic: string,
        type: 'theory' | 'code',
        options: {
            genType?: string
            language?: string
            useWeb?: boolean
        }
    ) => {
        setIsLoading(true)
        setError(null)
        try {
            const endpoint = type === 'theory' ? 'theory' : 'code'
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/generate/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    course_id: courseId,
                    topic,
                    type: options.genType,
                    language: options.language,
                    use_web: options.useWeb,
                }),
            })

            if (!response.ok) {
                throw new Error('Generation failed')
            }

            const data = await response.json()
            setGeneratedContent({
                content: data.content,
                type: data.type,
                topic: data.topic,
                validationStatus: data.validation_status,
                validationScore: data.validation_score,
                sources: data.sources,
                usedWebSearch: data.used_web_search,
                language: options.language,
            })
        } catch (err: any) {
            setError(err.message || 'Generation failed')
            console.error('Generation error:', err)
        }
        setIsLoading(false)
    }

    return (
        <div className="space-y-6">
            <GenerationForm onGenerate={handleGenerate} isLoading={isLoading} />

            {error && (
                <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
                    {error}
                </div>
            )}

            {generatedContent && !error && (
                <GeneratedContent
                    content={generatedContent.content}
                    type={generatedContent.type}
                    topic={generatedContent.topic}
                    validationStatus={generatedContent.validationStatus}
                    validationScore={generatedContent.validationScore}
                    sources={generatedContent.sources}
                    usedWebSearch={generatedContent.usedWebSearch}
                    language={generatedContent.language}
                />
            )}

            {!generatedContent && !error && !isLoading && (
                <div className="text-center py-12 text-muted-foreground">
                    <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Fill in the form above to generate content</p>
                </div>
            )}
        </div>
    )
}
