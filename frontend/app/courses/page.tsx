'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Plus, BookOpen, ArrowRight, Loader2 } from 'lucide-react'

interface Course {
    id: string
    name: string
    description: string | null
    created_at: string
}

export default function CoursesPage() {
    const [courses, setCourses] = useState<Course[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [newCourseName, setNewCourseName] = useState('')
    const [newCourseDescription, setNewCourseDescription] = useState('')
    const [isCreating, setIsCreating] = useState(false)

    useEffect(() => {
        fetchCourses()
    }, [])

    const fetchCourses = async () => {
        setIsLoading(true)
        const { data, error } = await supabase
            .from('courses')
            .select('*')
            .order('created_at', { ascending: false })

        if (error) {
            console.error('Error fetching courses:', error)
        } else {
            setCourses(data || [])
        }
        setIsLoading(false)
    }

    const createCourse = async () => {
        if (!newCourseName.trim()) return

        setIsCreating(true)
        const { data, error } = await supabase
            .from('courses')
            .insert([
                {
                    name: newCourseName.trim(),
                    description: newCourseDescription.trim() || null
                }
            ])
            .select()

        if (error) {
            console.error('Error creating course:', error)
        } else {
            setCourses([...(data || []), ...courses])
            setNewCourseName('')
            setNewCourseDescription('')
            setShowCreateForm(false)
            fetchCourses()
        }
        setIsCreating(false)
    }

    return (
        <main className="min-h-screen bg-gradient-to-b from-background to-muted">
            <div className="container mx-auto px-4 py-12">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold mb-2">Courses</h1>
                        <p className="text-muted-foreground">
                            Select a course to access materials, search, and AI features
                        </p>
                    </div>
                    <Button onClick={() => setShowCreateForm(!showCreateForm)} className="gap-2">
                        <Plus className="h-4 w-4" />
                        New Course
                    </Button>
                </div>

                {/* Create Course Form */}
                {showCreateForm && (
                    <Card className="p-6 mb-8 border-2 border-primary/20">
                        <h2 className="text-xl font-semibold mb-4">Create New Course</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm font-medium mb-2 block">Course Name</label>
                                <Input
                                    value={newCourseName}
                                    onChange={(e) => setNewCourseName(e.target.value)}
                                    placeholder="e.g., Structured Programming Language"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium mb-2 block">Description (optional)</label>
                                <Input
                                    value={newCourseDescription}
                                    onChange={(e) => setNewCourseDescription(e.target.value)}
                                    placeholder="Brief description of the course"
                                />
                            </div>
                            <div className="flex gap-2">
                                <Button onClick={createCourse} disabled={isCreating || !newCourseName.trim()}>
                                    {isCreating ? (
                                        <>
                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                            Creating...
                                        </>
                                    ) : (
                                        'Create Course'
                                    )}
                                </Button>
                                <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Courses Grid */}
                {isLoading ? (
                    <div className="flex items-center justify-center py-20">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    </div>
                ) : courses.length === 0 ? (
                    <div className="text-center py-20">
                        <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                        <h2 className="text-2xl font-semibold mb-2">No courses yet</h2>
                        <p className="text-muted-foreground mb-4">
                            Create your first course to get started
                        </p>
                        <Button onClick={() => setShowCreateForm(true)} className="gap-2">
                            <Plus className="h-4 w-4" />
                            Create Course
                        </Button>
                    </div>
                ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {courses.map((course) => (
                            <Link key={course.id} href={`/courses/${course.id}`}>
                                <Card className="p-6 hover:shadow-lg transition-all hover:border-primary/50 cursor-pointer group">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="p-3 rounded-lg bg-primary/10 text-primary">
                                            <BookOpen className="h-6 w-6" />
                                        </div>
                                        <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2">{course.name}</h3>
                                    <p className="text-sm text-muted-foreground line-clamp-2">
                                        {course.description || 'No description provided'}
                                    </p>
                                    <p className="text-xs text-muted-foreground mt-4">
                                        Created {new Date(course.created_at).toLocaleDateString()}
                                    </p>
                                </Card>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </main>
    )
}
