import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    })
}

export function formatFileSize(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024
        unitIndex++
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`
}

export function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength - 3) + '...'
}

export function getValidationEmoji(status: string): string {
    const mapping: Record<string, string> = {
        validated: '✅',
        warning: '⚠️',
        failed: '❌',
        pending: '⏳',
    }
    return mapping[status.toLowerCase()] || '❓'
}

export function getSourceIcon(type: 'course' | 'web'): string {
    return type === 'course' ? '📚' : '🌐'
}
