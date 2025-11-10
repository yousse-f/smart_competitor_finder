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
  Zap
} from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

interface DashboardStats {
  totalAnalyses: number;
  competitorsFound: number;
  reportsGenerated: number;
  avgMatchScore: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalAnalyses: 0,
    competitorsFound: 0,
    reportsGenerated: 0,
    avgMatchScore: 0
  });

  useEffect(() => {
    // Simulate loading stats with animation
    const timer = setTimeout(() => {
      setStats({
        totalAnalyses: 127,
        competitorsFound: 2485,
        reportsGenerated: 89,
        avgMatchScore: 87.3
      });
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const quickActions = [
    {
      title: 'Analizza Nuovo Sito',
      description: 'Estrai keywords e trova competitors',
      icon: Search,
      href: '/analyze',
      color: 'from-primary-500 to-secondary-400'
    },
    {
      title: 'Carica Excel',
      description: 'Analisi bulk di competitors',
      icon: FileText,
      href: '/upload',
      color: 'from-secondary-500 to-primary-400'
    },
    {
      title: 'Visualizza Report',
      description: 'Scarica analisi completate',
      icon: BarChart3,
      href: '/reports',
      color: 'from-green-500 to-emerald-400'
    }
  ];

  const recentAnalyses = [
    {
      url: 'fintech-solutions.com',
      keywords: 15,
      competitors: 23,
      score: 92,
      date: '2 ore fa'
    },
    {
      url: 'consulting-group.it',
      keywords: 12,
      competitors: 18,
      score: 88,
      date: '5 ore fa'
    },
    {
      url: 'digital-advisory.eu',
      keywords: 20,
      competitors: 31,
      score: 85,
      date: '1 giorno fa'
    }
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-primary-500 to-secondary-400 rounded-2xl p-8 text-white"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
              <Zap className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-2">
                Benvenuto nella Dashboard
              </h1>
              <p className="text-white/90 text-lg">
                Analizza competitors e genera insights con AI avanzata
              </p>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { 
              label: 'Analisi Totali', 
              value: stats.totalAnalyses, 
              icon: Search, 
              color: 'text-primary-400' 
            },
            { 
              label: 'Competitors Trovati', 
              value: stats.competitorsFound, 
              icon: Users, 
              color: 'text-secondary-400' 
            },
            { 
              label: 'Report Generati', 
              value: stats.reportsGenerated, 
              icon: FileText, 
              color: 'text-green-400' 
            },
            { 
              label: 'Score Medio', 
              value: `${stats.avgMatchScore}%`, 
              icon: TrendingUp, 
              color: 'text-yellow-400' 
            }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold text-slate-100">
                    {typeof stat.value === 'number' ? 
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 + index * 0.1 }}
                      >
                        {stat.value.toLocaleString()}
                      </motion.span>
                      : stat.value
                    }
                  </p>
                </div>
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-xl font-semibold text-slate-100 mb-6">
            Azioni Rapide
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action, index) => (
              <motion.div
                key={action.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="card card-hover p-6 cursor-pointer group"
                onClick={() => window.location.href = action.href}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${action.color} p-3 mb-4`}>
                  <action.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-100 mb-2">
                  {action.title}
                </h3>
                <p className="text-slate-400 text-sm mb-4">
                  {action.description}
                </p>
                <div className="flex items-center text-primary-400 text-sm group-hover:text-primary-300 transition-colors">
                  Inizia
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Recent Analyses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h2 className="text-xl font-semibold text-slate-100 mb-6">
            Analisi Recenti
          </h2>
          <div className="card">
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Sito Web</th>
                    <th>Keywords</th>
                    <th>Competitors</th>
                    <th>Score</th>
                    <th>Data</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAnalyses.map((analysis, index) => (
                    <motion.tr
                      key={analysis.url}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                    >
                      <td>
                        <div className="flex items-center gap-3">
                          <Globe className="w-4 h-4 text-slate-400" />
                          <span className="text-slate-300">{analysis.url}</span>
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
                      <td className="text-slate-400">{analysis.date}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
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