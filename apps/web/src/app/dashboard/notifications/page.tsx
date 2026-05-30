'use client';

import { useState } from 'react';

export default function NotificationsPage() {
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [notifications, setNotifications] = useState([
    {
      id: '1',
      type: 'achievement',
      title: 'Badge Earned: Quick Learner',
      message: 'You completed 5 lessons in one day!',
      read: false,
      created_at: '2024-03-15T10:30:00Z',
    },
    {
      id: '2',
      type: 'course',
      title: 'New Module Available',
      message: 'Advanced Patterns module has been added to your enrolled course.',
      read: false,
      created_at: '2024-03-14T15:00:00Z',
    },
    {
      id: '3',
      type: 'certificate',
      title: 'Certificate Ready',
      message: 'Your certificate for Python for Data Science is ready to download.',
      read: true,
      created_at: '2024-03-13T09:00:00Z',
    },
    {
      id: '4',
      type: 'streak',
      title: 'Streak Alert',
      message: "Don't break your 7-day streak! Complete a lesson today.",
      read: true,
      created_at: '2024-03-12T08:00:00Z',
    },
    {
      id: '5',
      type: 'system',
      title: 'Platform Update',
      message: 'New code playground with AI review is now available.',
      read: true,
      created_at: '2024-03-10T12:00:00Z',
    },
  ]);

  const typeIcons: Record<string, string> = {
    achievement: '🏆',
    course: '📚',
    certificate: '📜',
    streak: '🔥',
    system: '⚙️',
  };

  const typeColors: Record<string, string> = {
    achievement: 'bg-yellow-100 dark:bg-yellow-900',
    course: 'bg-blue-100 dark:bg-blue-900',
    certificate: 'bg-purple-100 dark:bg-purple-900',
    streak: 'bg-orange-100 dark:bg-orange-900',
    system: 'bg-gray-100 dark:bg-gray-800',
  };

  const markRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
    );
  };

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const filtered =
    filter === 'unread' ? notifications.filter((n) => !n.read) : notifications;
  const unreadCount = notifications.filter((n) => !n.read).length;

  const formatTime = (iso: string) => {
    const d = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return d.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Notifications</h1>
          <p className="text-muted-foreground">
            {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up!'}
          </p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={markAllRead}
            className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted"
          >
            Mark All Read
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {(['all', 'unread'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-lg px-4 py-2 text-sm font-medium capitalize transition-colors ${
              filter === f
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:text-foreground'
            }`}
          >
            {f} {f === 'unread' && unreadCount > 0 && `(${unreadCount})`}
          </button>
        ))}
      </div>

      {/* Notification List */}
      <div className="space-y-2">
        {filtered.length === 0 ? (
          <div className="rounded-xl border bg-card p-12 text-center text-muted-foreground">
            <p className="text-4xl">🔔</p>
            <p className="mt-2">No notifications to show</p>
          </div>
        ) : (
          filtered.map((n) => (
            <div
              key={n.id}
              className={`group flex items-start gap-4 rounded-xl border p-4 transition-colors ${
                !n.read ? 'border-primary/30 bg-primary/5' : 'bg-card'
              }`}
            >
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-lg ${
                  typeColors[n.type] || 'bg-muted'
                }`}
              >
                {typeIcons[n.type] || '📋'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium">{n.title}</h3>
                  {!n.read && (
                    <span className="h-2 w-2 rounded-full bg-primary" />
                  )}
                </div>
                <p className="mt-0.5 text-sm text-muted-foreground">{n.message}</p>
                <p className="mt-1 text-xs text-muted-foreground">{formatTime(n.created_at)}</p>
              </div>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {!n.read && (
                  <button
                    onClick={() => markRead(n.id)}
                    className="rounded p-1.5 text-xs text-muted-foreground hover:bg-muted"
                    title="Mark as read"
                  >
                    ✓
                  </button>
                )}
                <button
                  onClick={() => deleteNotification(n.id)}
                  className="rounded p-1.5 text-xs text-muted-foreground hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-900"
                  title="Delete"
                >
                  ✗
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
