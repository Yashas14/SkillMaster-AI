import { cn } from '../utils';
import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

function Spinner({ className, size = 'md' }: SpinnerProps) {
  const sizeClass = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  }[size];

  return <Loader2 className={cn('animate-spin text-brand-600', sizeClass, className)} />;
}

export { Spinner };
