'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Sparkles, RotateCcw } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/Button';

export default function UploadPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to analyze page after a short delay
    const timer = setTimeout(() => {
      router.push('/analyze');
    }, 3000);

    return () => clearTimeout(timer);
  }, [router]);

  const handleRedirectNow = () => {
    router.push('/analyze');
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto mt-20 text-center">
        <div className="card p-12">
          <div className="mb-8">
            <RotateCcw className="w-16 h-16 text-primary-500 mx-auto mb-4 animate-spin" />
            <h1 className="text-3xl font-bold text-slate-100 mb-4">
              Reindirizzamento in corso...
            </h1>
            <p className="text-slate-400 text-lg">
              La pagina di upload è stata spostata. Ti stiamo reindirizzando alla nuova interfaccia di analisi.
            </p>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-800 p-6 rounded-lg">
              <Sparkles className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-slate-100 mb-2">
                Nuova Esperienza di Analisi
              </h3>
              <p className="text-slate-400 text-sm">
                Ora puoi analizzare il sito web del cliente, selezionare keywords e caricare competitors tutto in un unico flusso integrato.
              </p>
            </div>

            <Button
              onClick={handleRedirectNow}
              className="btn-primary btn-lg w-full"
            >
              <ArrowRight className="w-5 h-5 mr-2" />
              Vai alla Nuova Analisi
            </Button>

            <p className="text-slate-500 text-sm">
              Reindirizzamento automatico tra 3 secondi...
            </p>
          </div>
        </div>
        
        {/* Footer */}
        <div className="text-center py-4 mt-8 border-t border-slate-700">
          <p className="text-xs text-slate-400">
            © 2025 Smart Competitor Finder - Creato da{' '}
            <a 
              href="https://www.studioinnovativo.it" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 transition-colors underline"
            >
              Studio Innovativo
            </a>
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}