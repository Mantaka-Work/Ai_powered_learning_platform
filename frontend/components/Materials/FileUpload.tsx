'use client'

import { useState, useRef } from 'react'
import { Upload, File, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatFileSize } from '@/lib/utils'

interface FileUploadProps {
    courseId: string
    onUploadSuccess?: () => void
    supportedTypes?: string[]
    maxSize?: number // in bytes
}

interface FileMetadata {
    title?: string
    category: 'theory' | 'lab'
    week_number?: number
    tags?: string[]
}

export function FileUpload({
    courseId,
    onUploadSuccess,
    supportedTypes = ['pdf', 'pptx', 'docx', 'py', 'js', 'java', 'cpp', 'md', 'txt'],
    maxSize = 50 * 1024 * 1024, // 50MB
}: FileUploadProps) {
    const [dragActive, setDragActive] = useState(false)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [metadata, setMetadata] = useState<FileMetadata>({ category: 'theory' })
    const [error, setError] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const inputRef = useRef<HTMLInputElement>(null)

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true)
        } else if (e.type === 'dragleave') {
            setDragActive(false)
        }
    }

    const validateFile = (file: File): string | null => {
        const ext = file.name.split('.').pop()?.toLowerCase()
        if (!ext || !supportedTypes.includes(ext)) {
            return `Unsupported file type. Supported: ${supportedTypes.join(', ')}`
        }
        if (file.size > maxSize) {
            return `File too large. Maximum size: ${formatFileSize(maxSize)}`
        }
        return null
    }

    const handleFile = (file: File) => {
        const validationError = validateFile(file)
        if (validationError) {
            setError(validationError)
            return
        }
        setError(null)
        setSelectedFile(file)
        // Auto-fill title from filename
        const title = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ')
        setMetadata((prev) => ({ ...prev, title }))
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0])
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0])
        }
    }

    const handleSubmit = async () => {
        if (!selectedFile) return

        setIsLoading(true)
        setError(null)

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)
            formData.append('course_id', courseId)
            formData.append('title', metadata.title || selectedFile.name.replace(/\.[^/.]+$/, ''))
            formData.append('category', metadata.category)
            if (metadata.week_number) {
                formData.append('week_number', String(metadata.week_number))
            }
            if (metadata.tags && metadata.tags.length > 0) {
                formData.append('tags', metadata.tags.join(','))
            }

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/materials/upload`, {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(errorData.detail || 'Upload failed')
            }

            // Success - clear the form
            setSelectedFile(null)
            setMetadata({ category: 'theory' })

            // Notify parent of success
            if (onUploadSuccess) {
                onUploadSuccess()
            }
        } catch (err: any) {
            setError(err.message || 'Upload failed')
            console.error('Upload error:', err)
        }

        setIsLoading(false)
    }

    const clearFile = () => {
        setSelectedFile(null)
        setError(null)
        if (inputRef.current) {
            inputRef.current.value = ''
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Upload className="h-5 w-5" />
                    Upload Material
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Drop Zone */}
                <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive
                        ? 'border-primary bg-primary/5'
                        : 'border-muted-foreground/25 hover:border-primary/50'
                        }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        ref={inputRef}
                        type="file"
                        className="hidden"
                        onChange={handleChange}
                        accept={supportedTypes.map((t) => `.${t}`).join(',')}
                    />

                    {selectedFile ? (
                        <div className="flex items-center justify-center gap-3">
                            <File className="h-8 w-8 text-primary" />
                            <div className="text-left">
                                <p className="font-medium">{selectedFile.name}</p>
                                <p className="text-sm text-muted-foreground">
                                    {formatFileSize(selectedFile.size)}
                                </p>
                            </div>
                            <Button variant="ghost" size="sm" onClick={clearFile}>
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    ) : (
                        <>
                            <Upload className="h-10 w-10 mx-auto mb-4 text-muted-foreground" />
                            <p className="text-muted-foreground mb-2">
                                Drag and drop a file here, or
                            </p>
                            <Button variant="outline" onClick={() => inputRef.current?.click()}>
                                Browse Files
                            </Button>
                            <p className="text-xs text-muted-foreground mt-2">
                                Supported: {supportedTypes.join(', ')} (max {formatFileSize(maxSize)})
                            </p>
                        </>
                    )}
                </div>

                {error && (
                    <div className="flex items-center gap-2 text-destructive text-sm">
                        <AlertCircle className="h-4 w-4" />
                        {error}
                    </div>
                )}

                {/* Metadata Form */}
                {selectedFile && (
                    <div className="space-y-3">
                        <div>
                            <label className="text-sm font-medium">Title</label>
                            <Input
                                value={metadata.title || ''}
                                onChange={(e) => setMetadata({ ...metadata, title: e.target.value })}
                                placeholder="Enter material title"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-medium">Category</label>
                            <div className="flex gap-2 mt-1">
                                {['theory', 'lab'].map((cat) => (
                                    <Button
                                        key={cat}
                                        type="button"
                                        variant={metadata.category === cat ? 'default' : 'outline'}
                                        size="sm"
                                        onClick={() => setMetadata({ ...metadata, category: cat as 'theory' | 'lab' })}
                                        className="capitalize"
                                    >
                                        {cat}
                                    </Button>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="text-sm font-medium">Week Number (optional)</label>
                            <Input
                                type="number"
                                min={1}
                                max={52}
                                value={metadata.week_number || ''}
                                onChange={(e) =>
                                    setMetadata({
                                        ...metadata,
                                        week_number: e.target.value ? parseInt(e.target.value) : undefined,
                                    })
                                }
                                placeholder="e.g., 5"
                            />
                        </div>

                        <Button onClick={handleSubmit} disabled={isLoading} className="w-full">
                            {isLoading ? (
                                <>
                                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                    Uploading & Processing...
                                </>
                            ) : (
                                <>
                                    <Upload className="h-4 w-4 mr-2" />
                                    Upload Material
                                </>
                            )}
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

interface UploadProgressProps {
    filename: string
    progress: number
    status: 'uploading' | 'processing' | 'complete' | 'error'
    error?: string
}

export function UploadProgress({ filename, progress, status, error }: UploadProgressProps) {
    return (
        <div className="p-3 border rounded-lg">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <File className="h-4 w-4" />
                    <span className="text-sm font-medium truncate max-w-[200px]">{filename}</span>
                </div>
                {status === 'complete' && <CheckCircle className="h-4 w-4 text-green-500" />}
                {status === 'error' && <AlertCircle className="h-4 w-4 text-red-500" />}
                {(status === 'uploading' || status === 'processing') && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                )}
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                    className={`h-full transition-all ${status === 'error' ? 'bg-destructive' : 'bg-primary'
                        }`}
                    style={{ width: `${progress}%` }}
                />
            </div>
            <p className="text-xs text-muted-foreground mt-1">
                {status === 'uploading' && `Uploading... ${progress}%`}
                {status === 'processing' && 'Processing document...'}
                {status === 'complete' && 'Upload complete!'}
                {status === 'error' && (error || 'Upload failed')}
            </p>
        </div>
    )
}
