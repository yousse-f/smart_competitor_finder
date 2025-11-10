'use client';

import React from 'react';
import { clsx } from 'clsx';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={clsx('spinner', sizeClasses[size], className)} />
  );
};

LoadingSpinner.displayName = 'LoadingSpinner';

export { LoadingSpinner };