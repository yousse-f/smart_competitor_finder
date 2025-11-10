'use client';

import { Suspense } from 'react';
import ReportsPageContent from './ReportsPageContent';

export const dynamic = 'force-dynamic';

export default function ReportsPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading reports...</p>
        </div>
      </div>
    }>
      <ReportsPageContent />
    </Suspense>
  );
}
