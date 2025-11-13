'use client';

import { useState, useMemo, useEffect, Suspense } from 'react';
import { motion } from 'framer-motion';
import { useSearchParams } from 'next/navigation';
import { 
  FileText, 
  Download, 
  Search, 
  Filter,
  Eye,
  Trash2,
  Calendar,
  TrendingUp,
  BarChart3,
  ExternalLink,
  Sparkles,
  RefreshCw,
  Package
} from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';

// Disable static generation for this page (uses useSearchParams)
export const dynamic = 'force-dynamic';

interface Report {
  id: string;
  name: string;
  date: string;
  status: 'completed' | 'processing' | 'failed';
  competitors: number;
  keywords: number;
  avgScore: number;
  clientUrl: string;
  type: 'single' | 'bulk';
  matches?: any[];
  targetKeywords?: string[];
  summary?: string;
  createdAt?: string;
}

interface CompetitorResult {
  url: string;
  score: number;
  keywordMatches: string[];
  title: string;
  description: string;
  lastAnalyzed: string;
}



export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [viewReportId, setViewReportId] = useState<string | null>(null);
  const [liveAnalyses, setLiveAnalyses] = useState<any[]>([]);
  const [isLoadingLiveAnalyses, setIsLoadingLiveAnalyses] = useState(true);
  
  // 🆕 Stati per streaming live
  const [streamingAnalysisId, setStreamingAnalysisId] = useState<string | null>(null);
  const [streamProgress, setStreamProgress] = useState(0);
  const [streamCurrentUrl, setStreamCurrentUrl] = useState('');
  const [streamResults, setStreamResults] = useState<any[]>([]);
  
  // 🆕 Stati per modal download
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [selectedReportForDownload, setSelectedReportForDownload] = useState<string | null>(null);

  // Get URL search params client-side
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      setViewReportId(params.get('view'));
    }
  }, []);

  // Helper function to normalize competitor data
  const normalizeCompetitorData = (competitor: any): CompetitorResult => {
    return {
      url: competitor.url,
      score: competitor.score || 0,
      keywordMatches: competitor.matched_keywords || competitor.keywordMatches || [],
      title: competitor.title || `Analysis for ${competitor.url}`,
      description: competitor.description || 'Competitor analysis',
      lastAnalyzed: competitor.lastAnalyzed || new Date().toISOString()
    };
  };
  
  // 🆕 Helper per classificare competitor in base allo score (sistema KPI)
  const getCompetitorStatus = (score: number) => {
    if (score >= 60) {
      return {
        category: 'DIRECT',
        label: 'Competitor Diretto',
        emoji: '🟢',
        color: 'green',
        badgeClass: 'badge-success'
      };
    } else if (score >= 40) {
      return {
        category: 'POTENTIAL',
        label: 'Da Valutare',
        emoji: '🟡',
        color: 'yellow',
        badgeClass: 'badge-warning'
      };
    } else {
      return {
        category: 'NON_COMPETITOR',
        label: 'Non Competitor',
        emoji: '🔴',
        color: 'red',
        badgeClass: 'badge-error'
      };
    }
  };
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'reports' | 'details'>('reports');

  // 🆕 Funzione per caricare analisi in corso dal backend
  const loadLiveAnalyses = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // 🔍 Controlla se c'è un'analisi in corso nel localStorage
      const currentAnalysisId = localStorage.getItem('current_analysis_id');
      const analysisStartedAt = localStorage.getItem('analysis_started_at');
      
      if (currentAnalysisId) {
        console.log('🔍 Trovata analisi in localStorage:', currentAnalysisId);
        
        // Carica i dettagli dell'analisi specifica
        try {
          const analysisResponse = await fetch(`${API_BASE_URL}/api/analyses/${currentAnalysisId}`);
          if (analysisResponse.ok) {
            const analysisData = await analysisResponse.json();
            
            // Se l'analisi è completata o fallita, rimuovi dal localStorage
            if (analysisData.metadata.status === 'completed' || analysisData.metadata.status === 'failed') {
              console.log('✅ Analisi terminata, rimuovo da localStorage');
              localStorage.removeItem('current_analysis_id');
              localStorage.removeItem('analysis_started_at');
            } else {
              console.log('📊 Analisi ancora in corso:', analysisData.metadata.progress + '%');
            }
          } else if (analysisResponse.status === 404) {
            // Analisi non trovata, rimuovi dal localStorage
            console.log('⚠️ Analisi non trovata, rimuovo da localStorage');
            localStorage.removeItem('current_analysis_id');
            localStorage.removeItem('analysis_started_at');
          }
        } catch (error) {
          console.error('❌ Errore nel recupero analisi specifica:', error);
        }
      }
      
      // Carica tutte le analisi
      const response = await fetch(`${API_BASE_URL}/api/analyze-bulk`);
      
      if (response.ok) {
        const data = await response.json();
        setLiveAnalyses(data.analyses || []);
        console.log('📊 Loaded live analyses:', data.analyses?.length || 0);
      }
    } catch (error) {
      console.error('❌ Error loading live analyses:', error);
    } finally {
      setIsLoadingLiveAnalyses(false);
    }
  };

  // 🆕 Funzione per eliminare analisi vecchie dal backend
  const cleanupOldAnalyses = async (daysOld: number = 1) => {
    if (!confirm(`Vuoi eliminare tutte le analisi più vecchie di ${daysOld} ${daysOld === 1 ? 'giorno' : 'giorni'}?`)) {
      return;
    }
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/analyze-bulk?days_old=${daysOld}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✅ Eliminate ${data.deleted_count} analisi vecchie. Rimangono ${data.remaining_analyses} analisi.`);
        // Ricarica le analisi
        loadLiveAnalyses();
      } else {
        throw new Error('Errore nella pulizia delle analisi');
      }
    } catch (error) {
      console.error('❌ Error cleaning up analyses:', error);
      alert('Errore durante la pulizia delle analisi');
    }
  };

  // 🆕 Funzione per eliminare una singola analisi
  const deleteSingleAnalysis = async (analysisId: string) => {
    if (!confirm(`Vuoi eliminare l'analisi ${analysisId}?`)) {
      return;
    }
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/analyze-bulk/${analysisId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        alert(`✅ Analisi ${analysisId} eliminata con successo`);
        // Ricarica le analisi
        loadLiveAnalyses();
      } else {
        throw new Error('Errore nell\'eliminazione dell\'analisi');
      }
    } catch (error) {
      console.error('❌ Error deleting analysis:', error);
      alert('Errore durante l\'eliminazione dell\'analisi');
    }
  };

  // Load reports from localStorage on component mount
  useEffect(() => {
    try {
      const savedReports = localStorage.getItem('competitorReports');
      if (savedReports) {
        const parsedReports = JSON.parse(savedReports);
        setReports(parsedReports);
      }
    } catch (error) {
      console.error('Error loading reports from localStorage:', error);
    }
    
    // 🆕 Carica anche le analisi in corso dal backend
    loadLiveAnalyses();
    
    // 🆕 Auto-refresh ogni 10 secondi se ci sono analisi in corso
    const intervalId = setInterval(() => {
      loadLiveAnalyses();
    }, 10000);
    
    return () => clearInterval(intervalId);
  }, []); // Remove reports from dependencies

  // 🆕 Funzione per riconnettersi allo stream di un'analisi
  const reconnectToStream = async (analysisId: string) => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      setStreamingAnalysisId(analysisId);
      setStreamResults([]);
      setStreamProgress(0);
      
      console.log('🔄 Reconnecting to stream:', analysisId);
      
      const response = await fetch(`${API_BASE_URL}/api/analyses/${analysisId}/stream`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('No response body reader available');
      }
      
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            console.log('📨 Stream event:', data.event);
            
            switch (data.event) {
              case 'reconnected':
                console.log('🔄 Reconnected:', data.status);
                if (data.current && data.total) {
                  setStreamProgress(Math.round((data.current / data.total) * 100));
                }
                break;
                
              case 'result':
                console.log('✅ Result:', data.url, data.score);
                setStreamResults(prev => [...prev, data]);
                break;
                
              case 'complete':
                console.log('🎉 Stream complete');
                setStreamProgress(100);
                // Ricarica le analisi per aggiornare lo stato
                setTimeout(() => {
                  loadLiveAnalyses();
                  setStreamingAnalysisId(null);
                }, 2000);
                break;
                
              case 'error':
                console.error('❌ Stream error:', data.message);
                alert(`Errore: ${data.message}`);
                setStreamingAnalysisId(null);
                break;
            }
          }
        }
      }
      
    } catch (error) {
      console.error('❌ Error reconnecting to stream:', error);
      alert('Errore nella riconnessione allo stream');
      setStreamingAnalysisId(null);
    }
  };

  // Separate useEffect for handling specific report view
  useEffect(() => {
    if (viewReportId && reports.length > 0) {
      // Find the report by ID
      const reportToView = reports.find(r => r.id === viewReportId);
      if (reportToView) {
        setSelectedReport(reportToView);
        setViewMode('details');
      }
    }
  }, [viewReportId, reports]);

  const filteredReports = useMemo(() => {
    return reports.filter(report => {
      const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           report.clientUrl.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || report.status === statusFilter;
      const matchesType = typeFilter === 'all' || report.type === typeFilter;
      
      return matchesSearch && matchesStatus && matchesType;
    });
  }, [reports, searchTerm, statusFilter, typeFilter]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed': return 'badge-success';
      case 'processing': return 'badge-warning';
      case 'failed': return 'badge-error';
      default: return 'badge-secondary';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completato';
      case 'processing': return 'In elaborazione';
      case 'failed': return 'Errore';
      default: return 'Sconosciuto';
    }
  };

  const downloadReport = (reportId: string, format: string) => {
    try {
      const report = reports.find(r => r.id === reportId);
      if (!report) {
        alert('Report non trovato');
        return;
      }

      if (format === 'excel') {
        downloadExcelReport(report);
      } else if (format === 'pdf') {
        downloadPdfReport(report);
      }
      
      // Chiudi il modal dopo il download
      setShowDownloadModal(false);
      setSelectedReportForDownload(null);
    } catch (error) {
      console.error('Errore durante il download:', error);
      alert('Errore durante il download del report');
    }
  };
  
  // 🆕 Funzione per aprire il modal di download
  const handleDownloadClick = (reportId: string) => {
    setSelectedReportForDownload(reportId);
    setShowDownloadModal(true);
  };

  const downloadExcelReport = (report: Report) => {
    // Importiamo xlsx dinamicamente per evitare problemi SSR
    import('xlsx').then((XLSX) => {
      // Prepariamo i dati per Excel
      const worksheetData = [];
      
      // Header del report
      worksheetData.push(['Smart Competitor Finder - Report Analisi']);
      worksheetData.push(['']);
      worksheetData.push(['Nome Report:', report.name]);
      worksheetData.push(['Data Analisi:', new Date(report.date).toLocaleDateString('it-IT')]);
      worksheetData.push(['Sito Cliente:', report.clientUrl]);
      worksheetData.push(['Numero Competitors:', report.competitors]);
      worksheetData.push(['Numero Keywords:', report.keywords]);
      worksheetData.push(['Score Medio:', `${report.avgScore}%`]);
      worksheetData.push(['']);
      
      // Keywords target se disponibili
      if (report.targetKeywords && report.targetKeywords.length > 0) {
        worksheetData.push(['Keywords Target:']);
        report.targetKeywords.forEach(keyword => {
          worksheetData.push(['', keyword]);
        });
        worksheetData.push(['']);
      }
      
      // Header della tabella competitors con KPI
      worksheetData.push(['Rank', 'URL Competitor', 'Categoria KPI', 'Keywords Trovate', 'Keywords Match']);
      
      // Dati competitors con classificazione KPI
      if (report.matches && report.matches.length > 0) {
        report.matches.forEach((comp: any, index: number) => {
          const competitor = normalizeCompetitorData(comp);
          const status = getCompetitorStatus(competitor.score);
          worksheetData.push([
            index + 1,
            competitor.url,
            `${status.emoji} ${status.label}`,
            competitor.keywordMatches.length,
            competitor.keywordMatches.join(', ')
          ]);
        });
      }
      
      // Creiamo il workbook
      const workbook = XLSX.utils.book_new();
      const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
      
      // Styling per il header
      const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1');
      for (let row = 0; row <= range.e.r; row++) {
        for (let col = 0; col <= range.e.c; col++) {
          const cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
          if (!worksheet[cellAddress]) continue;
          
          // Stile per il titolo principale
          if (row === 0) {
            worksheet[cellAddress].s = {
              font: { bold: true, sz: 16 },
              alignment: { horizontal: 'center' }
            };
          }
          // Stile per gli header della tabella
          else if (row === worksheetData.findIndex(row => row[0] === 'Rank')) {
            worksheet[cellAddress].s = {
              font: { bold: true },
              fill: { fgColor: { rgb: 'E2E8F0' } }
            };
          }
        }
      }
      
      // Imposta larghezza colonne con KPI (senza colonna Score)
      worksheet['!cols'] = [
        { width: 8 },   // Rank
        { width: 35 },  // URL
        { width: 25 },  // Categoria KPI
        { width: 15 },  // Keywords Trovate
        { width: 45 }   // Keywords Match
      ];
      
      // Aggiungi il worksheet al workbook
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Report Competitors');
      
      // Download del file
      const fileName = `${report.name.replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().toISOString().split('T')[0]}.xlsx`;
      XLSX.writeFile(workbook, fileName);
      
      console.log(`✅ Report Excel scaricato: ${fileName}`);
    }).catch(error => {
      console.error('Errore durante l\'importazione di xlsx:', error);
      alert('Errore durante la generazione del file Excel');
    });
  };

  const downloadPdfReport = (report: Report) => {
    // Usiamo solo jsPDF e creiamo la tabella manualmente
    import('jspdf').then((jsPDFModule) => {
      const jsPDF = jsPDFModule.default;
      const doc = new jsPDF();
      
      // Configurazione colori
      const primaryColor: [number, number, number] = [59, 130, 246]; // Blue-500
      const textColor: [number, number, number] = [51, 65, 85]; // Slate-700
      
      // Header del documento
      doc.setFillColor(...primaryColor);
      doc.rect(0, 0, 210, 30, 'F');
      
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text('Smart Competitor Finder', 20, 20);
      
      doc.setFontSize(12);
      doc.setFont('helvetica', 'normal');
      doc.text('Report di Analisi Competitiva', 20, 26);
      
      // Reset colore testo
      doc.setTextColor(...textColor);
      
      // Informazioni del report
      let yPosition = 45;
      doc.setFontSize(16);
      doc.setFont('helvetica', 'bold');
      doc.text('Dettagli Report', 20, yPosition);
      
      yPosition += 10;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      
      const reportInfo = [
        ['Nome Report:', report.name],
        ['Data Analisi:', new Date(report.date).toLocaleDateString('it-IT')],
        ['Sito Cliente:', report.clientUrl],
        ['Numero Competitors:', report.competitors.toString()],
        ['Numero Keywords:', report.keywords.toString()],
        ['Score Medio:', `${report.avgScore}%`],
        ['Tipo Analisi:', report.type === 'bulk' ? 'Analisi Bulk' : 'Analisi Singola']
      ];
      
      reportInfo.forEach(([label, value]) => {
        doc.setFont('helvetica', 'bold');
        doc.text(label, 20, yPosition);
        doc.setFont('helvetica', 'normal');
        doc.text(value, 80, yPosition);
        yPosition += 7;
      });
      
      // Keywords target se disponibili
      if (report.targetKeywords && report.targetKeywords.length > 0) {
        yPosition += 5;
        doc.setFont('helvetica', 'bold');
        doc.text('Keywords Target:', 20, yPosition);
        yPosition += 7;
        
        doc.setFont('helvetica', 'normal');
        const keywordsText = report.targetKeywords.join(', ');
        const splitKeywords = doc.splitTextToSize(keywordsText, 170);
        doc.text(splitKeywords, 20, yPosition);
        yPosition += splitKeywords.length * 5 + 5;
      }
      
      // Tabella competitors (creata manualmente)
      if (report.matches && report.matches.length > 0) {
        yPosition += 10;
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(14);
        doc.text('Top Competitors Trovati', 20, yPosition);
        yPosition += 10;
        
        // Header della tabella
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setFillColor(...primaryColor);
        doc.rect(20, yPosition, 170, 8, 'F');
        doc.setTextColor(255, 255, 255);
        
        // Colonne header con KPI (senza Score)
        doc.text('Rank', 25, yPosition + 5);
        doc.text('URL Competitor', 50, yPosition + 5);
        doc.text('Categoria KPI', 120, yPosition + 5);
        doc.text('Keywords', 170, yPosition + 5);
        
        yPosition += 12;
        doc.setTextColor(...textColor);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        
        // Righe della tabella con classificazione KPI
        report.matches.slice(0, 20).forEach((comp: any, index: number) => {
          const competitor = normalizeCompetitorData(comp);
          const status = getCompetitorStatus(competitor.score);
          
          // Riga alternata con colore KPI
          if (status.color === 'green') {
            doc.setFillColor(230, 249, 230);
          } else if (status.color === 'yellow') {
            doc.setFillColor(255, 249, 230);
          } else {
            doc.setFillColor(255, 230, 230);
          }
          doc.rect(20, yPosition - 3, 170, 7, 'F');
          
          // Dati della riga (senza Score)
          doc.text((index + 1).toString(), 27, yPosition);
          
          // URL troncato se troppo lungo
          const urlText = competitor.url.length > 30 ? 
            competitor.url.substring(0, 27) + '...' : competitor.url;
          doc.text(urlText, 50, yPosition);
          
          // Use text-only label for PDF (emoji causes encoding issues in jsPDF)
          doc.text(status.label, 120, yPosition);
          doc.text(competitor.keywordMatches.length.toString(), 177, yPosition);
          
          yPosition += 7;
          
          // Nuova pagina se necessario
          if (yPosition > 270) {
            doc.addPage();
            yPosition = 20;
          }
        });
      }
      
      // Footer
      doc.setFontSize(8);
      doc.setTextColor(128);
      doc.text(
        `Generato il ${new Date().toLocaleDateString('it-IT')}`,
        20,
        doc.internal.pageSize.height - 10
      );
      
      doc.text(
        'Report generato da Smart Competitor Finder - Analisi competitiva avanzata',
        20,
        doc.internal.pageSize.height - 5
      );
      
      // Download del file
      const fileName = `${report.name.replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      doc.save(fileName);
      
      console.log(`✅ Report PDF scaricato: ${fileName}`);
      
    }).catch(error => {
      console.error('Errore durante l\'importazione di jsPDF:', error);
      alert('Errore durante la generazione del file PDF');
    });
  };

  const viewReportDetails = (report: Report) => {
    setSelectedReport(report);
    setViewMode('details');
  };

  const deleteReport = (reportId: string) => {
    const report = reports.find(r => r.id === reportId);
    const reportName = report ? report.name : 'questo report';
    
    if (confirm(`Sei sicuro di voler eliminare "${reportName}"?\n\nQuesta azione non può essere annullata.`)) {
      try {
        // Rimuovi il report dall'array
        const updatedReports = reports.filter(r => r.id !== reportId);
        
        // Aggiorna lo stato
        setReports(updatedReports);
        
        // Aggiorna localStorage
        localStorage.setItem('competitorReports', JSON.stringify(updatedReports));
        
        // Se stiamo visualizzando i dettagli del report eliminato, torna alla lista
        if (selectedReport && selectedReport.id === reportId) {
          setSelectedReport(null);
          setViewMode('reports');
        }
        
        console.log(`✅ Report eliminato: ${reportName}`);
        
        // Mostra messaggio di successo
        const successMessage = document.createElement('div');
        successMessage.innerHTML = `
          <div style="position: fixed; top: 20px; right: 20px; background: #059669; color: white; padding: 12px 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999; font-family: system-ui;">
            ✅ Report "${reportName}" eliminato con successo
          </div>
        `;
        document.body.appendChild(successMessage);
        
        // Rimuovi il messaggio dopo 3 secondi
        setTimeout(() => {
          if (successMessage.parentNode) {
            successMessage.parentNode.removeChild(successMessage);
          }
        }, 3000);
        
      } catch (error) {
        console.error('Errore durante l\'eliminazione del report:', error);
        alert('Errore durante l\'eliminazione del report');
      }
    }
  };

  if (viewMode === 'details' && selectedReport) {
    return (
      <DashboardLayout>
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <Button
                onClick={() => {
                  setViewMode('reports');
                  setSelectedReport(null);
                }}
                variant="ghost"
                className="mb-4"
              >
                ← Torna ai Report
              </Button>
              <h1 className="text-3xl font-bold text-slate-100 mb-2">
                {selectedReport.name}
              </h1>
              <p className="text-slate-400">
                Analisi completata il {new Date(selectedReport.date).toLocaleDateString('it-IT')}
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                onClick={() => downloadReport(selectedReport.id, 'excel')}
                className="btn-primary"
              >
                <Download className="w-4 h-4 mr-2" />
                Excel
              </Button>
              <Button
                onClick={() => downloadReport(selectedReport.id, 'pdf')}
                variant="secondary"
              >
                <Download className="w-4 h-4 mr-2" />
                PDF
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Competitors</p>
                  <p className="text-2xl font-bold text-slate-100">{selectedReport.competitors}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-primary-400" />
              </div>
            </div>
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Keywords</p>
                  <p className="text-2xl font-bold text-slate-100">{selectedReport.keywords}</p>
                </div>
                <Search className="w-8 h-8 text-secondary-400" />
              </div>
            </div>
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Score Medio</p>
                  <p className="text-2xl font-bold text-slate-100">{selectedReport.avgScore}%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-400" />
              </div>
            </div>
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Sito Cliente</p>
                  <p className="text-lg font-medium text-slate-100 truncate">{selectedReport.clientUrl}</p>
                </div>
                <ExternalLink className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
          </div>

          {/* Competitors Table */}
          <div className="card">
            <div className="p-6 border-b border-slate-700">
              <h2 className="text-xl font-semibold text-slate-100">
                Top Competitors Trovati
              </h2>
              <p className="text-slate-400 mt-1">
                Risultati ordinati per score di rilevanza
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Competitor</th>
                    <th>Categoria KPI</th>
                    <th>Keywords Match</th>
                    <th>Ultima Analisi</th>
                    <th>Azioni</th>
                  </tr>
                </thead>
                <tbody>
                  {(selectedReport.matches || []).map((comp: any, index: number) => {
                    const competitor = selectedReport.matches ? normalizeCompetitorData(comp) : comp;
                    return (
                    <motion.tr
                      key={`${competitor.url}-${index}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <td>
                        <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                          {index + 1}
                        </div>
                      </td>
                      <td>
                        <div>
                          <p className="font-medium text-slate-100">{competitor.url}</p>
                          <p className="text-sm text-slate-400 truncate max-w-xs">
                            {competitor.title}
                          </p>
                        </div>
                      </td>
                      <td>
                        {(() => {
                          const status = getCompetitorStatus(competitor.score);
                          return (
                            <div className="space-y-1">
                              <Badge className={status.badgeClass}>
                                {status.emoji} {status.label}
                              </Badge>
                              <p className="text-xs text-slate-400">{competitor.score}%</p>
                            </div>
                          );
                        })()}
                      </td>
                      <td>
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {competitor.keywordMatches.slice(0, 3).map((keyword: string, i: number) => (
                            <Badge key={i} className="badge-primary text-xs">
                              {keyword}
                            </Badge>
                          ))}
                          {competitor.keywordMatches.length > 3 && (
                            <Badge className="badge-secondary text-xs">
                              +{competitor.keywordMatches.length - 3}
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td className="text-slate-400 text-sm">
                        {new Date(competitor.lastAnalyzed).toLocaleString('it-IT')}
                      </td>
                      <td>
                        <Button
                          onClick={() => window.open(`https://${competitor.url}`, '_blank')}
                          variant="ghost"
                          size="sm"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </td>
                    </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">
              Report Competitivi
            </h1>
            <p className="text-slate-400">
              Gestisci, scarica e rivedi tutte le analisi generate con l'AI.
            </p>
            <p className="text-slate-500 text-sm mt-1">
              Perfetto per clienti, presentazioni e benchmarking di mercato.
            </p>
          </div>
          <Button
            onClick={() => window.location.href = '/analyze'}
            className="btn-primary"
          >
            <FileText className="w-5 h-5 mr-2" />
            Nuova Analisi
          </Button>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6"
        >
          <h3 className="text-lg font-semibold text-slate-100 mb-4">
            Filtra i tuoi Report
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="label">🔍 Cerca per nome o dominio</label>
              <div className="relative">
                <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <Input
                  placeholder="Nome cliente o URL..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <label className="label">📌 Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input"
              >
                <option value="all">Tutti</option>
                <option value="completed">Completato</option>
                <option value="processing">In corso</option>
                <option value="failed">Con errori</option>
              </select>
            </div>

            <div>
              <label className="label">📁 Tipo</label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="input"
              >
                <option value="all">Tutti</option>
                <option value="single">Analisi Singola</option>
                <option value="bulk">Analisi Bulk</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                  setTypeFilter('all');
                }}
                variant="secondary"
                className="w-full"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                🔄 Reset
              </Button>
            </div>
          </div>
          
          {/* 🆕 Suggerimenti sotto i filtri */}
          <div className="mt-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <p className="text-sm text-slate-400">
              <span className="font-semibold text-slate-300">💡 Suggerimenti:</span>
            </p>
            <ul className="text-xs text-slate-500 mt-2 space-y-1 ml-4">
              <li>• Cerca per nome cliente o dominio</li>
              <li>• Filtra per stato (in corso / completato)</li>
              <li>• Filtra per tipo (analisi singola o bulk)</li>
            </ul>
          </div>
        </motion.div>

        {/* 🆕 Analisi in Corso */}
        {liveAnalyses.filter(a => a.status === 'in_progress').length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6 bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-2 border-blue-500/30"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
                <h3 className="text-lg font-semibold text-slate-100">
                  Analisi in Corso ({liveAnalyses.filter(a => a.status === 'in_progress').length})
                </h3>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => cleanupOldAnalyses(1)}
                  variant="secondary"
                  size="sm"
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Pulisci Vecchie
                </Button>
                <Button
                  onClick={loadLiveAnalyses}
                  variant="secondary"
                  size="sm"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Aggiorna
                </Button>
              </div>
            </div>
            
            <div className="space-y-3">
              {liveAnalyses
                .filter(a => a.status === 'in_progress')
                .map((analysis) => {
                  // 🔍 Controlla se questa è l'analisi corrente da localStorage
                  const currentAnalysisId = localStorage.getItem('current_analysis_id');
                  const isCurrentAnalysis = analysis.id === currentAnalysisId;
                  
                  return (
                  <div
                    key={analysis.id}
                    className={`p-4 bg-slate-800/50 rounded-lg border transition-colors ${
                      isCurrentAnalysis 
                        ? 'border-green-500/40 bg-green-500/5' 
                        : 'border-blue-500/20 hover:border-blue-500/40'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="text-slate-100 font-medium">
                            Analisi {analysis.id}
                          </p>
                          {isCurrentAnalysis && (
                            <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-xs px-2 py-0.5">
                              🔴 LIVE
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-slate-400">
                          Avviata: {new Date(analysis.started_at).toLocaleString('it-IT')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-blue-400">
                          {streamingAnalysisId === analysis.id ? streamProgress : analysis.progress}%
                        </p>
                        <p className="text-xs text-slate-400">
                          {analysis.processed_sites}/{analysis.total_sites} siti
                        </p>
                      </div>
                    </div>
                    
                    {/* Progress bar */}
                    <div className="w-full bg-slate-700/50 rounded-full h-2 mb-3 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${streamingAnalysisId === analysis.id ? streamProgress : analysis.progress}%` }}
                      ></div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <Badge className="badge-info">
                        {streamingAnalysisId === analysis.id ? '🔴 Streaming Live' : 'In Corso'}
                      </Badge>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => deleteSingleAnalysis(analysis.id)}
                          variant="ghost"
                          size="sm"
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                        <Button
                          onClick={() => reconnectToStream(analysis.id)}
                          variant="secondary"
                          size="sm"
                          disabled={streamingAnalysisId === analysis.id}
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          {streamingAnalysisId === analysis.id ? 'Connesso' : 'Visualizza Live'}
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Reports Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-slate-100">
                I Tuoi Report ({filteredReports.length})
              </h2>
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-slate-400" />
                <span className="text-sm text-slate-400">
                  {filteredReports.length} report{filteredReports.length !== 1 ? '' : ''}
                </span>
              </div>
            </div>
          </div>

          <div className="w-full">
            <table className="table w-full table-fixed">
              <thead>
                <tr>
                  <th className="w-[35%]">Nome Report</th>
                  <th className="w-[12%]">Data</th>
                  <th className="w-[12%]">Stato</th>
                  <th className="w-[10%]">Tipo</th>
                  <th className="w-[10%]">Competitors</th>
                  <th className="w-[21%] text-right">Azioni</th>
                </tr>
              </thead>
              <tbody>
                {filteredReports.map((report, index) => (
                  <motion.tr
                    key={report.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <td className="max-w-xs">
                      <div className="overflow-hidden">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium text-slate-100 truncate">{report.name}</p>
                        </div>
                        <p className="text-xs text-slate-500">
                          {report.type === 'bulk' ? '📦 Bulk' : '📁 Singola'} • {report.competitors} competitor analizzati
                        </p>
                      </div>
                    </td>
                    <td className="text-slate-300 text-sm whitespace-nowrap">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        {new Date(report.date).toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit' })}
                      </div>
                    </td>
                    <td>
                      <Badge className={getStatusBadge(report.status)}>
                        {report.status === 'completed' && '🟢 '}
                        {report.status === 'processing' && '🟡 '}
                        {report.status === 'failed' && '🔴 '}
                        {getStatusText(report.status)}
                      </Badge>
                    </td>
                    <td>
                      <Badge className={report.type === 'bulk' ? 'badge-primary' : 'badge-secondary'}>
                        {report.type === 'bulk' ? '📦 Bulk' : '📁 Singola'}
                      </Badge>
                    </td>
                    <td className="text-slate-300 text-center font-semibold">{report.competitors}</td>
                    <td>
                      <div className="flex items-center gap-2 justify-end">
                        {report.status === 'completed' && (
                          <>
                            <Button
                              onClick={() => viewReportDetails(report)}
                              variant="ghost"
                              size="sm"
                              title="Visualizza dettagli"
                              className="text-sm"
                            >
                              <Eye className="w-4 h-4 mr-1" />
                              Visualizza
                            </Button>
                            <Button
                              onClick={() => handleDownloadClick(report.id)}
                              variant="ghost"
                              size="sm"
                              title="Scarica Report"
                              className="text-sm"
                            >
                              <Download className="w-4 h-4 mr-1" />
                              Scarica
                            </Button>
                          </>
                        )}
                        <Button
                          onClick={() => deleteReport(report.id)}
                          variant="ghost"
                          size="sm"
                          className="text-red-400 hover:text-red-300 text-sm"
                          title="Elimina report"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Elimina
                        </Button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredReports.length === 0 && (
            <div className="p-12 text-center">
              <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-400 mb-2">
                {reports.length === 0 ? "Nessun report salvato" : "Nessun report trovato"}
              </h3>
              <p className="text-slate-500 mb-6">
                {reports.length === 0 
                  ? "Inizia la tua prima analisi per vedere i report qui" 
                  : "Non ci sono report che corrispondono ai filtri selezionati"
                }
              </p>
              {reports.length === 0 && (
                <Button
                  onClick={() => window.location.href = '/analyze'}
                  className="btn-primary"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Crea il tuo primo report
                </Button>
              )}
            </div>
          )}
        </motion.div>
        
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
        
        {/* 🆕 Modal Elegante per Scelta Formato Download */}
        {showDownloadModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 max-w-md w-full mx-4 overflow-hidden"
            >
              {/* Header */}
              <div className="p-6 border-b border-slate-700 bg-gradient-to-r from-blue-500/10 to-cyan-500/10">
                <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                  <Download className="w-6 h-6 text-cyan-400" />
                  Scegli Formato Export
                </h3>
                <p className="text-sm text-slate-400 mt-1">
                  Seleziona il formato per scaricare il report
                </p>
              </div>
              
              {/* Body - Scelta Formati */}
              <div className="p-6 space-y-3">
                {/* Opzione Excel */}
                <button
                  onClick={() => {
                    if (selectedReportForDownload) {
                      downloadReport(selectedReportForDownload, 'excel');
                    }
                  }}
                  className="w-full p-4 bg-gradient-to-r from-green-500/10 to-emerald-500/10 hover:from-green-500/20 hover:to-emerald-500/20 border border-green-500/30 hover:border-green-500/50 rounded-xl transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-semibold text-slate-100">
                        Excel (.xlsx)
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        Perfetto per analisi dati e presentazioni
                      </div>
                    </div>
                  </div>
                </button>
                
                {/* Opzione PDF */}
                <button
                  onClick={() => {
                    if (selectedReportForDownload) {
                      downloadReport(selectedReportForDownload, 'pdf');
                    }
                  }}
                  className="w-full p-4 bg-gradient-to-r from-red-500/10 to-orange-500/10 hover:from-red-500/20 hover:to-orange-500/20 border border-red-500/30 hover:border-red-500/50 rounded-xl transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-semibold text-slate-100">
                        PDF (.pdf)
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        Ideale per stampa e condivisione
                      </div>
                    </div>
                  </div>
                </button>
              </div>
              
              {/* Footer - Pulsante Annulla */}
              <div className="p-4 border-t border-slate-700 bg-slate-900/50">
                <Button
                  onClick={() => {
                    setShowDownloadModal(false);
                    setSelectedReportForDownload(null);
                  }}
                  variant="secondary"
                  className="w-full"
                >
                  Annulla
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}