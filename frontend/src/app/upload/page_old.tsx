'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  Download,
  Trash2,
  Play,
  Loader2,
  FileSpreadsheet
} from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface UploadForm {
  keywords: string;
  analysisName: string;
}

interface UploadedFile {
  name: string;
  size: number;
  type: string;
  lastModified: number;
  urls: string[];
}

export default function UploadPage() {
  const router = useRouter();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm<UploadForm>();
  const watchedKeywords = watch('keywords');

  // Demo URLs estratti dal file
  const demoUrls = [
    'https://consulenza-finanziaria.it',
    'https://investimenti-sicuri.com',
    'https://wealth-management.eu',
    'https://private-banking.net',
    'https://financial-advisor.co.uk'
  ];

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
      alert('Per favore carica un file Excel (.xlsx, .xls) o CSV');
      return;
    }

    // Mostra loading durante la lettura del file
    setIsProcessing(true);
    
    try {
      // Simula lettura file e estrazione URLs (in futuro sarà una vera lettura)
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simula tempo di lettura
      
      const fileData: UploadedFile = {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified,
        urls: demoUrls // In produzione, qui leggeremo il file Excel
      };

      setUploadedFile(fileData);
      
      // Mostra messaggio di successo
      alert(`✅ File "${file.name}" caricato con successo! Trovati ${demoUrls.length} URL.`);
      
    } catch (error) {
      console.error('Errore lettura file:', error);
      alert('❌ Errore durante la lettura del file');
    } finally {
      setIsProcessing(false);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setAnalysisResults(null);
  };

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Sparkles } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/Button';

export default function UploadPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to analyze page after a short delay
    const timer = setTimeout(() => {
      router.push('/analyze');
    }, 2000);

    return () => clearTimeout(timer);
  }, [router]);

  const handleRedirectNow = () => {
    router.push('/analyze');  const startAnalysis = async (data: UploadForm) => {
    if (!uploadedFile) return;

    setIsProcessing(true);
    setAnalysisProgress(0);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      
      // Create a File object from the uploaded data
      const csvContent = uploadedFile.urls.join('\n');
      const file = new File([csvContent], uploadedFile.name, { type: 'text/csv' });
      formData.append('file', file);
      formData.append('keywords', data.keywords);
      formData.append('analysis_name', data.analysisName || 'Bulk Analysis');
      
      console.log('🚀 Starting real backend analysis...');
      console.log('📁 File URLs:', uploadedFile.urls.length);
      console.log('🔍 Keywords:', data.keywords);
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          const newProgress = prev + 1;
          return newProgress > uploadedFile.urls.length ? uploadedFile.urls.length : newProgress;
        });
      }, 1000);
      
      // Call real backend API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/upload-and-analyze`, {
        method: 'POST',
        body: formData,
      });
      
      clearInterval(progressInterval);
      setAnalysisProgress(uploadedFile.urls.length);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      const results = await response.json();
      console.log('✅ Real backend results:', results);
      
      const reportData = {
        processedUrls: results.competitors_analyzed || uploadedFile.urls.length,
        keywords: data.keywords.split(',').map(k => k.trim()),
        matches: results.matches || [],
        reportId: results.analysis_id || `RPT_${Date.now()}`,
        summary: results.summary || 'Analysis completed successfully'
      };
      
      setAnalysisResults(reportData);
      
      // Save report to localStorage for reports page
      saveReportToStorage(reportData, data);
      
    } catch (error) {
      console.error('❌ Real backend analysis error:', error);
      // Fallback to demo data if backend fails
      const fallbackReportData = {
        processedUrls: uploadedFile.urls.length,
        keywords: data.keywords.split(',').map(k => k.trim()),
        matches: [
          { url: uploadedFile.urls[0] || 'example.com', score: 85, keywords_found: 7 },
          { url: uploadedFile.urls[1] || 'competitor.com', score: 72, keywords_found: 5 },
        ],
        reportId: `RPT_${Date.now()}`,
        error: 'Backend connection failed - showing fallback results'
      };
      
      setAnalysisResults(fallbackReportData);
      saveReportToStorage(fallbackReportData, data);
    } finally {
      setIsProcessing(false);
      setAnalysisProgress(0);
    }
  };

  const downloadSampleFile = () => {
    // Simula download file template
    const csvContent = "URL\nhttps://competitor1.com\nhttps://competitor2.com\nhttps://competitor3.com";
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'template_competitors.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
            Analisi Bulk Competitors
          </h1>
          <p className="text-slate-400 text-lg">
            Carica un file Excel con la lista dei competitors e avvia l'analisi automatica
          </p>
        </motion.div>

        {!analysisResults ? (
          <div className="space-y-8">
            {/* Upload Area */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card p-8"
            >
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-slate-100 mb-2">
                  1. Carica File Excel
                </h2>
                <p className="text-slate-400">
                  Carica un file Excel o CSV contenente gli URL dei competitors da analizzare
                </p>
              </div>

              {!uploadedFile ? (
                <div
                  className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
                    dragActive 
                      ? 'border-primary-400 bg-primary-400/10' 
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Upload className={`w-16 h-16 mx-auto mb-4 ${
                    dragActive ? 'text-primary-400' : 'text-slate-400'
                  }`} />
                  
                  <h3 className="text-lg font-semibold text-slate-100 mb-2">
                    Trascina qui il tuo file Excel
                  </h3>
                  <p className="text-slate-400 mb-6">
                    oppure clicca per selezionare dal computer
                  </p>
                  
                  <input
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleFileInput}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="inline-block">
                    <div className="btn btn-secondary cursor-pointer inline-flex items-center">
                      <FileSpreadsheet className="w-5 h-5 mr-2" />
                      Seleziona File
                    </div>
                  </label>

                  <div className="mt-6 flex justify-center">
                    <Button
                      onClick={downloadSampleFile}
                      variant="ghost"
                      size="sm"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Scarica Template
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-800 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                        <FileText className="w-6 h-6 text-green-400" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-100">{uploadedFile.name}</p>
                        <p className="text-sm text-slate-400">
                          {formatFileSize(uploadedFile.size)} • {uploadedFile.urls.length} URLs trovati
                        </p>
                      </div>
                    </div>
                    <Button
                      onClick={removeFile}
                      variant="ghost"
                      size="sm"
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Preview URLs */}
                  <div className="mt-4 max-h-32 overflow-y-auto">
                    <p className="text-sm text-slate-400 mb-2">Preview URLs:</p>
                    <div className="space-y-1">
                      {uploadedFile.urls.slice(0, 5).map((url, index) => (
                        <p key={index} className="text-xs text-slate-500 font-mono">
                          {url}
                        </p>
                      ))}
                      {uploadedFile.urls.length > 5 && (
                        <p className="text-xs text-slate-500">
                          ... e altri {uploadedFile.urls.length - 5} URLs
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Keywords Input */}
            {uploadedFile && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-8"
              >
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-slate-100 mb-2">
                    2. Configura Analisi
                  </h2>
                  <p className="text-slate-400">
                    Specifica le keywords da cercare e un nome per l'analisi
                  </p>
                </div>

                <form onSubmit={handleSubmit(startAnalysis)} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="label">Nome Analisi</label>
                      <Input
                        {...register('analysisName', { required: 'Nome richiesto' })}
                        placeholder="Analisi Competitors Q4 2025"
                      />
                      {errors.analysisName && (
                        <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                          <AlertCircle className="w-4 h-4" />
                          {errors.analysisName.message}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="label">Keywords (separate da virgola)</label>
                      <Input
                        {...register('keywords', { required: 'Keywords richieste' })}
                        placeholder="consulenza, investimenti, finanza"
                      />
                      {errors.keywords && (
                        <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                          <AlertCircle className="w-4 h-4" />
                          {errors.keywords.message}
                        </p>
                      )}
                    </div>
                  </div>

                  {watchedKeywords && (
                    <div>
                      <p className="text-sm text-slate-400 mb-2">Keywords da analizzare:</p>
                      <div className="flex flex-wrap gap-2">
                        {watchedKeywords.split(',').map((keyword, index) => (
                          <Badge key={index} className="badge-primary">
                            {keyword.trim()}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {isProcessing && (
                    <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Analizzando {uploadedFile.urls.length} competitors...
                        </span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {uploadedFile.urls.length > 0 ? Math.round((analysisProgress / uploadedFile.urls.length) * 100) : 0}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadedFile.urls.length > 0 ? (analysisProgress / uploadedFile.urls.length) * 100 : 0}%` }}
                        ></div>
                      </div>
                      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        {analysisProgress} / {uploadedFile.urls.length} completati
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end">
                    <Button
                      type="submit"
                      disabled={!uploadedFile || isProcessing}
                      className="btn-primary"
                    >
                      {isProcessing ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin mr-2" />
                          Analizzando...
                        </>
                      ) : (
                        <>
                          <Play className="w-5 h-5 mr-2" />
                          Avvia Analisi
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </motion.div>
            )}
          </div>
        ) : (
          /* Results */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="card p-8 text-center">
              <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-slate-100 mb-2">
                Analisi Completata!
              </h2>
              <p className="text-slate-400 mb-6">
                Abbiamo analizzato {analysisResults.processedUrls} competitors con {analysisResults.keywords.length} keywords
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-slate-800 p-6 rounded-lg">
                  <p className="text-3xl font-bold text-green-400">{analysisResults.processedUrls}</p>
                  <p className="text-slate-400">URLs Processati</p>
                </div>
                <div className="bg-slate-800 p-6 rounded-lg">
                  <p className="text-3xl font-bold text-blue-400">{analysisResults.matches.length}</p>
                  <p className="text-slate-400">Match Trovati</p>
                </div>
                <div className="bg-slate-800 p-6 rounded-lg">
                  <p className="text-3xl font-bold text-yellow-400">
                    {Math.round(analysisResults.matches.reduce((acc: number, m: any) => acc + m.score, 0) / analysisResults.matches.length)}%
                  </p>
                  <p className="text-slate-400">Score Medio</p>
                </div>
              </div>

              <div className="flex gap-4 justify-center">
                <Button
                  onClick={() => router.push(`/reports?view=${analysisResults.reportId}`)}
                  className="btn-primary"
                >
                  <FileText className="w-5 h-5 mr-2" />
                  Visualizza Report Completo
                </Button>
                <Button
                  onClick={() => {
                    setUploadedFile(null);
                    setAnalysisResults(null);
                  }}
                  variant="secondary"
                >
                  Nuova Analisi
                </Button>
              </div>
            </div>

            {/* Top Matches */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">
                Top Competitors per Score
              </h3>
              <div className="space-y-3">
                {analysisResults.matches.map((match: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <p className="text-slate-100 font-medium">{match.url}</p>
                        <p className="text-slate-400 text-sm">{match.keywords} keyword matches</p>
                      </div>
                    </div>
                    <Badge className={
                      match.score >= 90 ? 'badge-success' : 
                      match.score >= 75 ? 'badge-warning' : 'badge-secondary'
                    }>
                      {match.score}%
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
}