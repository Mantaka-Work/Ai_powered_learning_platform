'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Globe, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import ReactMarkdown from 'react-markdown'
import { cn } from '@/lib/utils'

interface ChatMessage {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: {
        course?: { title: string; type: string; relevance: number }[]
        web?: { title: string; url: string }[]
    }
    used_web_search?: boolean
    created_at: string
}

interface ChatInterfaceProps {
    messages: ChatMessage[]
    onSendMessage: (content: string, includeWebSearch?: boolean) => Promise<void>
    isLoading?: boolean
    courseId: string
}

export function ChatInterface({
    messages,
    onSendMessage,
    isLoading = false,
    courseId,
}: ChatInterfaceProps) {
    const [input, setInput] = useState('')
    const [includeWebSearch, setIncludeWebSearch] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return

        const message = input
        setInput('')
        await onSendMessage(message, includeWebSearch)
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
        }
    }

    return (
        <div className="flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                    <div className="text-center text-muted-foreground py-12">
                        <p className="text-lg">Start a conversation</p>
                        <p className="text-sm">Ask questions about your course materials</p>
                    </div>
                ) : (
                    messages.map((message) => (
                        <ChatBubble key={message.id} message={message} />
                    ))
                )}
                {isLoading && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Thinking...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-4">
                <form onSubmit={handleSubmit} className="space-y-2">
                    <div className="flex items-center gap-2 mb-2">
                        <Button
                            type="button"
                            variant={includeWebSearch ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setIncludeWebSearch(!includeWebSearch)}
                            className="gap-1"
                        >
                            <Globe className="h-4 w-4" />
                            {includeWebSearch ? 'Web Search On' : 'Web Search Off'}
                        </Button>
                        <span className="text-xs text-muted-foreground">
                            {includeWebSearch
                                ? '🌐 Will search the web for additional info'
                                : '📚 Using course materials only'}
                        </span>
                    </div>
                    <div className="flex gap-2">
                        <Textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask a question about your course..."
                            className="min-h-[60px] resize-none"
                            disabled={isLoading}
                        />
                        <Button type="submit" disabled={isLoading || !input.trim()}>
                            {isLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Send className="h-4 w-4" />
                            )}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    )
}

function ChatBubble({ message }: { message: ChatMessage }) {
    const isUser = message.role === 'user'

    return (
        <div
            className={cn(
                'flex flex-col gap-2 max-w-[80%]',
                isUser ? 'ml-auto items-end' : 'mr-auto items-start'
            )}
        >
            <div
                className={cn(
                    'rounded-lg px-4 py-2',
                    isUser
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                )}
            >
                {isUser ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                    <div className="markdown-content prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                )}
            </div>

            {/* Sources */}
            {!isUser && message.sources && (
                <div className="flex flex-wrap gap-1">
                    {message.sources.course?.map((source, i) => (
                        <Badge key={`course-${i}`} variant="secondary" className="text-xs">
                            📚 {source.title}
                        </Badge>
                    ))}
                    {message.sources.web?.map((source, i) => (
                        <Badge key={`web-${i}`} variant="outline" className="text-xs">
                            <a
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:underline"
                            >
                                🌐 {source.title}
                            </a>
                        </Badge>
                    ))}
                </div>
            )}

            {/* Web search indicator */}
            {!isUser && message.used_web_search && (
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Globe className="h-3 w-3" />
                    Included web search results
                </span>
            )}
        </div>
    )
}

export function WebSearchBadge({ used }: { used: boolean }) {
    return (
        <Badge variant={used ? 'default' : 'outline'} className="gap-1">
            <Globe className="h-3 w-3" />
            {used ? 'Web Search Used' : 'Course Only'}
        </Badge>
    )
}
