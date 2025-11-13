'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Search, 
  FileText, 
  TrendingUp, 
  Users, 
  Globe,
  ArrowRight,
  Zap,
  Clock,
  CheckCircle2,
  Upload,
  Target,
  Award,
  Activity
} from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

interface DashboardStats {
  totalAnalyses: number;
  competitorsFound: number;
  reportsGenerated: number;
  avgMatchScore: number;
  lastAnalysis: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalAnalyses: 0,
    competitorsFound: 0,
    reportsGenerated: 0,
    avgMatchScore: 0,
    lastAnalysis: '2 ore fa'
  });

  useEffect(() => {
    // Simulate loading stats with animation
    const timer = setTimeout(() => {
      setStats({
        totalAnalyses: 127,
        competitorsFound: 2485,
        reportsGenerated: 89,
        avgMatchScore: 87.3,
        lastAnalysis: '2 ore fa'
      });
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const quickActions = [
    {
      title: 'Analizza un Nuovo Sito',
      description: 'Capisci il business del cliente',
      icon: Search,
      href: '/analyze',
      color: 'from-blue-500 to-cyan-400',
      buttonText: 'Analizza Ora'
    },
    {
      title: 'Carica Lista Competitor',
      description: 'Analisi bulk di decine o centinaia di URL',
      icon: Upload,
      href: '/upload',
      color: 'from-cyan-500 to-teal-400',
      buttonText: 'Carica File'
    },
    {
      title: 'Visualizza i Report',
      description: 'Scarica risultati, score e raccomandazioni',
      icon: BarChart3,
      href: '/reports',
      color: 'from-teal-500 to-green-400',
      buttonText: 'Apri Report'
    }
  ];

  const recentAnalyses = [
    {
      url: 'fintech-solutions.com',
      keywords: 15,
      competitors: 23,
      score: 92,
      status: 'completed',
      date: '2 ore fa'
    },
    {
      url: 'consulting-group.it',
      keywords: 12,
      competitors: 18,
      score: 88,
      status: 'completed',
      date: '5 ore fa'
    },
    {
      url: 'digital-advisory.eu',
      keywords: 20,
      competitors: 31,
      score: 85,
      status: 'completed',
      date: '1 giorno fa'
    }
  ];

  const getStatusBadge = (status: string) => {
    if (status === 'completed') {
      return (
        <span className="flex items-center gap-1 text-green-400 text-sm">
          <CheckCircle2 className="w-4 h-4" />
          Completato
        </span>
      );
    }
    return null;
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header Superiore Professionale */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <h1 className="text-4xl font-bold text-slate-100">
            Benvenuto, Federico
          </h1>
          <p className="text-lg text-slate-400">
            La tua piattaforma per analizzare mercati, competitor e siti web in pochi minuti grazie all'AI
          </p>
        </motion.div>

        {/* KPI Section - 5 Cards Migliorate */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {[
            { 
              label: 'Analisi Totali',
              sublabel: 'Totale analisi effettuate',
              value: stats.totalAnalyses, 
              icon: Search, 
              color: 'text-blue-400',
              bgColor: 'bg-blue-500/10'
            },
            { 
              label: 'Competitor Identificati',
              sublabel: 'Match rilevati dall\'AI',
              value: stats.competitorsFound, 
              icon: Users, 
              color: 'text-cyan-400',
              bgColor: 'bg-cyan-500/10'
            },
            { 
              label: 'Report Generati',
              sublabel: 'Report esportati',
              value: stats.reportsGenerated, 
              icon: FileText, 
              color: 'text-green-400',
              bgColor: 'bg-green-500/10'
            },
            { 
              label: 'Score Medio',
              sublabel: 'Affidabilità media analisi',
              value: `${stats.avgMatchScore}%`, 
              icon: TrendingUp, 
              color: 'text-purple-400',
              bgColor: 'bg-purple-500/10'
            },
            { 
              label: 'Ultima Analisi',
              sublabel: 'Tempo dall\'ultima attività',
              value: stats.lastAnalysis, 
              icon: Clock, 
              color: 'text-orange-400',
              bgColor: 'bg-orange-500/10',
              isText: true
            }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card p-6 backdrop-blur-sm"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-xl ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
              <div>
                <p className="text-3xl font-bold text-slate-100 mb-1">
                  {stat.isText ? (
                    stat.value
                  ) : typeof stat.value === 'number' ? (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                    >
                      {stat.value.toLocaleString()}
                    </motion.span>
                  ) : stat.value}
                </p>
                <p className="text-sm font-medium text-slate-300 mb-1">{stat.label}</p>
                <p className="text-xs text-slate-500">{stat.sublabel}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Azioni Rapide - Versione Migliorata */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-2xl font-semibold text-slate-100 mb-6">
            Azioni Rapide
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action, index) => (
              <motion.div
                key={action.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="card card-hover p-8 cursor-pointer group"
                onClick={() => window.location.href = action.href}
              >
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-r ${action.color} p-3 mb-6 group-hover:scale-110 transition-transform`}>
                  <action.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-slate-100 mb-3">
                  {action.title}
                </h3>
                <p className="text-slate-400 mb-6">
                  {action.description}
                </p>
                <div className="flex items-center text-primary-400 font-medium group-hover:text-primary-300 transition-colors">
                  {action.buttonText}
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Analisi Recenti - Versione Potenziata */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h2 className="text-2xl font-semibold text-slate-100 mb-6">
            Analisi Recenti
          </h2>
          <div className="card">
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Sito Web</th>
                    <th>Keywords</th>
                    <th>Competitor</th>
                    <th>Score</th>
                    <th>Stato</th>
                    <th>Data</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAnalyses.map((analysis, index) => (
                    <motion.tr
                      key={analysis.url}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                    >
                      <td>
                        <div className="flex items-center gap-3">
                          <Globe className="w-4 h-4 text-slate-400" />
                          <span className="text-slate-300 font-medium">{analysis.url}</span>
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-primary">
                          {analysis.keywords}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-secondary">
                          {analysis.competitors}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${
                          analysis.score >= 90 ? 'badge-success' : 
                          analysis.score >= 80 ? 'badge-warning' : 'badge-error'
                        }`}>
                          {analysis.score}%
                        </span>
                      </td>
                      <td>
                        {getStatusBadge(analysis.status)}
                      </td>
                      <td className="text-slate-400">{analysis.date}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>

        {/* Panoramica Report (NUOVO - OPZIONALE MA POTENTE) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <h2 className="text-2xl font-semibold text-slate-100 mb-6">
            Panoramica Report
          </h2>
          <div className="card p-8 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-blue-500/10 rounded-xl mx-auto mb-3">
                  <FileText className="w-6 h-6 text-blue-400" />
                </div>
                <p className="text-3xl font-bold text-slate-100 mb-1">89</p>
                <p className="text-sm text-slate-400">Report totali</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-green-500/10 rounded-xl mx-auto mb-3">
                  <Award className="w-6 h-6 text-green-400" />
                </div>
                <p className="text-3xl font-bold text-slate-100 mb-1">95%</p>
                <p className="text-sm text-slate-400">Miglior score</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-purple-500/10 rounded-xl mx-auto mb-3">
                  <Users className="w-6 h-6 text-purple-400" />
                </div>
                <p className="text-3xl font-bold text-slate-100 mb-1">21</p>
                <p className="text-sm text-slate-400">Media competitor per analisi</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-orange-500/10 rounded-xl mx-auto mb-3">
                  <Activity className="w-6 h-6 text-orange-400" />
                </div>
                <p className="text-3xl font-bold text-slate-100 mb-1">Oggi</p>
                <p className="text-sm text-slate-400">Ultimo report generato</p>
              </div>
            </div>
          </div>
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
      </div>
    </DashboardLayout>
  );
}