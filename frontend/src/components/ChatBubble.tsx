import DOMPurify from 'dompurify'
import { Loader2, Wrench } from 'lucide-react'
import { marked } from 'marked'

export type ChatDisplayMessage =
  | { kind: 'user'; text: string }
  | { kind: 'agent'; text: string }
  | { kind: 'tool_activity'; label: string; pending?: boolean }

export default function ChatBubble({ message }: { message: ChatDisplayMessage }) {
  if (message.kind === 'tool_activity') {
    return (
      <div className="flex items-center gap-2 py-1 pl-1 text-xs text-slate-400">
        {message.pending ? <Loader2 size={12} className="animate-spin" /> : <Wrench size={12} />}
        <span>{message.label}</span>
      </div>
    )
  }

  const isUser = message.kind === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] whitespace-pre-wrap rounded-2xl bg-slate-900 px-4 py-2 text-sm text-white">
          {message.text}
        </div>
      </div>
    )
  }

  const html = DOMPurify.sanitize(marked.parse(message.text, { async: false }) as string)
  return (
    <div className="flex justify-start">
      <div
        className="chat-markdown max-w-[75%] rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-800 [&_ol]:my-1 [&_ol]:list-decimal [&_ol]:pl-5 [&_p]:my-1 [&_strong]:font-semibold [&_table]:my-2 [&_table]:w-full [&_td]:border [&_td]:border-slate-200 [&_td]:px-2 [&_td]:py-1 [&_th]:border [&_th]:border-slate-200 [&_th]:bg-slate-50 [&_th]:px-2 [&_th]:py-1 [&_ul]:my-1 [&_ul]:list-disc [&_ul]:pl-5"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  )
}
