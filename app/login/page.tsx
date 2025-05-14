'use client'

import Link from "next/link"
import { createClient } from "@/utils/supabase/client"
import { useRouter } from "next/navigation"
import { useCallback } from "react"

export default function Login({ searchParams }: { searchParams: { message: string } }) {
  const router = useRouter();
  const handleGoogleSignIn = useCallback(async () => {
    const supabase = createClient();
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
  }, []);

  return (
    <div className="flex-1 flex flex-col w-full px-8 sm:max-w-md justify-center gap-2">
      <Link
        href="/"
        className="absolute left-8 top-8 py-2 px-4 rounded-md no-underline text-foreground bg-btn-background hover:bg-btn-background-hover flex items-center group text-sm"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="mr-2 h-4 w-4 transition-transform group-hover:-translate-x-1"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>{" "}
        Back
      </Link>

      <div className="animate-in flex-1 flex flex-col w-full justify-center gap-2 text-foreground">
        <button
          onClick={handleGoogleSignIn}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded flex items-center justify-center gap-2"
        >
          <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g clipPath="url(#clip0_17_40)">
              <path d="M47.5 24.5C47.5 22.6 47.3 20.8 47 19H24V29.1H37.4C36.7 32.2 34.7 34.7 31.9 36.3V42.1H39.5C44 38.1 47.5 32.1 47.5 24.5Z" fill="#4285F4"/>
              <path d="M24 48C30.6 48 36.1 45.9 39.5 42.1L31.9 36.3C30.1 37.5 27.8 38.3 24 38.3C17.7 38.3 12.2 34.2 10.3 28.7H2.5V34.7C5.9 41.1 14.2 48 24 48Z" fill="#34A853"/>
              <path d="M10.3 28.7C9.7 26.5 9.7 24.2 10.3 22V16H2.5C0.5 19.8 0.5 24.2 2.5 28L10.3 28.7Z" fill="#FBBC05"/>
              <path d="M24 9.7C27.8 9.7 30.1 11.5 31.2 12.6L39.6 5.2C36.1 1.7 30.6 0 24 0C14.2 0 5.9 6.9 2.5 13.3L10.3 19.3C12.2 13.8 17.7 9.7 24 9.7Z" fill="#EA4335"/>
            </g>
            <defs>
              <clipPath id="clip0_17_40">
                <rect width="48" height="48" fill="white"/>
              </clipPath>
            </defs>
          </svg>
          Sign in with Google
        </button>
        {searchParams?.message && (
          <p className="mt-4 p-4 bg-foreground/10 text-foreground text-center">
            {searchParams.message}
          </p>
        )}
      </div>
    </div>
  )
}
