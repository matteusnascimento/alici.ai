import Link from "next/link"

const links = [
  ["Dashboard", "/dashboard"],
  ["Agents", "/agents"],
  ["Chat", "/chat"],
  ["Workflows", "/workflows"],
  ["Knowledge", "/knowledge"],
  ["Analytics", "/analytics"],
  ["Settings", "/settings"],
]

export default function Sidebar() {
  return (
    <aside className="w-60 border-r border-slate-200 bg-white">
      <div className="p-4 text-lg font-bold text-primary">Alici</div>
      <nav className="space-y-1 p-2">
        {links.map(([name, href]) => (
          <Link key={href} href={href} className="block rounded-md px-3 py-2 text-sm hover:bg-slate-100">
            {name}
          </Link>
        ))}
      </nav>
    </aside>
  )
}
