import Link from "next/link"

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
        <h1 className="text-2xl font-bold">Login</h1>
        <p className="mt-1 text-sm text-slate-500">Alici AI Platform</p>
        <div className="mt-6 space-y-3">
          <input className="w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="Email" />
          <input className="w-full rounded-lg border border-slate-300 px-3 py-2" type="password" placeholder="Password" />
          <Link href="/dashboard" className="block rounded-lg bg-primary px-4 py-2 text-center text-white">Sign in</Link>
        </div>
      </section>
    </main>
  )
}
