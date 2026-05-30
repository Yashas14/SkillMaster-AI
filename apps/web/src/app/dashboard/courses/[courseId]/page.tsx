'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import Link from 'next/link';

export default function CourseDetailPage() {
  const params = useParams();
  const [activeTab, setActiveTab] = useState('overview');
  const [enrolled, setEnrolled] = useState(false);

  // Mock course data
  const course = {
    id: params.courseId,
    title: 'Advanced React Patterns',
    description:
      'Master advanced React patterns including Hooks, Context, Suspense, Server Components, and more. Build production-ready applications with modern architecture.',
    instructor: 'Jane Doe',
    level: 'Advanced',
    category: 'Web Development',
    rating: 4.8,
    review_count: 243,
    student_count: 1250,
    duration: '24 hours',
    lessons_count: 42,
    updated_at: '2024-03-01',
    price: 49.99,
    thumbnail: null,
    tags: ['React', 'TypeScript', 'Next.js', 'Hooks'],
    what_you_learn: [
      'Advanced hook patterns and custom hooks',
      'Render props and higher-order components',
      'State management with Context and Zustand',
      'Server Components and streaming SSR',
      'Performance optimization techniques',
      'Testing strategies for React applications',
    ],
    modules: [
      {
        id: '1',
        title: 'Getting Started',
        lessons: [
          { id: '1', title: 'Course Overview', duration: '5:00', free: true },
          { id: '2', title: 'Setting Up Your Environment', duration: '12:00', free: true },
        ],
      },
      {
        id: '2',
        title: 'React Fundamentals Review',
        lessons: [
          { id: '3', title: 'Components & JSX', duration: '18:00', free: false },
          { id: '4', title: 'Introduction to React Hooks', duration: '15:30', free: false },
          { id: '5', title: 'Custom Hooks', duration: '20:00', free: false },
        ],
      },
      {
        id: '3',
        title: 'Advanced Patterns',
        lessons: [
          { id: '6', title: 'Render Props', duration: '14:00', free: false },
          { id: '7', title: 'Higher-Order Components', duration: '16:00', free: false },
          { id: '8', title: 'Compound Components', duration: '22:00', free: false },
        ],
      },
    ],
    reviews: [
      {
        name: 'Alex M.',
        rating: 5,
        date: '2024-02-28',
        comment: 'Best React course I have taken. The advanced patterns section is gold.',
      },
      {
        name: 'Sarah K.',
        rating: 4,
        date: '2024-02-15',
        comment: 'Very comprehensive. Would love more exercises though.',
      },
    ],
  };

  const totalLessons = course.modules.reduce((sum, m) => sum + m.lessons.length, 0);

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-white">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 text-sm text-white/80">
              <span>{course.category}</span>
              <span>•</span>
              <span>{course.level}</span>
            </div>
            <h1 className="mt-2 text-3xl font-bold">{course.title}</h1>
            <p className="mt-3 text-white/90">{course.description}</p>
            <div className="mt-4 flex flex-wrap items-center gap-4 text-sm">
              <span>By {course.instructor}</span>
              <span>★ {course.rating} ({course.review_count} reviews)</span>
              <span>{course.student_count.toLocaleString()} students</span>
              <span>{course.duration}</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {course.tags.map((tag) => (
                <span key={tag} className="rounded-full bg-white/20 px-3 py-1 text-xs">
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <div className="shrink-0 rounded-xl bg-white/10 p-6 backdrop-blur-sm lg:w-72">
            <div className="text-3xl font-bold">${course.price}</div>
            {!enrolled ? (
              <button
                onClick={() => setEnrolled(true)}
                className="mt-3 w-full rounded-lg bg-white px-4 py-3 font-semibold text-blue-600 hover:bg-white/90"
              >
                Enroll Now
              </button>
            ) : (
              <Link
                href={`/dashboard/courses/${course.id}/lessons/1`}
                className="mt-3 block w-full rounded-lg bg-green-500 px-4 py-3 text-center font-semibold text-white hover:bg-green-600"
              >
                Continue Learning
              </Link>
            )}
            <div className="mt-4 space-y-2 text-sm text-white/80">
              <p>{totalLessons} lessons</p>
              <p>{course.modules.length} modules</p>
              <p>Certificate of completion</p>
              <p>Lifetime access</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {['overview', 'curriculum', 'reviews'].map((tab) => (
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
      {activeTab === 'overview' && (
        <div className="rounded-xl border bg-card p-6">
          <h2 className="text-lg font-semibold">What You&apos;ll Learn</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {course.what_you_learn.map((item, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="mt-0.5 text-green-500">✓</span>
                <span className="text-sm">{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'curriculum' && (
        <div className="space-y-3">
          {course.modules.map((mod) => (
            <div key={mod.id} className="rounded-xl border bg-card overflow-hidden">
              <div className="border-b bg-muted/50 px-4 py-3">
                <h3 className="font-semibold">{mod.title}</h3>
                <p className="text-xs text-muted-foreground">{mod.lessons.length} lessons</p>
              </div>
              <div className="divide-y">
                {mod.lessons.map((lesson) => (
                  <div key={lesson.id} className="flex items-center gap-3 px-4 py-3">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs">
                      ▶
                    </span>
                    <span className="flex-1 text-sm">{lesson.title}</span>
                    {lesson.free && (
                      <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900 dark:text-green-300">
                        Free Preview
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">{lesson.duration}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'reviews' && (
        <div className="space-y-4">
          <div className="flex items-center gap-4 rounded-xl border bg-card p-6">
            <div className="text-center">
              <div className="text-4xl font-bold">{course.rating}</div>
              <div className="text-sm text-muted-foreground">{course.review_count} reviews</div>
            </div>
          </div>
          {course.reviews.map((review, i) => (
            <div key={i} className="rounded-xl border bg-card p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                  {review.name[0]}
                </div>
                <div>
                  <p className="font-medium">{review.name}</p>
                  <p className="text-xs text-muted-foreground">{review.date}</p>
                </div>
                <div className="ml-auto text-yellow-500">
                  {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
                </div>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{review.comment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
