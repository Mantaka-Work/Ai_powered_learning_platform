import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api` : 'http://localhost:8000/api'

// Create axios instance
const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            window.location.href = '/auth/login'
        }
        return Promise.reject(error)
    }
)

// Types
export interface SearchResult {
    id: string
    content: string
    material_id: string
    material_title: string
    file_type: string
    category: string
    relevance_score: number
}

export interface WebSearchResult {
    title: string
    url: string
    snippet: string
    source_domain: string
}

export interface SearchResponse {
    query: string
    course_results: SearchResult[]
    web_results: WebSearchResult[]
    took_ms: number
    used_web_search: boolean
    average_relevance: number
}

export interface GenerationResponse {
    id: string
    status: string
    type: string
    topic: string
    content: string
    validation_status?: string
    validation_score?: number
    sources: {
        course?: { title: string; type: string; relevance: number }[]
        web?: { title: string; url: string }[]
    }
    used_web_search: boolean
}

export interface ChatMessage {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: any[]
    used_web_search?: boolean
    created_at: string
}

export interface ChatSession {
    id: string
    title: string
    course_id: string
    message_count: number
    created_at: string
    updated_at: string
}

// API Functions

// Auth
export const authApi = {
    login: async (email: string, password: string) => {
        const response = await api.post('/auth/login', { email, password })
        return response.data
    },
    register: async (email: string, password: string, fullName?: string) => {
        const response = await api.post('/auth/register', { email, password, full_name: fullName })
        return response.data
    },
    logout: async () => {
        const response = await api.post('/auth/logout')
        localStorage.removeItem('access_token')
        return response.data
    },
}

// Materials
export const materialsApi = {
    upload: async (courseId: string, file: File, metadata: any) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('metadata', JSON.stringify(metadata))

        const response = await api.post(`/materials/${courseId}/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return response.data
    },
    list: async (courseId: string, filters?: any) => {
        const response = await api.get(`/materials/${courseId}`, { params: filters })
        return response.data
    },
    get: async (materialId: string) => {
        const response = await api.get(`/materials/item/${materialId}`)
        return response.data
    },
    delete: async (courseId: string, materialId: string) => {
        const response = await api.delete(`/materials/${courseId}/${materialId}`)
        return response.data
    },
}

// Search
export const searchApi = {
    semantic: async (courseId: string, query: string, limit = 10): Promise<SearchResponse> => {
        const response = await api.post('/search/semantic', {
            course_id: courseId,
            query,
            limit,
        })
        return response.data
    },
    hybrid: async (
        courseId: string,
        query: string,
        includeWeb?: boolean,
        limit = 10
    ): Promise<SearchResponse> => {
        const response = await api.post('/search/hybrid', {
            course_id: courseId,
            query,
            include_web: includeWeb,
            limit,
        })
        return response.data
    },
    web: async (query: string, limit = 10): Promise<SearchResponse> => {
        const response = await api.post('/search/web', { query, limit })
        return response.data
    },
}

// Generation
export const generateApi = {
    theory: async (
        courseId: string,
        topic: string,
        type = 'notes',
        useWeb = false
    ): Promise<GenerationResponse> => {
        const response = await api.post('/generate/theory', {
            course_id: courseId,
            topic,
            type,
            use_web: useWeb,
        })
        return response.data
    },
    code: async (
        courseId: string,
        topic: string,
        language: string,
        type = 'example',
        useWeb = false
    ): Promise<GenerationResponse> => {
        const response = await api.post('/generate/code', {
            course_id: courseId,
            topic,
            language,
            type,
            use_web: useWeb,
        })
        return response.data
    },
    history: async (courseId: string, type?: string) => {
        const response = await api.get(`/generate/history/${courseId}`, { params: { type } })
        return response.data
    },
}

// Chat
export const chatApi = {
    createSession: async (courseId: string, title?: string): Promise<ChatSession> => {
        const response = await api.post('/chat/sessions', { course_id: courseId, title })
        return response.data
    },
    getSessions: async (courseId?: string): Promise<ChatSession[]> => {
        const response = await api.get('/chat/sessions', { params: { course_id: courseId } })
        return response.data
    },
    getHistory: async (sessionId: string): Promise<{ session: ChatSession; messages: ChatMessage[] }> => {
        const response = await api.get(`/chat/sessions/${sessionId}`)
        return response.data
    },
    sendMessage: async (
        sessionId: string,
        courseId: string,
        content: string,
        includeWebSearch?: boolean
    ): Promise<{ message: ChatMessage; sources: any }> => {
        const response = await api.post(`/chat/message/sync`, {
            session_id: sessionId,
            course_id: courseId,
            message: content,
            include_web_search: includeWebSearch ?? false,
        })
        return response.data
    },
    deleteSession: async (sessionId: string) => {
        const response = await api.delete(`/chat/sessions/${sessionId}`)
        return response.data
    },
}

// Validation
export const validationApi = {
    validateCode: async (code: string, language: string, execute = false) => {
        const response = await api.post('/validate/code', { code, language, execute })
        return response.data
    },
    validateContent: async (content: string, contentType: string) => {
        const response = await api.post('/validate/content', { content, content_type: contentType })
        return response.data
    },
}

export default api
