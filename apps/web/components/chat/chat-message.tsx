export default function ChatMessage({ role, content }: { role: string; content: string }) {
  const isAssistant = role === "assistant"
  return (
    <div className={`rounded-xl px-4 py-3 ${isAssistant ? "border border-slate-200 bg-white" : "bg-primary text-white"}`}>
      <div className="text-[10px] uppercase opacity-70">{role}</div>
      <div className="text-sm">{content}</div>
    </div>
  )
}
