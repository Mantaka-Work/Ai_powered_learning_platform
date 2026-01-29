import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Auth helpers
export const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
    })
    // Store the access token for API calls
    if (data?.session?.access_token) {
        localStorage.setItem('access_token', data.session.access_token)
    }
    return { data, error }
}

export const signUp = async (email: string, password: string, fullName?: string) => {
    const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
            data: {
                full_name: fullName,
            },
        },
    })
    return { data, error }
}

export const signOut = async () => {
    localStorage.removeItem('access_token')
    const { error } = await supabase.auth.signOut()
    return { error }
}

export const getUser = async () => {
    const { data: { user }, error } = await supabase.auth.getUser()
    return { user, error }
}

export const getSession = async () => {
    const { data: { session }, error } = await supabase.auth.getSession()
    return { session, error }
}
