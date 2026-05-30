import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-brand-100 text-brand-700 dark:bg-brand-900 dark:text-brand-300',
        secondary: 'border-transparent bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100',
        destructive: 'border-transparent bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
        success: 'border-transparent bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
        warning: 'border-transparent bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
        outline: 'border-slate-300 text-slate-700 dark:border-slate-700 dark:text-slate-300',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
