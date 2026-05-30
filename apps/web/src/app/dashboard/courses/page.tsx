import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { BookOpen, Search } from 'lucide-react';

export const metadata = {
  title: 'My Courses',
};

export default async function CoursesPage() {
  const session = await auth();
  if (!session?.user) redirect('/login');

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Courses</h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Track your progress and continue learning
          </p>
        </div>
        <Link
          href="/courses"
          className="flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <BookOpen className="h-4 w-4" />
          Browse More
        </Link>
      </div>

      {/* Search & Filter */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search your courses..."
            className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-4 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
          />
        </div>
        <select className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white">
          <option>All Status</option>
          <option>In Progress</option>
          <option>Completed</option>
          <option>Not Started</option>
        </select>
      </div>

      {/* Course List */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[
          {
            id: '1',
            title: 'Full-Stack AI Development with Next.js & Python',
            instructor: 'Dr. Sarah Chen',
            progress: 25,
            totalLessons: 42,
            completedLessons: 10,
            category: 'AI/ML',
            difficulty: 'Intermediate',
            lastAccessed: '2 hours ago',
          },
          {
            id: '2',
            title: 'Introduction to Machine Learning with PyTorch',
            instructor: 'Dr. Sarah Chen',
            progress: 10,
            totalLessons: 30,
            completedLessons: 3,
            category: 'AI/ML',
            difficulty: 'Beginner',
            lastAccessed: '1 day ago',
          },
        ].map((course) => (
          <Link
            key={course.id}
            href={`/dashboard/courses/${course.id}`}
            className="group overflow-hidden rounded-xl border border-slate-200 bg-white transition-all hover:border-slate-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700"
          >
            <div className="aspect-video bg-gradient-to-br from-brand-500 via-brand-600 to-purple-600 p-4">
              <div className="flex items-center justify-between">
                <span className="rounded-md bg-white/20 px-2 py-1 text-xs font-medium text-white backdrop-blur">
                  {course.category}
                </span>
                <span className="rounded-md bg-white/20 px-2 py-1 text-xs font-medium text-white backdrop-blur">
                  {course.difficulty}
                </span>
              </div>
            </div>
            <div className="p-4">
              <h3 className="line-clamp-2 font-semibold text-slate-900 group-hover:text-brand-600 dark:text-white dark:group-hover:text-brand-400">
                {course.title}
              </h3>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                {course.instructor}
              </p>
              <div className="mt-3">
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="text-slate-500">
                    {course.completedLessons}/{course.totalLessons} lessons
                  </span>
                  <span className="font-medium text-brand-600">{course.progress}%</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                  <div
                    className="h-full rounded-full bg-brand-600 transition-all"
                    style={{ width: `${course.progress}%` }}
                  />
                </div>
              </div>
              <p className="mt-3 text-xs text-slate-400 dark:text-slate-500">
                Last accessed {course.lastAccessed}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
