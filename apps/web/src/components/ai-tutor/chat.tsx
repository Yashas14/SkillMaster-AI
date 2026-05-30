'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Brain, Send, Loader2, Sparkles, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface AiTutorChatProps {
  userId: string;
  courseId?: string;
  lessonId?: string;
}

const PERSONAS = [
  { id: 'socratic_guide', label: 'Socratic Guide', emoji: '🏛️' },
  { id: 'friendly_peer', label: 'Friendly Peer', emoji: '🤝' },
  { id: 'strict_professor', label: 'Strict Professor', emoji: '👨‍🏫' },
  { id: 'debate_partner', label: 'Debate Partner', emoji: '⚔️' },
] as const;

export function AiTutorChat({ userId, courseId, lessonId }: AiTutorChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        "Hello! I'm your AI learning companion powered by Claude Opus 4.6. I use the Socratic method — I'll guide you by asking thought-provoking questions rather than just giving answers. What would you like to explore today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState<string>('socratic_guide');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  async function handleSend() {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessageId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      },
    ]);

    try {
      const response = await fetch('/api/ai/tutor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          user_id: userId,
          course_id: courseId,
          lesson_id: lessonId,
          persona: selectedPersona,
        }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'text') {
                  fullContent += data.content;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: fullContent }
                        : msg,
                    ),
                  );
                } else if (data.type === 'done') {
                  if (data.session_id) setSessionId(data.session_id);
                }
              } catch {
                // Skip malformed chunks
              }
            }
          }
        }
      }

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId ? { ...msg, isStreaming: false } : msg,
        ),
      );
    } catch {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: "I'm sorry, I encountered an error. Please try again.",
                isStreaming: false,
              }
            : msg,
        ),
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleNewChat() {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content:
          "Fresh start! What would you like to learn about today? I'm here to guide you through questions and exploration.",
        timestamp: new Date(),
      },
    ]);
    setSessionId(null);
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-100 dark:bg-brand-900">
            <Brain className="h-5 w-5 text-brand-600 dark:text-brand-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">
              AI Tutor · Claude Opus 4.6
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Socratic Learning Companion
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedPersona}
            onChange={(e) => setSelectedPersona(e.target.value)}
            className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
          >
            {PERSONAS.map((p) => (
              <option key={p.id} value={p.id}>
                {p.emoji} {p.label}
              </option>
            ))}
          </select>
          <button
            onClick={handleNewChat}
            className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
            title="New chat"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              'flex gap-3',
              message.role === 'user' ? 'flex-row-reverse' : 'flex-row',
            )}
          >
            <div
              className={cn(
                'flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm',
                message.role === 'user'
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800',
              )}
            >
              {message.role === 'user' ? 'You' : <Sparkles className="h-4 w-4 text-brand-600" />}
            </div>
            <div
              className={cn(
                'max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
                message.role === 'user'
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100',
              )}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              {message.isStreaming && (
                <span className="ml-1 inline-block h-4 w-1 animate-pulse bg-brand-500" />
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-200 p-4 dark:border-slate-800">
        <div className="flex items-end gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything... I'll guide you with questions"
            rows={1}
            className="max-h-32 min-h-[2.5rem] flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition-colors focus:border-brand-500 focus:bg-white focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:bg-slate-800"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
        <p className="mt-2 text-center text-xs text-slate-400 dark:text-slate-500">
          AI responses may not always be accurate. Always verify important information.
        </p>
      </div>
    </div>
  );
}
