'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileUpload } from '@/components/Materials/FileUpload'
import { SearchInterface } from '@/components/Search/SearchInterface'
import { GenerationInterface } from '@/components/Generation/GenerationInterface'
import { ChatInterface } from '@/components/Chat/ChatInterface'
import { chatApi } from '@/lib/api'
import { ArrowLeft, Upload, Search, Sparkles, MessageSquare, Loader2, FileText } from 'lucide-react'

interface Course {
    id: string
    name: string
    description: string | null
    created_at: string
}

interface Material {
    id: string
    title: string
    file_type: string
    category: string
    week_number: number | null
    created_at: string
}

interface ChatMessage {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: any
    used_web_search?: boolean
    created_at: string
}

export default function CoursePage() {
    const params = useParams()
    const courseId = params.id as string

    const [course, setCourse] = useState<Course | null>(null)
    const [materials, setMaterials] = useState<Material[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('materials')

    // Chat state
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
    const [chatSessionId, setChatSessionId] = useState<string | null>(null)
    const [isChatLoading, setIsChatLoading] = useState(false)

    useEffect(() => {
        if (courseId) {
            fetchCourseData()
        }
    }, [courseId])

    const fetchCourseData = async () => {
        setIsLoading(true)

        // Fetch course details
        const { data: courseData, error: courseError } = await supabase
            .from('courses')
            .select('*')
            .eq('id', courseId)
            .single()

        if (courseError) {
            console.error('Error fetching course:', courseError)
        } else {
            setCourse(courseData)
        }

        // Fetch materials
        const { data: materialsData, error: materialsError } = await supabase
            .from('materials')
            .select('*')
            .eq('course_id', courseId)
            .order('created_at', { ascending: false })

        if (materialsError) {
            console.error('Error fetching materials:', materialsError)
        } else {
            setMaterials(materialsData || [])
        }

        setIsLoading(false)
    }

    const handleSendMessage = async (content: string, includeWebSearch?: boolean) => {
        setIsChatLoading(true)
        try {
            let sessionId = chatSessionId

            // Create session if doesn't exist
            if (!sessionId) {
                const session = await chatApi.createSession(courseId, `Chat about ${course?.name}`)
                sessionId = session.id
                setChatSessionId(sessionId)
            }

            // Add user message to UI
            const userMessage: ChatMessage = {
                id: `temp-${Date.now()}`,
                role: 'user',
                content,
                created_at: new Date().toISOString()
            }
            setChatMessages(prev => [...prev, userMessage])

            // Send message to API
            const response = await chatApi.sendMessage(sessionId, courseId, content, includeWebSearch)

            // Add assistant response
            const assistantMessage: ChatMessage = {
                id: response.message.id,
                role: 'assistant',
                content: response.message.content,
                sources: response.sources,
                used_web_search: response.message.used_web_search,
                created_at: response.message.created_at
            }
            setChatMessages(prev => [...prev.filter(m => m.id !== userMessage.id),
            { ...userMessage, id: `user-${Date.now()}` },
                assistantMessage
            ])
        } catch (error) {
            console.error('Error sending message:', error)
        }
        setIsChatLoading(false)
    }

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (!course) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center">
                <h1 className="text-2xl font-bold mb-4">Course not found</h1>
                <Link href="/courses">
                    <Button>Back to Courses</Button>
                </Link>
            </div>
        )
    }

    return (
        <main className="min-h-screen bg-gradient-to-b from-background to-muted">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/courses">
                        <Button variant="ghost" size="icon">
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold">{course.name}</h1>
                        {course.description && (
                            <p className="text-muted-foreground">{course.description}</p>
                        )}
                    </div>
                </div>

                {/* Tabs */}
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                    <TabsList className="grid w-full grid-cols-4 mb-8">
                        <TabsTrigger value="materials" className="gap-2">
                            <Upload className="h-4 w-4" />
                            Materials
                        </TabsTrigger>
                        <TabsTrigger value="search" className="gap-2">
                            <Search className="h-4 w-4" />
                            Search
                        </TabsTrigger>
                        <TabsTrigger value="generate" className="gap-2">
                            <Sparkles className="h-4 w-4" />
                            Generate
                        </TabsTrigger>
                        <TabsTrigger value="chat" className="gap-2">
                            <MessageSquare className="h-4 w-4" />
                            Chat
                        </TabsTrigger>
                    </TabsList>

                    {/* Materials Tab */}
                    <TabsContent value="materials">
                        <div className="grid lg:grid-cols-2 gap-8">
                            {/* Upload Section */}
                            <Card className="p-6">
                                <h2 className="text-xl font-semibold mb-4">Upload Materials</h2>
                                <FileUpload courseId={courseId} onUploadSuccess={fetchCourseData} />
                            </Card>

                            {/* Materials List */}
                            <Card className="p-6">
                                <h2 className="text-xl font-semibold mb-4">
                                    Uploaded Materials ({materials.length})
                                </h2>
                                {materials.length === 0 ? (
                                    <p className="text-muted-foreground text-center py-8">
                                        No materials uploaded yet
                                    </p>
                                ) : (
                                    <div className="space-y-3 max-h-[500px] overflow-y-auto">
                                        {materials.map((material) => (
                                            <div
                                                key={material.id}
                                                className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50"
                                            >
                                                <FileText className="h-5 w-5 text-primary" />
                                                <div className="flex-1 min-w-0">
                                                    <p className="font-medium truncate">{material.title}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {material.file_type.toUpperCase()} • {material.category}
                                                        {material.week_number && ` • Week ${material.week_number}`}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </Card>
                        </div>
                    </TabsContent>

                    {/* Search Tab */}
                    <TabsContent value="search">
                        <Card className="p-6">
                            <SearchInterface courseId={courseId} />
                        </Card>
                    </TabsContent>

                    {/* Generate Tab */}
                    <TabsContent value="generate">
                        <Card className="p-6">
                            <GenerationInterface courseId={courseId} />
                        </Card>
                    </TabsContent>

                    {/* Chat Tab */}
                    <TabsContent value="chat">
                        <Card className="h-[600px] flex flex-col">
                            <ChatInterface
                                messages={chatMessages}
                                onSendMessage={handleSendMessage}
                                isLoading={isChatLoading}
                                courseId={courseId}
                            />
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </main>
    )
}
