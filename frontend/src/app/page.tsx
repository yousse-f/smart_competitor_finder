'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Activity, ArrowRight, CheckCircle2, Search, FileSpreadsheet, 
  Zap, Shield, TrendingUp, Users, BarChart3, Target, Clock,
  Sparkles, ChevronRight, Download, Eye, Brain, Database
} from 'lucide-react';
import { Button, Card, CardContent, Badge } from '@/components/ui';

export default function LandingPage() {
  const router = useRouter();

  // Tutti i CTA portano alla pagina di login
  const handleCTA = () => {
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(0,180,216,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(56,189,248,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjAzKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-20" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 border-b border-slate-800/50 backdrop-blur-xl bg-slate-900/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                Smart Competitor Finder
              </span>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <Button 
                variant="primary" 
                size="md"
                onClick={handleCTA}
                className="shadow-lg shadow-blue-500/25"
              >
                Accedi
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Content */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <Badge className="mb-6 bg-blue-500/10 text-blue-400 border-blue-500/20">
                <Sparkles className="w-3 h-3 mr-1" />
                Powered by AI
              </Badge>
              
              <h1 className="text-5xl lg:text-6xl font-bold mb-6 leading-tight">
                Scopri i Tuoi{' '}
                <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 bg-clip-text text-transparent animate-gradient">
                  Competitor
                </span>
                <br />in 60 Secondi
              </h1>
              
              <p className="text-xl text-slate-400 mb-8 leading-relaxed">
                Non perdere più giorni a cercare manualmente i competitor. 
                La nostra <span className="text-cyan-400 font-semibold">intelligenza artificiale</span> analizza 
                il web e trova i tuoi concorrenti automaticamente.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-12">
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={handleCTA}
                  className="shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 transition-all"
                >
                  Inizia Ora - Accedi
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button 
                  variant="secondary" 
                  size="lg"
                  onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  <Eye className="w-5 h-5 mr-2" />
                  Come Funziona
                </Button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6">
                {[
                  { value: '5min', label: 'Analisi completa' },
                  { value: '100+', label: 'Siti simultanei' },
                  { value: '95%', label: 'Accuratezza AI' }
                ].map((stat, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + i * 0.1 }}
                  >
                    <div className="text-3xl font-bold text-cyan-400">{stat.value}</div>
                    <div className="text-sm text-slate-500">{stat.label}</div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Right: Mockup */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              {/* Floating Card Mockup */}
              <div className="relative">
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-cyan-400/20 blur-3xl" />
                
                {/* Main Card */}
                <Card className="relative border-slate-700/50 shadow-2xl backdrop-blur-sm bg-slate-800/90">
                  <CardContent padding="lg">
                    <div className="space-y-4">
                      {/* Header */}
                      <div className="flex items-center justify-between pb-4 border-b border-slate-700">
                        <h3 className="text-lg font-semibold">Potenziali Competitor</h3>
                        <Badge className="bg-green-500/10 text-green-400 border-green-500/20">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          Completato
                        </Badge>
                      </div>

                      {/* Results Preview */}
                      {[
                        { 
                          title: 'Analisi Keywords', 
                          description: 'Estrazione automatica keywords dal tuo sito',
                          icon: Search,
                          color: 'from-blue-500 to-cyan-400'
                        },
                        { 
                          title: 'Match Semantico AI', 
                          description: 'Confronto intelligente con competitor',
                          icon: Brain,
                          color: 'from-cyan-400 to-teal-400'
                        },
                        { 
                          title: 'Report Excel/PDF', 
                          description: 'Esportazione professionale con score',
                          icon: FileSpreadsheet,
                          color: 'from-teal-400 to-green-400'
                        }
                      ].map((item, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.5 + i * 0.1 }}
                          className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg border border-slate-700/50"
                        >
                          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center flex-shrink-0`}>
                            <item.icon className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="text-sm font-medium text-slate-200">{item.title}</div>
                            <div className="text-xs text-slate-500">{item.description}</div>
                          </div>
                        </motion.div>
                      ))}

                      {/* Action Button */}
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1.2 }}
                      >
                        <Button variant="primary" size="sm" className="w-full">
                          <Download className="w-4 h-4 mr-2" />
                          Scarica Report Excel
                        </Button>
                      </motion.div>
                    </div>
                  </CardContent>
                </Card>

                {/* Floating Elements */}
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="absolute -top-6 -right-6 w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/30"
                >
                  <Brain className="w-8 h-8 text-white" />
                </motion.div>

                <motion.div
                  animate={{ y: [0, 10, 0] }}
                  transition={{ duration: 2.5, repeat: Infinity }}
                  className="absolute -bottom-4 -left-4 w-14 h-14 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-xl flex items-center justify-center shadow-xl shadow-cyan-500/30"
                >
                  <Database className="w-7 h-7 text-white" />
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">
              Stanco di Perdere Tempo?
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              L'analisi competitor manuale è lenta, incompleta e costosa. 
              Ecco perché abbiamo creato una soluzione automatizzata.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Prima: Pain Points */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <Card className="h-full border-red-900/30 bg-red-950/20">
                <CardContent padding="lg">
                  <h3 className="text-2xl font-bold mb-6 text-red-400">❌ Metodo Tradizionale</h3>
                  <ul className="space-y-4">
                    {[
                      'Ore perse su Google a cercare manualmente',
                      'Analisi incomplete e superficiali',
                      'Impossibile scalare oltre 10-20 siti',
                      'Dati non strutturati e difficili da analizzare',
                      'Costi elevati di consulenti esterni'
                    ].map((item, i) => (
                      <li key={i} className="flex items-start gap-3 text-slate-300">
                        <div className="w-6 h-6 rounded-full bg-red-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-red-400 text-lg">✕</span>
                        </div>
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </motion.div>

            {/* Dopo: Soluzione */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <Card className="h-full border-green-900/30 bg-green-950/20">
                <CardContent padding="lg">
                  <h3 className="text-2xl font-bold mb-6 text-green-400">✓ Con Smart Competitor</h3>
                  <ul className="space-y-4">
                    {[
                      '100 siti analizzati in 5 minuti',
                      'AI trova keywords e semantica nascosta',
                      'Report Excel professionali automatici',
                      'Score di match 0-100% per ogni competitor',
                      'Costo fisso mensile, analisi illimitate'
                    ].map((item, i) => (
                      <li key={i} className="flex items-start gap-3 text-slate-300">
                        <CheckCircle2 className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">
              Come Funziona in 3 Step
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Processo semplificato per risultati professionali in pochi minuti
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                step: '01',
                title: 'Analisi del Tuo Business',
                description: 'Inserisci il tuo sito web e personalizza il contesto: aggiungi keywords specifiche, descrizione aziendale e settore. L\'AI apprende il tuo posizionamento di mercato.',
                color: 'from-blue-500 to-cyan-400'
              },
              {
                icon: Brain,
                step: '02',
                title: 'Analisi Competitor in Real-Time',
                description: 'Carica un file Excel con centinaia di URL. L\'AI analizza ogni sito istantaneamente, confronta keywords e semantica, calcola il match score in tempo reale con aggiornamenti live.',
                color: 'from-cyan-400 to-teal-400'
              },
              {
                icon: FileSpreadsheet,
                step: '03',
                title: 'Export Report Professionale',
                description: 'Scarica report completo in Excel o PDF con score dettagliato, keywords matchate, classificazione settore e raccomandazioni strategiche pronte per presentazioni.',
                color: 'from-teal-400 to-green-400'
              }
            ].map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
              >
                <Card className="h-full border-slate-700/50 hover:border-slate-600 transition-all hover:shadow-xl hover:shadow-blue-500/10 group">
                  <CardContent padding="lg">
                    <div className={`w-16 h-16 mb-6 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                      <step.icon className="w-8 h-8 text-white" />
                    </div>
                    <div className="text-sm font-bold text-cyan-400 mb-2">STEP {step.step}</div>
                    <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                    <p className="text-slate-400 leading-relaxed">{step.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Case Studies / Sectors */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">
              Settori di Applicazione
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Utilizzato da professionisti in diverse industry per vincere la concorrenza
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: TrendingUp,
                sector: 'Finanza & Investimenti',
                use_case: 'Analisi banche online e fintech',
                result: '45 competitor trovati in 3 minuti',
                gradient: 'from-blue-500 to-cyan-400'
              },
              {
                icon: BarChart3,
                sector: 'E-commerce',
                use_case: 'Monitoraggio marketplace e shop',
                result: '120+ siti analizzati simultaneamente',
                gradient: 'from-cyan-400 to-teal-400'
              },
              {
                icon: Users,
                sector: 'Consulting',
                use_case: 'Report per clienti B2B',
                result: 'Export Excel professionali pronti',
                gradient: 'from-teal-400 to-green-400'
              },
              {
                icon: Target,
                sector: 'SaaS & Tech',
                use_case: 'Competitive intelligence software',
                result: 'Score semantico AI 95% accurato',
                gradient: 'from-green-400 to-emerald-400'
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Card className="h-full border-slate-700/50 hover:border-slate-600 transition-all hover:shadow-xl hover:shadow-blue-500/10 group cursor-pointer">
                  <CardContent padding="lg">
                    <div className={`w-12 h-12 mb-4 rounded-xl bg-gradient-to-br ${item.gradient} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                      <item.icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-bold mb-2">{item.sector}</h3>
                    <p className="text-sm text-slate-400 mb-3">{item.use_case}</p>
                    <div className="pt-3 border-t border-slate-700">
                      <div className="flex items-center gap-2 text-xs text-cyan-400">
                        <Zap className="w-3 h-3" />
                        {item.result}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">
              Funzionalità Avanzate
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Tecnologia AI all'avanguardia per analisi competitor professionali
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Shield,
                title: 'Scraping Intelligente',
                description: '4 livelli di fallback per superare protezioni anti-bot e WAF',
                badge: 'Anti-Block'
              },
              {
                icon: Brain,
                title: 'Semantic Analysis',
                description: 'Non solo keywords: AI capisce il contesto e trova competitor nascosti',
                badge: 'AI-Powered'
              },
              {
                icon: FileSpreadsheet,
                title: 'Report Automatici',
                description: 'Export Excel stilizzati con grafici, score e raccomandazioni',
                badge: 'Professional'
              },
              {
                icon: Zap,
                title: 'Analisi Bulk',
                description: 'Carica Excel con 100+ URL, analizza tutti simultaneamente',
                badge: 'Veloce'
              },
              {
                icon: Target,
                title: 'Match Score 0-100%',
                description: 'Algoritmo ibrido keyword + semantic per scoring preciso',
                badge: 'Accurato'
              },
              {
                icon: Clock,
                title: 'Real-Time Streaming',
                description: 'Vedi il progresso in tempo reale, aggiornamenti SSE live',
                badge: 'Live'
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Card className="h-full border-slate-700/50 hover:border-slate-600 transition-all hover:shadow-xl hover:shadow-blue-500/10 group">
                  <CardContent padding="lg">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <feature.icon className="w-5 h-5 text-white" />
                      </div>
                      <Badge className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20 text-xs">
                        {feature.badge}
                      </Badge>
                    </div>
                    <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                    <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="border-slate-700/50 bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-cyan-400/10 blur-3xl" />
              
              <CardContent padding="lg">
                <div className="relative text-center">
                  <h2 className="text-4xl font-bold mb-4">
                    Pronto a Dominare il Mercato?
                  </h2>
                  <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
                    Richiedi accesso alla piattaforma e inizia ad analizzare i tuoi competitor 
                    con l'intelligenza artificiale oggi stesso.
                  </p>

                  <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                    <Button 
                      variant="primary" 
                      size="lg"
                      onClick={handleCTA}
                      className="shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 transition-all"
                    >
                      Richiedi Accesso
                      <ChevronRight className="w-5 h-5 ml-2" />
                    </Button>
                  </div>

                  <div className="flex items-center justify-center gap-8 text-sm text-slate-500">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" />
                      Setup immediato
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" />
                      Supporto dedicato
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" />
                      Dati sicuri
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800 py-12 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                <span className="text-lg font-bold">Smart Competitor Finder</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                Analisi competitor automatizzata con intelligenza artificiale. 
                Trova, analizza e batti la concorrenza in pochi minuti.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#how-it-works" className="hover:text-cyan-400 transition-colors">Come Funziona</a></li>
                <li><a href="/login" className="hover:text-cyan-400 transition-colors">Login</a></li>
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h3 className="font-semibold mb-4">Contatti</h3>
              <p className="text-sm text-slate-400 mb-2">
                Creato da{' '}
                <a 
                  href="https://www.studioinnovativo.it" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  Studio Innovativo
                </a>
              </p>
              <p className="text-xs text-slate-500">
                © 2025 Smart Competitor Finder. All rights reserved.
              </p>
            </div>
          </div>

          <div className="pt-8 border-t border-slate-800">
            <p className="text-center text-xs text-slate-500">
              Tecnologia AI per l'analisi competitor professionale
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
