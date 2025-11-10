'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { 
  Globe, 
  Search, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Loader2,
  AlertCircle,
  Sparkles, 
  Upload,
  FileText,
  Settings,
  Brain
} from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { 
  analyzeUrl as apiAnalyzeUrl, 
  uploadAndAnalyze, 
  handleApiError, 
  type KeywordData as ApiKeywordData 
} from '@/lib/api';

interface AnalysisForm {
  clientUrl: string;
  keywords: string[];
  competitorFile?: FileList;
}

interface KeywordData {
  keyword: string;
  frequency: number;
  relevance: 'high' | 'medium' | 'low';
  category: string;
}

interface SiteSummary {
  business_description: string;
  industry_sector: string;
  target_market: string;
  key_services: string[];
  confidence_score: number;
  processing_time: number;
}

// Normalize URL function (outside component to avoid recreating)
const normalizeUrl = (url: string): string => {
  if (!url) return url;
  
  // Remove whitespace
  url = url.trim();
  
  // Remove any duplicate protocols that might occur
  url = url.replace(/^https?:\/\/https?:\/\//, 'https://');
  
  // If no protocol at all, add https://
  if (!url.match(/^https?:\/\//)) {
    url = `https://${url}`;
  }
  
  // Clean up any potential double slashes after the protocol
  url = url.replace(/^(https?:\/\/)\/+/, '$1');
  
  return url;
};

// 🆕 Helper function per estrarre URL dall'Excel
const extractUrlsFromFile = async (file: File): Promise<string[]> => {
  try {
    const XLSX = await import('xlsx');
    const data = await file.arrayBuffer();
    const workbook = XLSX.read(data, { type: 'array' });
    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
    const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 }) as any[][];
    
    // Estrai URL dalla prima colonna (skippa header se presente)
    const urls: string[] = [];
    for (let i = 0; i < jsonData.length; i++) {
      const row = jsonData[i];
      if (row && row[0]) {
        const url = String(row[0]).trim();
        // Salta header e valori non-URL
        if (url && !url.toLowerCase().includes('url') && !url.toLowerCase().includes('competitor')) {
          urls.push(url);
        }
      }
    }
    
    return urls;
  } catch (error) {
    console.error('Error extracting URLs:', error);
    // Fallback: ritorna array vuoto
    return [];
  }
};



export default function AnalyzePage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [currentAnalyzingUrl, setCurrentAnalyzingUrl] = useState<string>(''); // 🆕 URL corrente in analisi
  const [totalCompetitorsToAnalyze, setTotalCompetitorsToAnalyze] = useState<number>(0); // 🆕 Totale da analizzare
  const [extractedKeywords, setExtractedKeywords] = useState<KeywordData[]>([]);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [siteSummary, setSiteSummary] = useState<SiteSummary | null>(null);
  const [customKeywords, setCustomKeywords] = useState<string>('');
  const [aiContextPrompt, setAiContextPrompt] = useState<string>('');
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  // Test URL normalization on component mount (dev only)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🧪 Testing URL normalization:');
      const testUrls = [
        'esempio.com',
        'www.esempio.com',
        'https://esempio.com',
        'http://esempio.com',
        'https://https://esempio.com',
        'https://www.esempio.com',
        '  https://esempio.com  ',
        'https:///esempio.com'
      ];
      
      testUrls.forEach(url => {
        console.log(`  "${url}" → "${normalizeUrl(url)}"`);
      });
    }
  }, []);

  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm<AnalysisForm>();
  
  const watchedUrl = watch('clientUrl');
  const watchedKeywords = watch('keywords') || [];

  const steps = [
    { id: 1, title: 'URL Sito', description: 'Inserisci l\'URL da analizzare' },
    { id: 2, title: 'Configurazione', description: 'Summary e keywords personalizzate' },
    { id: 3, title: 'Upload Excel', description: 'Carica file competitors' },
    { id: 4, title: 'Risultati', description: 'Visualizza analisi' }
  ];

  // Save report to localStorage
  const saveReportToStorage = (reportData: any, keywords: string[] = [], analysisName: string = '') => {
    try {
      const existingReports = JSON.parse(localStorage.getItem('competitorReports') || '[]');
      
      const newReport = {
        id: reportData.reportId,
        name: analysisName || `Analisi ${watchedUrl} - ${new Date().toLocaleDateString()}`,
        date: new Date().toISOString().split('T')[0],
        status: 'completed' as const,
        competitors: reportData.totalCompetitors,
        keywords: reportData.keywordMatches,
        avgScore: reportData.averageScore,
        clientUrl: watchedUrl,
        type: 'bulk' as const,
        matches: reportData.matches || reportData.topCompetitors,
        targetKeywords: keywords,
        summary: `Analizzati ${reportData.totalCompetitors} competitors con score medio ${reportData.averageScore}%`,
        createdAt: new Date().toISOString()
      };

      existingReports.unshift(newReport);
      localStorage.setItem('competitorReports', JSON.stringify(existingReports.slice(0, 50)));
      
      console.log('✅ Report saved to localStorage:', newReport.id);
      return newReport.id;
    } catch (error) {
      console.error('❌ Error saving report:', error);
      return null;
    }
  };



  // Step 1: Analisi URL
  const analyzeUrlStep = async () => {
    if (!watchedUrl) return;
    
    setIsAnalyzing(true);
    try {
      const normalizedUrl = normalizeUrl(watchedUrl);
      console.log('🔍 URL Normalization:');
      console.log('  Original:', watchedUrl);
      console.log('  Normalized:', normalizedUrl);
      
      const response = await apiAnalyzeUrl(normalizedUrl);
      console.log('✅ Backend response:', response);

      if (response.status === 'success' && response.keywords) {
        console.log('🎯 Keywords ricevute:', response.keywords);
        
        if (response.keywords.length > 0) {
          console.log('📝 Esempio keyword:', response.keywords[0]);
          console.log('🏷️ Chiavi disponibili:', Object.keys(response.keywords[0]));
        }
        
        setExtractedKeywords(response.keywords);
        setCurrentStep(2);
        
        // Auto-genera il summary AI quando arriviamo alla Step 2
        setTimeout(() => {
          handleGenerateSummary();
        }, 500);
      } else {
        throw new Error(response.message || 'Errore durante l\'analisi');
      }
    } catch (error: any) {
      console.error('❌ Error analyzing URL:', error);
      let errorMessage = handleApiError(error);
      const normalizedUrl = normalizeUrl(watchedUrl);
      
      // Provide more specific error messages for common issues
      if (errorMessage.includes('ERR_NAME_NOT_RESOLVED')) {
        const domain = normalizedUrl.replace(/^https?:\/\//, '');
        const suggestions = domain.startsWith('www.') 
          ? [domain.replace('www.', '')]  
          : [`www.${domain}`];
        errorMessage = `Il dominio "${normalizedUrl}" non esiste o non è raggiungibile.\n\nProva con: ${suggestions.map(s => `https://${s}`).join(' o ')}`;
      } else if (errorMessage.includes('ERR_CONNECTION_REFUSED')) {
        errorMessage = `Impossibile connettersi a "${normalizedUrl}". Il sito potrebbe essere offline.`;
      } else if (errorMessage.includes('ERR_CERT_')) {
        errorMessage = `Certificato SSL non valido per "${normalizedUrl}". Prova con http:// invece di https://.`;
      }
      
      alert(`Errore di analisi:\n${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Step 2: Selezione Keywords
  const toggleKeyword = (keyword: string) => {
    const currentKeywords = watchedKeywords;
    const newKeywords = currentKeywords.includes(keyword)
      ? currentKeywords.filter(k => k !== keyword)
      : [...currentKeywords, keyword];
    setValue('keywords', newKeywords);
  };

  // Genera suggerimenti keywords dinamici basati sul summary AI
  const generateKeywordSuggestions = (summary: SiteSummary | null): string => {
    if (!summary) return 'web design, sviluppo software, consulenza digitale, marketing online...';
    
    // Estrai parole chiave dai servizi e dal settore
    const services = Array.isArray(summary.key_services) ? summary.key_services : [];
    const sector = summary.industry_sector || '';
    const description = summary.business_description || '';
    
    let suggestions: string[] = [];
    
    // Aggiungi servizi chiave
    suggestions = [...suggestions, ...services.slice(0, 4)];
    
    // Aggiungi variazioni basate sul settore
    const sectorKeywords: { [key: string]: string[] } = {
      'Arredamento': ['mobili', 'design interno', 'casa', 'arredo'],
      'Tecnologia dell\'Informazione': ['software', 'sviluppo web', 'digitale', 'IT'],
      'E-commerce': ['vendita online', 'shopping', 'prodotti', 'marketplace'],
      'Marketing': ['pubblicità', 'branding', 'comunicazione', 'promozione'],
      'Consulenza': ['servizi professionali', 'advisory', 'business', 'strategia'],
      'Immobiliare': ['case', 'proprietà', 'vendita immobili', 'affitto'],
      'Salute': ['benessere', 'cure mediche', 'assistenza sanitaria', 'salute'],
      'Educazione': ['formazione', 'corsi', 'istruzione', 'apprendimento']
    };
    
    // Trova settore corrispondente
    Object.keys(sectorKeywords).forEach(key => {
      if (sector.includes(key) || description.toLowerCase().includes(key.toLowerCase())) {
        suggestions = [...suggestions, ...sectorKeywords[key].slice(0, 3)];
      }
    });
    
    // Parole chiave generiche se non trova nient'altro
    if (suggestions.length < 4) {
      suggestions = [...suggestions, 'servizi professionali', 'qualità', 'esperienza', 'clienti'];
    }
    
    // Rimuovi duplicati e prendi i primi 6
    const uniqueSuggestions = [...new Set(suggestions)].slice(0, 6);
    return uniqueSuggestions.join(', ') + '...';
  };

  // Genera contesto AI intelligente basato sul summary del sito
  const generateAIContext = (summary: SiteSummary | null): string => {
    if (!summary) return 'Cerco competitors che operano in settori simili al mio, con focus su aziende innovative...';
    
    const sector = summary.industry_sector || '';
    const target = summary.target_market || '';
    const services = Array.isArray(summary.key_services) ? summary.key_services : [];
    const description = summary.business_description || '';
    
    let context = '';
    
    // Costruisci il contesto basato sui dati del sito
    if (sector && services.length > 0) {
      context += `Cerco competitors nel settore ${sector.toLowerCase()}`;
      
      // Aggiungi dettagli sui servizi principali
      if (services.length > 0) {
        const mainServices = services.slice(0, 3).join(', ').toLowerCase();
        context += ` specializzati in ${mainServices}`;
      }
      
      // Aggiungi informazioni sul target se disponibile
      if (target && target.toLowerCase().includes('aziende')) {
        context += ', con focus su clienti business';
      } else if (target && target.toLowerCase().includes('privati')) {
        context += ', orientati verso clienti privati';
      } else if (target && target.toLowerCase().includes('professionisti')) {
        context += ', che servono professionisti e aziende';
      }
      
      // Aggiungi caratteristiche specifiche basate sul settore
      if (sector.toLowerCase().includes('tecnologia') || sector.toLowerCase().includes('digitale')) {
        context += ', interessato a realtà innovative che utilizzano tecnologie avanzate';
      } else if (sector.toLowerCase().includes('arredamento') || sector.toLowerCase().includes('design')) {
        context += ', con attenzione al design e alla qualità dei prodotti';
      } else if (sector.toLowerCase().includes('consulenza') || sector.toLowerCase().includes('servizi')) {
        context += ', che offrono expertise e soluzioni personalizzate';
      }
      
      // Finalizza il contesto
      context += '. Valuto competitor sia locali che nazionali con presenza online consolidata.';
    } else {
      // Fallback generico
      context = 'Cerco competitors che operano in settori affini, con particolare interesse per aziende che condividono target di mercato simili e approccio professionale.';
    }
    
    return context;
  };

  // AI Site Summary Generation
  const handleGenerateSummary = async () => {
    if (!watchedUrl || isGeneratingSummary) return;

    setIsGeneratingSummary(true);
    try {
      const normalizedUrl = normalizeUrl(watchedUrl);
      console.log('🤖 Generating AI summary for:', normalizedUrl);
      
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/generate-site-summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: normalizedUrl }),
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ HTTP Error:', response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('📦 Full response data:', data);
      
      if (data.status === 'success' && data.business_description) {
        console.log('✅ AI Summary generated:', data);
        // Il backend restituisce i dati direttamente, non in un campo summary
        const summaryData = {
          business_description: data.business_description,
          industry_sector: data.industry_sector,
          target_market: data.target_market,
          key_services: data.key_services,
          confidence_score: data.confidence_score,
          processing_time: data.processing_time
        };
        setSiteSummary(summaryData);
        
        // Auto-popola il contesto AI quando il summary è pronto
        if (!aiContextPrompt.trim()) {
          setAiContextPrompt(generateAIContext(summaryData));
        }
      } else {
        console.error('❌ Backend error details:', data);
        throw new Error(data.message || 'Errore durante la generazione del summary');
      }
    } catch (error: any) {
      console.error('❌ Full error details:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        alert(`Errore di connessione al backend:\n${error.message}\n\nAssicurati che il backend sia avviato.`);
      } else {
        alert(`Errore nella generazione del summary AI:\n${error.message}`);
      }
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  // Step 3: Upload File and Analysis with REAL-TIME SSE streaming
  const handleFileUpload = async (data: AnalysisForm) => {
    if (!data.competitorFile || data.competitorFile.length === 0) {
      alert('Seleziona un file da caricare');
      return;
    }

    // Converti customKeywords da stringa a array
    const keywordsArray = customKeywords
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0);

    if (keywordsArray.length === 0) {
      alert('Inserisci almeno una keyword per continuare');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setCurrentAnalyzingUrl('');
    
    try {
      const file = data.competitorFile[0];
      console.log('🚀 Starting REAL-TIME streaming analysis...');
      console.log('📁 File name:', file.name);
      console.log('🔍 Keywords:', keywordsArray);
      
      // 🎯 Usa Server-Sent Events per aggiornamenti REAL-TIME dal backend
      const formData = new FormData();
      formData.append('file', file);
      formData.append('keywords', JSON.stringify(keywordsArray));
      
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const eventSourceUrl = `${API_BASE_URL}/api/upload-and-analyze-stream`;
      
      // Crea richiesta POST per SSE
      const response = await fetch(eventSourceUrl, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('No response body reader available');
      }
      
      let buffer = '';
      
      // Leggi stream SSE
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            // 🎯 Gestisci eventi real-time
            switch (data.event) {
              case 'started':
                console.log('🚀 Analysis started, total sites:', data.total, 'ID:', data.analysis_id);
                setTotalCompetitorsToAnalyze(data.total);
                
                // 💾 Salva analysis_id in localStorage
                if (data.analysis_id) {
                  localStorage.setItem('current_analysis_id', data.analysis_id);
                  localStorage.setItem('analysis_started_at', new Date().toISOString());
                  console.log('💾 Analysis ID saved to localStorage:', data.analysis_id);
                }
                break;
              
              case 'start':
                // Backward compatibility con vecchio evento
                console.log('🚀 Analysis started, total sites:', data.total);
                setTotalCompetitorsToAnalyze(data.total);
                break;
                
              case 'progress':
                console.log(`📊 Analyzing (${data.current}/${data.total}): ${data.url}`);
                setCurrentAnalyzingUrl(data.url);
                setAnalysisProgress(data.percentage);
                break;
                
              case 'result':
                console.log(`✅ Result: ${data.url} → ${data.score}%`);
                break;
                
              case 'error':
                console.warn(`⚠️ Error analyzing ${data.url}: ${data.message}`);
                break;
                
              case 'complete':
                console.log('🎉 Analysis complete!');
                setAnalysisProgress(100);
                setCurrentAnalyzingUrl('Completato!');
                
                // 💾 Pulisci localStorage (analisi completata)
                localStorage.removeItem('current_analysis_id');
                localStorage.removeItem('analysis_started_at');
                
                // Classifica competitors per categoria KPI
                const directCompetitors = data.matches.filter((m: any) => m.competitor_status?.category === 'DIRECT');
                const potentialCompetitors = data.matches.filter((m: any) => m.competitor_status?.category === 'POTENTIAL');
                const nonCompetitors = data.matches.filter((m: any) => m.competitor_status?.category === 'NON_COMPETITOR');
                
                const reportData = {
                  totalCompetitors: data.total_competitors,
                  keywordMatches: keywordsArray.length,
                  averageScore: data.average_score,
                  matches: data.matches,
                  directCompetitors,
                  potentialCompetitors,
                  nonCompetitors,
                  summaryByStatus: data.summary_by_status,
                  topCompetitors: data.matches.slice(0, 5).map((match: any) => ({
                    url: match.url,
                    score: match.score,
                    keywords: match.keywords_found?.length || 0,
                    status: match.competitor_status
                  })),
                  reportId: data.report_id
                };

                setAnalysisResult(reportData);
                saveReportToStorage(reportData, keywordsArray);
                setCurrentStep(4);
                break;
            }
          }
        }
      }
      
    } catch (error: any) {
      console.error('❌ Streaming analysis error:', error);
      const errorMessage = handleApiError(error);
      alert(`Errore durante l'analisi: ${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getRelevanceColor = (relevance: string) => {
    switch (relevance) {
      case 'high': return 'badge-success';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-secondary';
      default: return 'badge-secondary';
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-3xl font-bold text-slate-100 mb-4">
            Analisi Competitiva AI
          </h1>
          <p className="text-slate-400 text-lg">
            Estrai keywords, analizza competitors e genera report dettagliati
          </p>
        </motion.div>

        {/* Progress Steps */}
        <div className="flex justify-center">
          <div className="flex items-center space-x-4">
            {steps.map((step) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-all ${
                  currentStep >= step.id 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-slate-700 text-slate-400'
                }`}>
                  {currentStep > step.id ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    step.id
                  )}
                </div>
                <div className="ml-2 mr-6">
                  <p className={`text-sm font-medium ${
                    currentStep >= step.id ? 'text-slate-100' : 'text-slate-400'
                  }`}>
                    {step.title}
                  </p>
                  <p className="text-xs text-slate-500">{step.description}</p>
                </div>
                {step.id < steps.length && (
                  <ArrowRight className="w-4 h-4 text-slate-600 mr-4" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          {/* Step 1: URL Input */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="card p-8"
            >
              <div className="text-center mb-8">
                <Globe className="w-16 h-16 text-primary-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-slate-100 mb-2">
                  Inserisci URL del Sito
                </h2>
                <p className="text-slate-400">
                  Inserisci il dominio o URL completo. Analizzeremo il contenuto per estrarre keywords rilevanti.
                </p>
              </div>

              <div className="max-w-lg mx-auto space-y-6">
                <div>
                  <label className="label">URL Sito Web</label>
                  <Input
                    {...register('clientUrl', { 
                      required: 'URL richiesto',
                      validate: (value) => {
                        try {
                          const normalized = normalizeUrl(value);
                          console.log('🔍 Validation - Original:', value, 'Normalized:', normalized);
                          
                          // Check if it's a valid URL format after normalization
                          const urlPattern = /^https?:\/\/[^\s/$.?#].[^\s]*$/;
                          const isValid = urlPattern.test(normalized);
                          
                          if (!isValid) {
                            return 'Inserisci un dominio valido (es: esempio.com)';
                          }
                          
                          // Additional check: ensure it doesn't have duplicate protocols
                          if (normalized.includes('://') && normalized.split('://').length > 2) {
                            return 'URL non valido - protocollo duplicato rilevato';
                          }
                          
                          return true;
                        } catch (error) {
                          return 'Errore nella validazione dell\'URL';
                        }
                      }
                    })}
                    placeholder="esempio.com o https://esempio.com"
                    className="text-lg"
                  />
                  {watchedUrl && !errors.clientUrl && (
                    <p className="text-slate-500 text-sm mt-1">
                      📍 Analizzeremo: <span className="text-primary-400">{normalizeUrl(watchedUrl)}</span>
                    </p>
                  )}
                  {errors.clientUrl && (
                    <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.clientUrl.message}
                    </p>
                  )}
                </div>

                <Button
                  onClick={analyzeUrlStep}
                  disabled={!watchedUrl || isAnalyzing}
                  size="lg"
                  className="w-full"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin mr-2" />
                      Analizzando sito...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Analizza con AI
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Configuration (AI Summary + Custom Keywords) */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="card p-8"
            >
              <div className="text-center mb-8">
                <Settings className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-slate-100 mb-2">
                  Configurazione Analisi
                </h2>
                <p className="text-slate-400">
                  Analisi AI del sito e configurazione personalizzata per i competitors
                </p>
              </div>

              {/* AI Site Summary Section */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
                  <Sparkles className="w-5 h-5 mr-2 text-primary-400" />
                  Analisi AI del Sito
                </h3>
                
                {isGeneratingSummary && (
                  <div className="text-center mb-6">
                    <div className="flex items-center justify-center space-x-2 text-blue-400">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Analisi in corso...</span>
                    </div>
                  </div>
                )}

                {siteSummary && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-lg p-6 mb-6 border border-green-500/30"
                  >
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-semibold text-green-300 mb-2">Descrizione Business:</h4>
                        <p className="text-slate-300 text-sm">{siteSummary.business_description}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold text-green-300 mb-2">Settore:</h4>
                        <p className="text-slate-300 text-sm">{siteSummary.industry_sector}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold text-green-300 mb-2">Target Market:</h4>
                        <p className="text-slate-300 text-sm">{siteSummary.target_market}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold text-green-300 mb-2">Servizi Chiave:</h4>
                        <p className="text-slate-300 text-sm">
                          {Array.isArray(siteSummary.key_services) 
                            ? siteSummary.key_services.join(', ')
                            : siteSummary.key_services}
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 flex justify-end">
                      <Button
                        onClick={handleGenerateSummary}
                        disabled={isGeneratingSummary}
                        variant="ghost"
                        size="sm"
                      >
                        Rigenera
                      </Button>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Custom Keywords Section */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
                  <Search className="w-5 h-5 mr-2 text-primary-400" />
                  Keywords Personalizzate
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Inserisci le keywords più rilevanti per i tuoi competitors (separate da virgola):
                    </label>
                    <textarea
                      value={customKeywords}
                      onChange={(e) => setCustomKeywords(e.target.value)}
                      placeholder={`es: ${generateKeywordSuggestions(siteSummary)}`}
                      rows={3}
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-slate-100 placeholder-slate-400"
                    />
                    <p className="mt-2 text-sm text-slate-500">
                      Più specifiche sono le keywords, più precisa sarà l'analisi dei competitors
                    </p>
                    {siteSummary && (
                      <div 
                        key="keyword-suggestions-box"
                        className="mt-3 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20"
                      >
                        <p className="text-blue-300 text-sm mb-2">💡 Suggerimenti basati sul tuo sito:</p>
                        <div className="flex flex-wrap gap-2">
                          {generateKeywordSuggestions(siteSummary).split(', ').slice(0, -1).map((keyword, index) => (
                            <button
                              key={index}
                              onClick={() => {
                                const current = customKeywords.trim();
                                const newKeywords = current ? `${current}, ${keyword.trim()}` : keyword.trim();
                                setCustomKeywords(newKeywords);
                              }}
                              className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs hover:bg-blue-500/30 transition-colors"
                            >
                              + {keyword.trim()}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* AI Context Prompt Section */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-primary-400" />
                  Contesto AI
                </h3>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Contesto intelligente per l'analisi dei competitors:
                  </label>
                  <textarea
                    value={aiContextPrompt}
                    onChange={(e) => setAiContextPrompt(e.target.value)}
                    placeholder={generateAIContext(siteSummary)}
                    rows={4}
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-slate-100 placeholder-slate-400"
                  />
                  <p className="mt-2 text-sm text-slate-500">
                    Questo contesto aiuta l'AI a comprendere meglio i criteri di matching specifici per il tuo settore
                  </p>
                  {siteSummary && (
                    <div className="mt-3">
                      <button
                        onClick={() => setAiContextPrompt(generateAIContext(siteSummary))}
                        className="px-4 py-2 bg-purple-500/20 text-purple-300 rounded-lg text-sm hover:bg-purple-500/30 transition-colors border border-purple-500/30"
                      >
                        🤖 Usa contesto suggerito
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-between">
                <Button
                  onClick={() => setCurrentStep(1)}
                  variant="secondary"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Indietro
                </Button>
                <Button
                  onClick={() => setCurrentStep(3)}
                  disabled={!customKeywords.trim()}
                  variant="primary"
                >
                  Continua
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 3: File Upload */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="card p-8"
            >
              <div className="text-center mb-8">
                <Upload className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-slate-100 mb-2">
                  Carica Excel Competitors
                </h2>
                <p className="text-slate-400">
                  Carica un file Excel con la lista degli URL dei competitors da analizzare
                </p>
              </div>

              <form onSubmit={handleSubmit(handleFileUpload)} className="space-y-6">
                {/* 🆕 Progress Bar con URL corrente */}
                {isAnalyzing && (
                  <div className="mb-6 p-6 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-lg border-2 border-blue-500/30">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
                        <div>
                          <span className="text-base font-semibold text-slate-100">
                            Analisi in corso...
                          </span>
                          {totalCompetitorsToAnalyze > 0 && (
                            <span className="text-sm text-slate-400 ml-2">
                              ({analysisProgress}% di {totalCompetitorsToAnalyze} siti)
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="text-2xl font-bold text-blue-400">
                        {analysisProgress}%
                      </span>
                    </div>
                    
                    {/* Progress bar */}
                    <div className="w-full bg-slate-700/50 rounded-full h-3 mb-4 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500 ease-out relative"
                        style={{ width: `${analysisProgress}%` }}
                      >
                        <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                      </div>
                    </div>
                    
                    {/* 🆕 URL corrente in analisi */}
                    {currentAnalyzingUrl && (
                      <div className="mt-3 p-3 bg-slate-800/50 rounded-lg border border-blue-500/20">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-slate-400">🔍 Analizzando:</span>
                          <span className="text-blue-300 font-mono font-medium truncate">
                            {currentAnalyzingUrl}
                          </span>
                        </div>
                      </div>
                    )}
                    
                    {/* 💡 Messaggio: Puoi navigare via */}
                    <div className="mt-4 p-4 bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-lg border border-green-500/20">
                      <div className="flex items-start gap-3">
                        <div className="text-green-400 mt-0.5">💡</div>
                        <div className="flex-1">
                          <p className="text-sm text-slate-300 font-medium mb-1">
                            Puoi lasciare questa pagina!
                          </p>
                          <p className="text-xs text-slate-400">
                            L'analisi continua in background. Vai su <span className="text-blue-400 font-semibold">Reports</span> per vedere i progressi.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="max-w-lg mx-auto">
                  <label className="label">File Excel (.xlsx, .xls)</label>
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    {...register('competitorFile', { required: 'File richiesto' })}
                    className="input"
                  />
                  {errors.competitorFile && (
                    <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.competitorFile.message}
                    </p>
                  )}
                  
                  <div className="mt-4 p-4 bg-slate-800 rounded-lg">
                    <p className="text-sm text-slate-300 mb-2">
                      <FileText className="w-4 h-4 inline mr-1" />
                      Formato file richiesto:
                    </p>
                    <ul className="text-xs text-slate-400 space-y-1">
                      <li>• Colonna A: URL competitors</li>
                      <li>• Una riga per ogni competitor</li>
                      <li>• Formato: https://esempio.com</li>
                    </ul>
                  </div>
                </div>

                <div className="flex justify-between">
                  <Button
                    type="button"
                    onClick={() => setCurrentStep(2)}
                    variant="secondary"
                    disabled={isAnalyzing}
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Indietro
                  </Button>
                  <Button
                    type="submit"
                    disabled={isAnalyzing}
                    variant="primary"
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        Analizzando competitors...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5 mr-2" />
                        Avvia Analisi
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </motion.div>
          )}

          {/* Step 4: Results */}
          {currentStep === 4 && analysisResult && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="card p-8 text-center">
                <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-slate-100 mb-2">
                  Analisi Completata!
                </h2>
                <p className="text-slate-400 mb-6">
                  Abbiamo analizzato {analysisResult.totalCompetitors} competitors con {analysisResult.keywordMatches} keywords
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 p-6 rounded-lg border border-green-500/30">
                    <p className="text-4xl font-bold text-green-400 mb-1">
                      {analysisResult.summaryByStatus?.direct?.count || 0}
                    </p>
                    <p className="text-green-300 font-medium">🟢 Competitor Diretti</p>
                    <p className="text-slate-400 text-sm mt-1">Alta priorità</p>
                  </div>
                  <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 p-6 rounded-lg border border-yellow-500/30">
                    <p className="text-4xl font-bold text-yellow-400 mb-1">
                      {analysisResult.summaryByStatus?.potential?.count || 0}
                    </p>
                    <p className="text-yellow-300 font-medium">🟡 Da Valutare</p>
                    <p className="text-slate-400 text-sm mt-1">Media priorità</p>
                  </div>
                  <div className="bg-gradient-to-br from-red-500/20 to-red-600/10 p-6 rounded-lg border border-red-500/30">
                    <p className="text-4xl font-bold text-red-400 mb-1">
                      {analysisResult.summaryByStatus?.non_competitor?.count || 0}
                    </p>
                    <p className="text-red-300 font-medium">🔴 Non Competitor</p>
                    <p className="text-slate-400 text-sm mt-1">Bassa priorità</p>
                  </div>
                </div>

                <div className="flex gap-4 justify-center">
                  <Button
                    onClick={() => window.location.href = '/reports'}
                    variant="primary"
                  >
                    <FileText className="w-5 h-5 mr-2" />
                    Visualizza Report
                  </Button>
                  <Button
                    onClick={() => {
                      setCurrentStep(1);
                      setAnalysisResult(null);
                      setExtractedKeywords([]);
                    }}
                    variant="secondary"
                  >
                    Nuova Analisi
                  </Button>
                </div>
              </div>

              {/* 🆕 Competitors classificati per KPI - 3 categorie colorate */}
              {analysisResult.matches && analysisResult.matches.length > 0 && (
                <div className="space-y-4">
                  {/* 🟢 COMPETITOR DIRETTI */}
                  {analysisResult.directCompetitors && analysisResult.directCompetitors.length > 0 && (
                    <div className="card p-6 border-2 border-green-500/30 bg-green-500/5">
                      <div className="flex items-center gap-3 mb-4">
                        <span className="text-3xl">🟢</span>
                        <div>
                          <h3 className="text-xl font-bold text-green-400">
                            Competitor Diretti - Alta Priorità
                          </h3>
                          <p className="text-slate-400 text-sm">
                            Monitora attentamente questi competitor ({analysisResult.directCompetitors.length})
                          </p>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {analysisResult.directCompetitors.map((competitor: any, index: number) => (
                          <div key={index} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-green-500/20">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
                                {index + 1}
                              </div>
                              <div>
                                <p className="text-slate-100 font-medium">{competitor.url}</p>
                                <p className="text-green-400 text-sm">{competitor.keywords_found?.length || 0} keywords match</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 🟡 COMPETITOR POTENZIALI */}
                  {analysisResult.potentialCompetitors && analysisResult.potentialCompetitors.length > 0 && (
                    <div className="card p-6 border-2 border-yellow-500/30 bg-yellow-500/5">
                      <div className="flex items-center gap-3 mb-4">
                        <span className="text-3xl">🟡</span>
                        <div>
                          <h3 className="text-xl font-bold text-yellow-400">
                            Da Valutare - Media Priorità
                          </h3>
                          <p className="text-slate-400 text-sm">
                            Possibili competitor in settori affini ({analysisResult.potentialCompetitors.length})
                          </p>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {analysisResult.potentialCompetitors.map((competitor: any, index: number) => (
                          <div key={index} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-yellow-500/20">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold">
                                •
                              </div>
                              <div>
                                <p className="text-slate-100 font-medium">{competitor.url}</p>
                                <p className="text-yellow-400 text-sm">{competitor.keywords_found?.length || 0} keywords match</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 🔴 NON COMPETITOR */}
                  {analysisResult.nonCompetitors && analysisResult.nonCompetitors.length > 0 && (
                    <div className="card p-6 border-2 border-red-500/30 bg-red-500/5">
                      <div className="flex items-center gap-3 mb-4">
                        <span className="text-3xl">🔴</span>
                        <div>
                          <h3 className="text-xl font-bold text-red-400">
                            Non Competitor
                          </h3>
                          <p className="text-slate-400 text-sm">
                            Settori diversi o scarsa rilevanza ({analysisResult.nonCompetitors.length})
                          </p>
                        </div>
                      </div>
                      <div className="space-y-2">
                        {analysisResult.nonCompetitors.map((competitor: any, index: number) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg border border-red-500/10">
                            <div className="flex items-center gap-3">
                              <div className="w-6 h-6 bg-red-500/30 rounded-full flex items-center justify-center text-red-400 text-xs">
                                ×
                              </div>
                              <div>
                                <p className="text-slate-300 text-sm">{competitor.url}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center py-4 mt-8 border-t border-slate-700"
        >
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
        </motion.div>
      </div>
    </DashboardLayout>
  );
}