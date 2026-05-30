'use client';

import { useState } from 'react';

export default function LearningPathPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [goal, setGoal] = useState('');
  const [skills, setSkills] = useState('');
  const [targetSkills, setTargetSkills] = useState('');
  const [weeklyHours, setWeeklyHours] = useState(10);
  const [isGenerating, setIsGenerating] = useState(false);

  // Mock learning paths data
  const paths = [
    {
      id: '1',
      title: 'Full-Stack Web Development',
      goal: 'Become a full-stack developer',
      status: 'active',
      progress: 45,
      estimated_weeks: 12,
      items: [
        { title: 'HTML & CSS Fundamentals', status: 'completed', hours: 8 },
        { title: 'JavaScript Deep Dive', status: 'completed', hours: 15 },
        { title: 'React.js Mastery', status: 'in_progress', hours: 20 },
        { title: 'Node.js & Express', status: 'not_started', hours: 15 },
        { title: 'Database Design', status: 'not_started', hours: 10 },
        { title: 'Capstone Project', status: 'not_started', hours: 25 },
      ],
    },
  ];

  const handleCreate = async () => {
    setIsGenerating(true);
    // In production: POST /api/v1/learning-paths/
    await new Promise((r) => setTimeout(r, 2000));
    setIsGenerating(false);
    setShowCreate(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Learning Paths</h1>
          <p className="text-muted-foreground">AI-generated personalized learning journeys</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          + Create New Path
        </button>
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-2xl bg-card p-6 shadow-xl">
            <h2 className="text-lg font-semibold">Create Learning Path</h2>
            <p className="text-sm text-muted-foreground">
              Tell us your goal and we&apos;ll generate a personalized path using AI.
            </p>
            <div className="mt-4 space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium">Learning Goal</label>
                <textarea
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="e.g., Become a machine learning engineer..."
                  className="w-full rounded-lg border bg-background p-3 text-sm"
                  rows={3}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium">Current Skills</label>
                <input
                  type="text"
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  placeholder="Python, Basic Math, Git..."
                  className="w-full rounded-lg border bg-background p-3 text-sm"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium">Target Skills</label>
                <input
                  type="text"
                  value={targetSkills}
                  onChange={(e) => setTargetSkills(e.target.value)}
                  placeholder="TensorFlow, Deep Learning, MLOps..."
                  className="w-full rounded-lg border bg-background p-3 text-sm"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium">
                  Weekly Study Hours: {weeklyHours}h
                </label>
                <input
                  type="range"
                  min={1}
                  max={40}
                  value={weeklyHours}
                  onChange={(e) => setWeeklyHours(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
            <div className="mt-6 flex gap-3 justify-end">
              <button
                onClick={() => setShowCreate(false)}
                className="rounded-lg border px-4 py-2 text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={!goal || isGenerating}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
              >
                {isGenerating ? 'Generating with AI...' : 'Generate Path'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Paths List */}
      {paths.map((path) => (
        <div key={path.id} className="rounded-xl border bg-card">
          <div className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold">{path.title}</h2>
                <p className="text-sm text-muted-foreground">{path.goal}</p>
              </div>
              <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                {path.status}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-sm">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">{path.progress}%</span>
              </div>
              <div className="h-2 rounded-full bg-muted">
                <div
                  className="h-2 rounded-full bg-primary transition-all"
                  style={{ width: `${path.progress}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Est. {path.estimated_weeks} weeks
              </p>
            </div>

            {/* Path Items */}
            <div className="mt-6 space-y-3">
              {path.items.map((item, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-3 rounded-lg border p-3 transition-colors ${
                    item.status === 'completed'
                      ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950'
                      : item.status === 'in_progress'
                        ? 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950'
                        : ''
                  }`}
                >
                  <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${
                    item.status === 'completed'
                      ? 'bg-green-500 text-white'
                      : item.status === 'in_progress'
                        ? 'bg-blue-500 text-white'
                        : 'bg-muted text-muted-foreground'
                  }`}>
                    {item.status === 'completed' ? '✓' : i + 1}
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${item.status === 'completed' ? 'line-through text-muted-foreground' : ''}`}>
                      {item.title}
                    </p>
                    <p className="text-xs text-muted-foreground">{item.hours}h estimated</p>
                  </div>
                  {item.status === 'in_progress' && (
                    <span className="text-xs font-medium text-blue-600">In Progress</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
