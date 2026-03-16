export type Message = {
  id: string
  conversation_id: string
  role: "user" | "assistant" | "system"
  content: string
}
