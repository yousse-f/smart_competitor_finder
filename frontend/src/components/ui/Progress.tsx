'use client';

import React from 'react';
import { clsx } from 'clsx';

export interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
  showPercentage?: boolean;
  label?: string;
}

const Progress: React.FC<ProgressProps> = ({ 
  value, 
  max = 100, 
  className, 
  showPercentage = false,
  label 
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={clsx('space-y-2', className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center text-sm">
          {label && <span className="text-text-primary">{label}</span>}
          {showPercentage && (
            <span className="text-text-secondary">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

Progress.displayName = 'Progress';

export { Progress };