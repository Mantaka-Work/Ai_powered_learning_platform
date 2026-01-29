'use client'

import { useState } from 'react'
import { Sparkles, Loader2, Globe, Copy, Check, BookOpen, Code } from 'lucide-react'
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
        web?: { title: string; url: string }[]
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
    const isCode = type.startsWith('code_')

    const handleCopy = async () => {
        await navigator.clipboard.writeText(content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <Card>
            <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            {isCode ? <Code className="h-5 w-5" /> : <BookOpen className="h-5 w-5" />}
                            {topic}
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
                        <Button variant="outline" size="sm" onClick={handleCopy}>
                            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </Button>
                    </div>
                </div>
            </CardHeader>

            <CardContent>
                {isCode ? (
                    <SyntaxHighlighter
                        language={language || 'text'}
                        style={oneDark}
                        customStyle={{ borderRadius: '0.5rem', fontSize: '0.875rem' }}
                    >
                        {content}
                    </SyntaxHighlighter>
                ) : (
                    <div className="markdown-content prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                )}

                {/* Sources */}
                {sources && (sources.course?.length || sources.web?.length) && (
                    <div className="mt-4 pt-4 border-t">
                        <p className="text-sm font-medium mb-2">Sources</p>
                        <div className="flex flex-wrap gap-2">
                            {sources.course?.map((s, i) => (
                                <Badge key={`course-${i}`} variant="secondary" className="text-xs">
                                    📚 {s.title}
                                </Badge>
                            ))}
                            {sources.web?.map((s, i) => (
                                <Badge key={`web-${i}`} variant="outline" className="text-xs">
                                    <a href={s.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                                        🌐 {s.title}
                                    </a>
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
