'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';

type ContentTab = 'content' | 'quiz' | 'notes' | 'discussion';

export default function LessonPage() {
  const params = useParams();
  const [activeTab, setActiveTab] = useState<ContentTab>('content');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [notes, setNotes] = useState('');

  // Mock lesson data
  const lesson = {
    id: params.lessonId,
    title: 'Introduction to React Hooks',
    module: 'React Fundamentals',
    course: 'Advanced React Patterns',
    content_type: 'video',
    duration: '15:30',
    completed: false,
    content: `
## React Hooks

Hooks let you use state and other React features without writing a class.

### useState

\`\`\`jsx
const [count, setCount] = useState(0);
\`\`\`

The \`useState\` hook returns a stateful value and a function to update it.

### useEffect

\`\`\`jsx
useEffect(() => {
  document.title = \`You clicked \${count} times\`;
}, [count]);
\`\`\`

### Rules of Hooks

1. Only call Hooks at the top level
2. Only call Hooks from React functions
3. Use the ESLint plugin for enforcement
    `,
  };

  const modules = [
    {
      title: 'Getting Started',
      lessons: [
        { id: '1', title: 'Course Overview', completed: true, duration: '5:00' },
        { id: '2', title: 'Setting Up Your Environment', completed: true, duration: '12:00' },
      ],
    },
    {
      title: 'React Fundamentals',
      lessons: [
        { id: '3', title: 'Components & JSX', completed: true, duration: '18:00' },
        { id: '4', title: 'Introduction to React Hooks', completed: false, duration: '15:30', current: true },
        { id: '5', title: 'Custom Hooks', completed: false, duration: '20:00' },
      ],
    },
    {
      title: 'Advanced Patterns',
      lessons: [
        { id: '6', title: 'Render Props', completed: false, duration: '14:00' },
        { id: '7', title: 'Higher-Order Components', completed: false, duration: '16:00' },
      ],
    },
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Course Sidebar */}
      {sidebarOpen && (
        <aside className="w-80 shrink-0 overflow-y-auto border-r bg-card">
          <div className="p-4">
            <h2 className="font-semibold">{lesson.course}</h2>
            <p className="text-sm text-muted-foreground">3 modules, 7 lessons</p>
          </div>
          <div className="space-y-1 px-2 pb-4">
            {modules.map((mod, mi) => (
              <div key={mi}>
                <p className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {mod.title}
                </p>
                {mod.lessons.map((l) => (
                  <button
                    key={l.id}
                    className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                      (l as any).current
                        ? 'bg-primary/10 text-primary font-medium'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`}
                  >
                    <span className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] ${
                      l.completed
                        ? 'bg-green-500 text-white'
                        : (l as any).current
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground'
                    }`}>
                      {l.completed ? '✓' : ''}
                    </span>
                    <span className="flex-1 text-left truncate">{l.title}</span>
                    <span className="text-xs text-muted-foreground">{l.duration}</span>
                  </button>
                ))}
              </div>
            ))}
          </div>
        </aside>
      )}

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="flex items-center justify-between border-b px-4 py-2">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="rounded p-1 hover:bg-muted">
              ☰
            </button>
            <div>
              <p className="text-xs text-muted-foreground">{lesson.module}</p>
              <h1 className="font-semibold">{lesson.title}</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="rounded-lg border px-3 py-1.5 text-sm hover:bg-muted">
              ← Previous
            </button>
            <button className="rounded-lg bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground">
              Mark Complete & Next →
            </button>
          </div>
        </div>

        {/* Content Tabs */}
        <div className="flex border-b">
          {(['content', 'quiz', 'notes', 'discussion'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2.5 text-sm font-medium capitalize transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-primary text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'content' && (
            <div className="mx-auto max-w-3xl">
              {/* Video placeholder */}
              <div className="mb-6 flex aspect-video items-center justify-center rounded-xl bg-gray-900 text-white">
                <div className="text-center">
                  <div className="text-5xl">▶</div>
                  <p className="mt-2 text-sm text-gray-400">{lesson.duration}</p>
                </div>
              </div>
              {/* Markdown content */}
              <div className="prose dark:prose-invert max-w-none">
                <pre className="whitespace-pre-wrap text-sm">{lesson.content}</pre>
              </div>
            </div>
          )}

          {activeTab === 'quiz' && (
            <div className="mx-auto max-w-2xl space-y-6">
              <div className="rounded-xl border p-6 text-center">
                <h3 className="text-lg font-semibold">Lesson Quiz</h3>
                <p className="mt-1 text-muted-foreground">
                  Test your understanding of React Hooks
                </p>
                <button className="mt-4 rounded-lg bg-primary px-6 py-2 text-sm font-medium text-primary-foreground">
                  Generate Adaptive Quiz
                </button>
                <p className="mt-2 text-xs text-muted-foreground">
                  Powered by Claude Opus 4.6
                </p>
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="mx-auto max-w-2xl">
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Take notes on this lesson..."
                className="min-h-[400px] w-full rounded-xl border bg-background p-4 text-sm"
              />
              <div className="mt-3 flex justify-end">
                <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
                  Save Notes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'discussion' && (
            <div className="mx-auto max-w-2xl space-y-4">
              <div className="rounded-xl border p-4 text-center text-muted-foreground">
                <p>No discussions yet. Ask a question or share an insight!</p>
                <button className="mt-3 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
                  Start a Discussion
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
