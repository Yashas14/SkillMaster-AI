import type { Metadata } from 'next';
import { AiTutorChat } from '@/components/ai-tutor/chat';
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'AI Tutor',
};

export default async function AiTutorPage() {
  const session = await auth();
  if (!session?.user) redirect('/login');

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-4xl flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">AI Tutor</h1>
        <p className="mt-1 text-slate-600 dark:text-slate-400">
          Your personal Socratic learning companion powered by Claude Opus 4.6
        </p>
      </div>
      <AiTutorChat userId={session.user.id!} />
    </div>
  );
}
