// ════════════════════════════════════════════════════════════
// Database Seed Script
// ════════════════════════════════════════════════════════════

import 'dotenv/config';
import { createDb } from './index';
import { users, courses, courseModules, lessons, enrollments } from './schema';
import { randomUUID } from 'crypto';

async function seed() {
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error('DATABASE_URL is required');
  }

  const db = createDb(databaseUrl);
  console.log('🌱 Seeding database...');

  // Create admin user
  const adminId = randomUUID();
  const instructorId = randomUUID();
  const studentId = randomUUID();

  await db.insert(users).values([
    {
      id: adminId,
      email: 'admin@skillmaster.ai',
      name: 'Admin User',
      role: 'admin',
      isVerified: true,
      onboardingCompleted: true,
    },
    {
      id: instructorId,
      email: 'instructor@skillmaster.ai',
      name: 'Dr. Sarah Chen',
      displayName: 'Dr. Chen',
      role: 'instructor',
      bio: 'PhD in Computer Science with 15 years of teaching experience. Specializing in AI/ML and distributed systems.',
      headline: 'AI Researcher & Educator',
      isVerified: true,
      onboardingCompleted: true,
      profile: {
        skills: ['Python', 'Machine Learning', 'Deep Learning', 'NLP'],
        interests: ['AI Ethics', 'Education Technology'],
        learningGoals: [],
        experienceLevel: 'expert',
        education: 'PhD Computer Science, MIT',
        occupation: 'Professor',
      },
    },
    {
      id: studentId,
      email: 'student@skillmaster.ai',
      name: 'Alex Johnson',
      role: 'student',
      isVerified: true,
      onboardingCompleted: true,
      profile: {
        skills: ['JavaScript', 'React'],
        interests: ['Web Development', 'AI'],
        learningGoals: ['Master full-stack development', 'Learn machine learning'],
        experienceLevel: 'intermediate',
      },
    },
  ]);

  // Create courses
  const course1Id = randomUUID();
  const course2Id = randomUUID();

  await db.insert(courses).values([
    {
      id: course1Id,
      title: 'Full-Stack AI Development with Next.js & Python',
      slug: 'fullstack-ai-development',
      description:
        'Master the art of building AI-powered web applications using Next.js, FastAPI, and modern AI APIs. This comprehensive course covers everything from setting up your development environment to deploying production-ready AI features.',
      shortDescription:
        'Build AI-powered full-stack applications with Next.js 15 and FastAPI.',
      instructorId: instructorId,
      category: 'ai_ml',
      difficulty: 'intermediate',
      tags: ['nextjs', 'python', 'fastapi', 'ai', 'full-stack'],
      status: 'published',
      price: 49.99,
      currency: 'USD',
      isFree: false,
      estimatedDurationMinutes: 1800,
      totalLessons: 42,
      totalModules: 8,
      rating: 4.8,
      totalRatings: 128,
      totalEnrollments: 1542,
      prerequisites: ['Basic JavaScript', 'Basic Python'],
      learningOutcomes: [
        'Build production-ready AI applications',
        'Integrate Claude, GPT-4, and other AI models',
        'Design scalable full-stack architectures',
        'Implement RAG pipelines for custom AI assistants',
      ],
      targetAudience: [
        'Intermediate developers',
        'Frontend developers wanting to learn AI',
        'Backend developers wanting full-stack skills',
      ],
      publishedAt: new Date(),
    },
    {
      id: course2Id,
      title: 'Introduction to Machine Learning with PyTorch',
      slug: 'intro-machine-learning-pytorch',
      description:
        'Start your machine learning journey with PyTorch. Learn neural networks, CNNs, RNNs, and transformers from scratch with hands-on projects.',
      shortDescription: 'Learn ML fundamentals and build neural networks with PyTorch.',
      instructorId: instructorId,
      category: 'ai_ml',
      difficulty: 'beginner',
      tags: ['python', 'pytorch', 'machine-learning', 'deep-learning'],
      status: 'published',
      price: 0,
      currency: 'USD',
      isFree: true,
      estimatedDurationMinutes: 1200,
      totalLessons: 30,
      totalModules: 6,
      rating: 4.6,
      totalRatings: 256,
      totalEnrollments: 5230,
      prerequisites: ['Python basics', 'Basic math'],
      learningOutcomes: [
        'Understand core ML concepts',
        'Build and train neural networks',
        'Work with CNNs for computer vision',
        'Implement NLP models with transformers',
      ],
      targetAudience: ['Beginners to ML', 'Python developers', 'Data analysts'],
      publishedAt: new Date(),
    },
  ]);

  // Create modules for course 1
  const module1Id = randomUUID();
  const module2Id = randomUUID();

  await db.insert(courseModules).values([
    {
      id: module1Id,
      courseId: course1Id,
      title: 'Getting Started with AI Development',
      description: 'Set up your environment and understand the AI development landscape.',
      order: 1,
      estimatedDurationMinutes: 120,
    },
    {
      id: module2Id,
      courseId: course1Id,
      title: 'Building Your First AI Feature',
      description: 'Integrate Claude API and build a streaming chat interface.',
      order: 2,
      estimatedDurationMinutes: 180,
    },
  ]);

  // Create lessons
  await db.insert(lessons).values([
    {
      id: randomUUID(),
      moduleId: module1Id,
      courseId: course1Id,
      title: 'Course Overview & Architecture',
      description: 'Understand the full-stack AI architecture we will build.',
      contentType: 'video',
      order: 1,
      estimatedDurationMinutes: 15,
      isFree: true,
      isRequired: true,
      bloomLevel: 'remember',
      content: {
        videoUrl: 'https://storage.skillmaster.ai/videos/course1/lesson1.mp4',
        videoDurationSeconds: 900,
      },
    },
    {
      id: randomUUID(),
      moduleId: module1Id,
      courseId: course1Id,
      title: 'Setting Up the Development Environment',
      description: 'Install and configure Next.js, FastAPI, Docker, and all required tools.',
      contentType: 'article',
      order: 2,
      estimatedDurationMinutes: 30,
      isFree: true,
      isRequired: true,
      bloomLevel: 'apply',
      content: {
        articleMarkdown:
          '# Setting Up Your Development Environment\n\nIn this lesson, we will set up everything you need...',
      },
    },
    {
      id: randomUUID(),
      moduleId: module2Id,
      courseId: course1Id,
      title: 'Understanding the Claude API',
      description: 'Deep dive into Anthropic Claude API, system prompts, and streaming.',
      contentType: 'video',
      order: 1,
      estimatedDurationMinutes: 25,
      isFree: false,
      isRequired: true,
      bloomLevel: 'understand',
      content: {
        videoUrl: 'https://storage.skillmaster.ai/videos/course1/lesson3.mp4',
        videoDurationSeconds: 1500,
      },
    },
    {
      id: randomUUID(),
      moduleId: module2Id,
      courseId: course1Id,
      title: 'Build a Streaming Chat Interface',
      description: 'Hands-on: Build a real-time streaming AI chat with React and WebSockets.',
      contentType: 'assignment',
      order: 2,
      estimatedDurationMinutes: 45,
      isFree: false,
      isRequired: true,
      bloomLevel: 'create',
      content: {},
    },
  ]);

  // Create enrollment
  await db.insert(enrollments).values([
    {
      id: randomUUID(),
      userId: studentId,
      courseId: course1Id,
      status: 'active',
      progress: 25,
      amountPaid: 49.99,
      currency: 'USD',
      paymentStatus: 'completed',
      paymentId: 'pi_test_123456',
    },
    {
      id: randomUUID(),
      userId: studentId,
      courseId: course2Id,
      status: 'active',
      progress: 10,
      amountPaid: 0,
      currency: 'USD',
      paymentStatus: 'completed',
    },
  ]);

  console.log('✅ Database seeded successfully!');
  console.log(`   - 3 users (admin, instructor, student)`);
  console.log(`   - 2 courses with modules and lessons`);
  console.log(`   - 2 enrollments`);

  process.exit(0);
}

seed().catch((err) => {
  console.error('❌ Seed failed:', err);
  process.exit(1);
});
