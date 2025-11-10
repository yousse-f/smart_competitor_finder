import axios from 'axios';

// Configurazione base API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 secondi per analisi lunghe
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors per logging e gestione errori
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Tipi TypeScript per le API
export interface KeywordData {
  keyword: string;
  frequency: number;
  relevance: 'high' | 'medium' | 'low';
  category: string;
}

export interface AnalysisRequest {
  url: string;
}

export interface AnalysisResponse {
  url: string;
  keywords: KeywordData[];
  title?: string;
  description?: string;
  status: 'success' | 'error';
  message?: string;
}

export interface BulkAnalysisRequest {
  keywords: string[];
  competitors_file?: File;
}

export interface CompetitorMatch {
  url: string;
  score: number;
  keywords_found: string[];
  title?: string;
  description?: string;
  competitor_status?: {
    category: 'DIRECT' | 'POTENTIAL' | 'NON_COMPETITOR';
    label: string;
    label_en: string;
    color: string;
    emoji: string;
    priority: number;
    action: string;
  };
}

export interface BulkAnalysisResponse {
  total_competitors: number;
  matches: CompetitorMatch[];
  average_score: number;
  report_id: string;
  status: 'success' | 'error';
  message?: string;
  summary_by_status?: {
    direct: {
      count: number;
      label: string;
      emoji: string;
    };
    potential: {
      count: number;
      label: string;
      emoji: string;
    };
    non_competitor: {
      count: number;
      label: string;
      emoji: string;
    };
  };
}

export interface SiteSummaryResponse {
  url: string;
  business_description: string;
  industry_sector: string;
  target_market: string;
  key_services: string[];
  confidence_score: number;
  processing_time: number;
  status: 'success' | 'error';
}

// Funzioni API
export const analyzeUrl = async (url: string): Promise<AnalysisResponse> => {
  try {
    const response = await apiClient.post('/api/analyze-site', { 
      url,
      max_keywords: 100, // TEST: limite aumentato per analisi completa
      use_advanced_scraping: true
    }, {
      timeout: 90000, // 90 secondi per analisi AI che può richiedere tempo
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Errore durante l\'analisi del sito');
  }
};

export const uploadAndAnalyze = async (
  keywords: string[],
  file: File,
  analysisName?: string
): Promise<BulkAnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('keywords', keywords.join(','));
    
    if (analysisName) {
      formData.append('analysis_name', analysisName);
    }

    console.log('🚀 Sending to backend:', {
      fileName: file.name,
      keywords: keywords.join(','),
      analysisName
    });

    const response = await apiClient.post('/api/upload-and-analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minuti per analisi bulk
    });

    console.log('✅ Backend response:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ Upload and analyze error:', error);
    throw new Error(error.response?.data?.detail || 'Errore durante l\'analisi bulk');
  }
};

export const generateSiteSummary = async (url: string): Promise<SiteSummaryResponse> => {
  try {
    const response = await apiClient.post('/api/generate-site-summary', { 
      url,
      detailed_analysis: false
    }, {
      timeout: 90000, // 90 secondi per analisi AI che richiede tempo
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Errore durante la generazione del riassunto AI');
  }
};

export const downloadReport = async (reportId: string, format: 'excel' | 'pdf' = 'excel'): Promise<Blob> => {
  try {
    const response = await apiClient.get(`/api/report/${reportId}`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Errore durante il download del report');
  }
};

// Utility per gestire gli errori API
export const handleApiError = (error: any): string => {
  if (error.response) {
    // Errore dalla risposta del server
    return error.response.data?.detail || error.response.data?.message || 'Errore del server';
  } else if (error.request) {
    // Errore di rete
    return 'Impossibile connettersi al server. Verifica la connessione internet.';
  } else {
    // Errore generico
    return error.message || 'Errore sconosciuto';
  }
};

// Funzione per verificare lo stato del backend
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('Backend non raggiungibile:', error);
    return false;
  }
};