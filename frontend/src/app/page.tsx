'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const isAuthenticated = localStorage.getItem('isAuthenticated');
    
    if (isAuthenticated === 'true') {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  // Loading screen while redirecting
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="spinner w-8 h-8 mx-auto mb-4" />
        <p className="text-slate-400">Caricamento...</p>
      </div>
    </div>
  );
}
