'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';

type Language = 'python' | 'javascript' | 'typescript';

const SAMPLE_CODE: Record<Language, string> = {
  python: `def fibonacci(n):
    """Return the nth Fibonacci number."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Test
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")`,
  javascript: `function quickSort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[Math.floor(arr.length / 2)];
  const left = arr.filter(x => x < pivot);
  const middle = arr.filter(x => x === pivot);
  const right = arr.filter(x => x > pivot);
  return [...quickSort(left), ...middle, ...quickSort(right)];
}

console.log(quickSort([3, 6, 8, 10, 1, 2, 1]));`,
  typescript: `interface TreeNode<T> {
  value: T;
  left: TreeNode<T> | null;
  right: TreeNode<T> | null;
}

function inorderTraversal<T>(node: TreeNode<T> | null): T[] {
  if (!node) return [];
  return [
    ...inorderTraversal(node.left),
    node.value,
    ...inorderTraversal(node.right),
  ];
}

console.log("Tree traversal ready");`,
};

export default function CodePlaygroundPage() {
  const { data: session } = useSession();
  const [language, setLanguage] = useState<Language>('python');
  const [code, setCode] = useState(SAMPLE_CODE.python);
  const [stdin, setStdin] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [review, setReview] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'output' | 'review'>('output');

  const handleRun = async () => {
    setIsRunning(true);
    setActiveTab('output');
    try {
      const res = await fetch('/api/v1/code/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, stdin }),
      });
      const data = await res.json();
      setOutput(
        data.success
          ? data.stdout || '(no output)'
          : `Error:\n${data.stderr || data.error || 'Unknown error'}`
      );
    } catch (e) {
      setOutput('Failed to execute code. Check your connection.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleReview = async () => {
    setIsReviewing(true);
    setActiveTab('review');
    try {
      const res = await fetch('/api/v1/code/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, review_type: 'comprehensive' }),
      });
      const data = await res.json();
      setReview(data);
    } catch (e) {
      setReview({ error: 'Failed to get review' });
    } finally {
      setIsReviewing(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Code Playground</h1>
          <p className="text-muted-foreground">Write, run, and get AI-powered code reviews</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={language}
            onChange={(e) => {
              const lang = e.target.value as Language;
              setLanguage(lang);
              setCode(SAMPLE_CODE[lang]);
            }}
            className="rounded-lg border bg-background px-3 py-2 text-sm"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
          </select>
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700 disabled:opacity-50"
          >
            {isRunning ? 'Running...' : '▶ Run'}
          </button>
          <button
            onClick={handleReview}
            disabled={isReviewing}
            className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700 disabled:opacity-50"
          >
            {isReviewing ? 'Reviewing...' : '🔍 AI Review'}
          </button>
        </div>
      </div>

      <div className="grid flex-1 gap-4 lg:grid-cols-2">
        {/* Editor */}
        <div className="flex flex-col overflow-hidden rounded-xl border">
          <div className="border-b bg-muted/50 px-4 py-2 text-sm font-medium">
            Editor — {language}
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 resize-none bg-[#1e1e1e] p-4 font-mono text-sm text-green-400 focus:outline-none"
            spellCheck={false}
          />
        </div>

        {/* Output Panel */}
        <div className="flex flex-col overflow-hidden rounded-xl border">
          <div className="flex border-b bg-muted/50">
            <button
              onClick={() => setActiveTab('output')}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === 'output' ? 'border-b-2 border-primary text-foreground' : 'text-muted-foreground'
              }`}
            >
              Output
            </button>
            <button
              onClick={() => setActiveTab('review')}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === 'review' ? 'border-b-2 border-primary text-foreground' : 'text-muted-foreground'
              }`}
            >
              AI Review
            </button>
          </div>

          <div className="flex-1 overflow-auto p-4">
            {activeTab === 'output' ? (
              <pre className="font-mono text-sm whitespace-pre-wrap">
                {output || 'Click "Run" to execute your code.'}
              </pre>
            ) : review ? (
              <div className="space-y-4">
                {review.error ? (
                  <p className="text-destructive">{review.error}</p>
                ) : (
                  <>
                    {review.score !== undefined && (
                      <div className="flex items-center gap-3">
                        <div className={`flex h-14 w-14 items-center justify-center rounded-full text-lg font-bold text-white ${
                          review.score >= 80 ? 'bg-green-500' :
                          review.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}>
                          {review.score}
                        </div>
                        <div>
                          <p className="font-semibold">Code Quality Score</p>
                          <p className="text-sm text-muted-foreground">{review.summary}</p>
                        </div>
                      </div>
                    )}
                    {review.issues?.length > 0 && (
                      <div>
                        <h4 className="mb-2 font-semibold">Issues</h4>
                        {review.issues.map((issue: any, i: number) => (
                          <div key={i} className={`mb-2 rounded-lg border-l-4 p-3 ${
                            issue.severity === 'error' ? 'border-red-500 bg-red-50 dark:bg-red-950' :
                            issue.severity === 'warning' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-950' :
                            'border-blue-500 bg-blue-50 dark:bg-blue-950'
                          }`}>
                            <p className="text-sm font-medium">{issue.message}</p>
                            {issue.suggestion && (
                              <p className="mt-1 text-xs text-muted-foreground">{issue.suggestion}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                    {review.strengths?.length > 0 && (
                      <div>
                        <h4 className="mb-2 font-semibold text-green-600">Strengths</h4>
                        <ul className="space-y-1 text-sm">
                          {review.strengths.map((s: string, i: number) => (
                            <li key={i} className="flex gap-2">
                              <span className="text-green-500">✓</span> {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : (
              <p className="text-muted-foreground">Click "AI Review" to get feedback on your code.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
