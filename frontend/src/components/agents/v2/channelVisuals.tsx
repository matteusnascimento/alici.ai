import type { LucideIcon } from 'lucide-react';
import { Briefcase, Cable, Disc3, Globe, Instagram, Mail, MessageCircle, Send, Webhook } from 'lucide-react';

export const CHANNEL_VISUALS: Record<string, { icon: LucideIcon; accent: string }> = {
  whatsapp: { icon: MessageCircle, accent: 'from-emerald-400/25 via-emerald-400/10 to-transparent text-emerald-200' },
  instagram: { icon: Instagram, accent: 'from-rose-400/25 via-fuchsia-400/10 to-transparent text-rose-100' },
  telegram: { icon: Send, accent: 'from-sky-400/25 via-sky-400/10 to-transparent text-sky-100' },
  slack: { icon: Cable, accent: 'from-violet-400/25 via-violet-400/10 to-transparent text-violet-100' },
  discord: { icon: Disc3, accent: 'from-indigo-400/25 via-indigo-400/10 to-transparent text-indigo-100' },
  website_chat: { icon: Globe, accent: 'from-cyan-400/25 via-cyan-400/10 to-transparent text-cyan-100' },
  email: { icon: Mail, accent: 'from-sky-400/25 via-sky-400/10 to-transparent text-sky-100' },
  crm: { icon: Briefcase, accent: 'from-amber-400/25 via-amber-400/10 to-transparent text-amber-100' },
  api: { icon: Webhook, accent: 'from-cyan-400/25 via-cyan-400/10 to-transparent text-cyan-100' },
  webhook: { icon: Webhook, accent: 'from-cyan-400/25 via-cyan-400/10 to-transparent text-cyan-100' },
};