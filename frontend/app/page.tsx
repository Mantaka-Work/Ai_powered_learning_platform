import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { BookOpen, Search, Sparkles, MessageSquare, Shield } from 'lucide-react'

export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-b from-background to-muted">
            {/* Hero Section */}
            <section className="container mx-auto px-4 py-20 text-center">
                <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                    AI-Powered Learning Platform
                </h1>
                <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                    Enhance your university learning experience with AI-generated notes,
                    semantic search, and intelligent chat assistance.
                </p>
                <div className="flex gap-4 justify-center">
                    <Link href="/courses">
                        <Button size="lg" className="gap-2">
                            <BookOpen className="h-5 w-5" />
                            Browse Courses
                        </Button>
                    </Link>
                    <Link href="/auth/login">
                        <Button size="lg" variant="outline">
                            Get Started
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Features Section */}
            <section className="container mx-auto px-4 py-16">
                <h2 className="text-3xl font-bold text-center mb-12">Platform Features</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <FeatureCard
                        icon={<BookOpen className="h-8 w-8" />}
                        title="Course Materials"
                        description="Upload and manage PDF, PPTX, DOCX, and code files organized by week and topic."
                    />
                    <FeatureCard
                        icon={<Search className="h-8 w-8" />}
                        title="Smart Search"
                        description="Semantic search through course materials with automatic web search fallback."
                    />
                    <FeatureCard
                        icon={<Sparkles className="h-8 w-8" />}
                        title="AI Generation"
                        description="Generate notes, summaries, study guides, and code examples on any topic."
                    />
                    <FeatureCard
                        icon={<MessageSquare className="h-8 w-8" />}
                        title="Chat Assistant"
                        description="Ask questions and get answers grounded in your course materials."
                    />
                </div>
            </section>

            {/* How It Works Section */}
            <section className="container mx-auto px-4 py-16 bg-muted/50 rounded-3xl">
                <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
                <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
                    <StepCard
                        number={1}
                        title="Upload Materials"
                        description="Upload your course slides, notes, and code files to the platform."
                    />
                    <StepCard
                        number={2}
                        title="AI Processing"
                        description="Our AI indexes and understands your materials for intelligent retrieval."
                    />
                    <StepCard
                        number={3}
                        title="Learn Smarter"
                        description="Search, generate content, and chat with AI about your courses."
                    />
                </div>
            </section>

            {/* Source Attribution Section */}
            <section className="container mx-auto px-4 py-16 text-center">
                <div className="flex justify-center gap-8 mb-6">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">📚</span>
                        <span className="text-muted-foreground">Course Materials</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">🌐</span>
                        <span className="text-muted-foreground">Web Sources</span>
                    </div>
                </div>
                <p className="text-muted-foreground max-w-xl mx-auto">
                    Every response clearly shows its sources, so you always know where information comes from.
                </p>
            </section>

            {/* Footer */}
            <footer className="container mx-auto px-4 py-8 border-t">
                <div className="flex justify-between items-center">
                    <p className="text-muted-foreground">
                        © 2024 AI Learning Platform. Built for BUET Hackathon.
                    </p>
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <Shield className="h-4 w-4" />
                        <span>Validated Content</span>
                    </div>
                </div>
            </footer>
        </main>
    )
}

function FeatureCard({ icon, title, description }: {
    icon: React.ReactNode
    title: string
    description: string
}) {
    return (
        <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
            <div className="text-primary mb-4">{icon}</div>
            <h3 className="font-semibold text-lg mb-2">{title}</h3>
            <p className="text-muted-foreground text-sm">{description}</p>
        </div>
    )
}

function StepCard({ number, title, description }: {
    number: number
    title: string
    description: string
}) {
    return (
        <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold mx-auto mb-4">
                {number}
            </div>
            <h3 className="font-semibold text-lg mb-2">{title}</h3>
            <p className="text-muted-foreground text-sm">{description}</p>
        </div>
    )
}
