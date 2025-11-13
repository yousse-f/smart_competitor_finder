'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Activity, ArrowRight, CheckCircle2, Search, FileSpreadsheet, 
  Zap, Shield, TrendingUp, Users, BarChart3, Target, Clock,
  Sparkles, ChevronRight, Download, Eye, Brain, Database, User, Settings, Globe
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
                {/* Magnifying glass solo */}
                <Search className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                Smart Competitor Finder
              </span>
            </motion.div>
            
            {/* Navigation Links */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="hidden md:flex items-center gap-3"
            >
              {/* Bottoni di navigazione rimossi - solo per utenti loggati nella sidebar */}
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
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              <Badge className="mb-6 bg-blue-500/10 text-blue-400 border-blue-500/20">
                <Sparkles className="w-3 h-3 mr-1" />
                Analisi AI Semantica
              </Badge>
              
              <h1 className="text-5xl lg:text-6xl font-bold mb-6 leading-tight">
                Trova i Veri Competitor{' '}
                <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 bg-clip-text text-transparent animate-gradient">
                  in 60 Secondi
                </span>
              </h1>
              
              <p className="text-xl text-slate-400 mb-6 leading-relaxed">
                L'AI confronta centinaia di siti e ti consegna un report professionale.
              </p>
              
              <p className="text-lg text-slate-300 mb-8">
                <span className="text-cyan-400 font-semibold">Zero lavoro manuale.</span>{' '}
                <span className="text-cyan-400 font-semibold">Zero errori.</span>{' '}
                <span className="text-cyan-400 font-semibold">Solo risultati.</span>
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-12">
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={handleCTA}
                  className="shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 transition-all"
                >
                  Inizia Subito
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button 
                  variant="secondary" 
                  size="lg"
                  onClick={() => document.getElementById('video-demo')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  <Eye className="w-5 h-5 mr-2" />
                  Guarda Demo
                </Button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6">
                {[
                  { value: '60s', label: 'Per iniziare' },
                  { value: '100+', label: 'Siti analizzati' },
                  { value: '0', label: 'Lavoro manuale' }
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
              transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
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
                          title: 'Estrazione Keywords', 
                          description: 'Identifica le parole chiave del tuo business',
                          icon: Search,
                          color: 'from-blue-500 to-cyan-400'
                        },
                        { 
                          title: 'Analisi Intelligente', 
                          description: 'AI confronta e trova competitor rilevanti',
                          icon: Brain,
                          color: 'from-cyan-400 to-teal-400'
                        },
                        { 
                          title: 'Report Pronto', 
                          description: 'Scarica Excel con score e raccomandazioni',
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
                        <Button 
                          variant="primary" 
                          size="sm" 
                          className="w-full opacity-60 cursor-not-allowed"
                          disabled
                        >
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
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  className="absolute -top-6 -right-6 w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/30"
                >
                  <Brain className="w-8 h-8 text-white" />
                </motion.div>

                <motion.div
                  animate={{ y: [0, 10, 0] }}
                  transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                  className="absolute -bottom-4 -left-4 w-14 h-14 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-xl flex items-center justify-center shadow-xl shadow-cyan-500/30"
                >
                  <Database className="w-7 h-7 text-white" />
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Value Proposition Section */}
      <section className="relative z-10 py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center">
            <p className="text-lg text-slate-300 leading-relaxed">
              Il primo sistema che <span className="text-cyan-400 font-semibold">identifica i veri competitor</span> del tuo business in pochi minuti, 
              confrontando centinaia di siti tramite <span className="text-cyan-400 font-semibold">analisi semantica AI</span>.
            </p>
          </div>
        </div>
      </section>

      {/* Video Demo Section */}
      <section id="video-demo" className="relative z-10 py-20 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-4">
              <h2 className="text-4xl font-bold">
                🎥 Guarda l'AI al Lavoro
              </h2>
              <Badge className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 text-yellow-400 border-yellow-500/30 text-sm px-3 py-1">
                <Sparkles className="w-3 h-3 mr-1" />
                Coming Soon
              </Badge>
            </div>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-2">
              Demo Reale - Sistema in azione step-by-step
            </p>
            <p className="text-base text-slate-500">
              Come l'AI identifica i tuoi competitor reali in pochi secondi
            </p>
          </div>

          <div className="relative">
            {/* Video Placeholder - Modern Design */}
            <div className="relative aspect-video rounded-2xl overflow-hidden border border-slate-700/30 shadow-2xl backdrop-blur-sm">
              {/* Modern Gradient Background */}
              <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-950/30 to-slate-900">
                {/* Animated Grid Pattern */}
                <motion.div
                  animate={{
                    opacity: [0.03, 0.08, 0.03],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="absolute inset-0"
                  style={{
                    backgroundImage: `linear-gradient(rgba(56, 189, 248, 0.1) 1px, transparent 1px),
                                     linear-gradient(90deg, rgba(56, 189, 248, 0.1) 1px, transparent 1px)`,
                    backgroundSize: '50px 50px'
                  }}
                />
                
                {/* Smooth Gradient Orbs */}
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.15, 0.25, 0.15],
                  }}
                  transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full blur-3xl"
                />
                <motion.div
                  animate={{
                    scale: [1, 1.3, 1],
                    opacity: [0.15, 0.25, 0.15],
                  }}
                  transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 2
                  }}
                  className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-tl from-cyan-500/20 to-transparent rounded-full blur-3xl"
                />
              </div>
              
              {/* Content Container */}
              <div className="relative w-full h-full flex items-center justify-center backdrop-blur-[1px]">
                {/* Floating Process Cards */}
                <div className="absolute inset-0 flex items-center justify-around px-12 opacity-20">
                  <motion.div
                    animate={{
                      y: [0, -15, 0],
                      opacity: [0.2, 0.4, 0.2]
                    }}
                    transition={{
                      duration: 5,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                    className="flex flex-col items-center gap-2"
                  >
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg">
                      <Search className="w-8 h-8 text-white" />
                    </div>
                    <div className="text-xs text-slate-400 font-medium">Analizza</div>
                  </motion.div>
                  
                  <motion.div
                    animate={{
                      y: [0, -15, 0],
                      opacity: [0.2, 0.4, 0.2]
                    }}
                    transition={{
                      duration: 5,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 1
                    }}
                    className="flex flex-col items-center gap-2"
                  >
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center shadow-lg">
                      <Brain className="w-8 h-8 text-white" />
                    </div>
                    <div className="text-xs text-slate-400 font-medium">Confronta</div>
                  </motion.div>
                  
                  <motion.div
                    animate={{
                      y: [0, -15, 0],
                      opacity: [0.2, 0.4, 0.2]
                    }}
                    transition={{
                      duration: 5,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 2
                    }}
                    className="flex flex-col items-center gap-2"
                  >
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-400 to-green-400 flex items-center justify-center shadow-lg">
                      <FileSpreadsheet className="w-8 h-8 text-white" />
                    </div>
                    <div className="text-xs text-slate-400 font-medium">Genera Report</div>
                  </motion.div>
                </div>

                {/* Center Content */}
                <div className="relative z-10 text-center space-y-6 px-8">
                  {/* Modern Play Button */}
                  <motion.div
                    animate={{
                      scale: [1, 1.05, 1],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                    className="w-28 h-28 mx-auto bg-gradient-to-br from-blue-500 via-cyan-400 to-blue-500 rounded-full flex items-center justify-center shadow-2xl shadow-blue-500/50 relative group cursor-pointer"
                  >
                    {/* Pulse Ring */}
                    <motion.div
                      animate={{
                        scale: [1, 1.4],
                        opacity: [0.5, 0],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeOut"
                      }}
                      className="absolute inset-0 rounded-full bg-cyan-400/30"
                    />
                    <svg className="w-14 h-14 text-white relative z-10" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </motion.div>
                  
                  <div>
                    <div className="text-3xl font-bold text-white mb-3">Demo Reale</div>
                    <div className="text-lg text-slate-300 mb-4">Sistema in azione step-by-step</div>
                    <Badge className="bg-gradient-to-r from-yellow-500/30 to-orange-500/30 text-yellow-300 border-yellow-500/40 backdrop-blur-sm px-4 py-1.5">
                      <Sparkles className="w-4 h-4 mr-2" />
                      In Preparazione
                    </Badge>
                  </div>
                  
                  <div className="pt-2">
                    <Badge className="bg-cyan-500/20 text-cyan-300 border-cyan-500/30 backdrop-blur-sm">
                      <Clock className="w-4 h-4 mr-2" />
                      Durata: 60 secondi
                    </Badge>
                  </div>
                </div>
              </div>
            </div>

            {/* Trust Elements Below Video */}
            <div className="grid grid-cols-4 gap-4 mt-8">
              {[
                { icon: CheckCircle2, text: 'Nessun setup' },
                { icon: Clock, text: '60 secondi' },
                { icon: Zap, text: 'Risultati immediati' },
                { icon: Shield, text: 'Dati sicuri' }
              ].map((item, i) => (
                <div
                  key={i}
                  className="flex flex-col items-center gap-2 text-center"
                >
                  <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                    <item.icon className="w-5 h-5 text-cyan-400" />
                  </div>
                  <span className="text-sm text-slate-400">{item.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Immediate Benefits Section */}
      <section className="relative z-10 py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <Card className="border-slate-700/50 bg-slate-800/50">
            <CardContent padding="lg">
              <h3 className="text-2xl font-bold mb-6 text-center">Benefici Immediati</h3>
              <div className="grid md:grid-cols-3 gap-6">
                {[
                  {
                    icon: Clock,
                    title: 'Risparmi giorni di analisi manuale',
                    color: 'from-blue-500 to-cyan-400'
                  },
                  {
                    icon: FileSpreadsheet,
                    title: 'Report pronti per clienti e investitori',
                    color: 'from-cyan-400 to-teal-400'
                  },
                  {
                    icon: Target,
                    title: 'Identificazione dei veri competitor (non quelli "simili")',
                    color: 'from-teal-400 to-green-400'
                  }
                ].map((benefit, i) => (
                  <div key={i} className="flex flex-col items-center text-center">
                    <div className={`w-14 h-14 mb-4 rounded-xl bg-gradient-to-br ${benefit.color} flex items-center justify-center shadow-lg`}>
                      <benefit.icon className="w-7 h-7 text-white" />
                    </div>
                    <p className="text-slate-300 leading-relaxed">{benefit.title}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Problem Section */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Il Problema che Risolviamo
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Analizzare competitor manualmente costa tempo e denaro. Noi lo facciamo in automatico.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Prima: Pain Points */}
            <div>
              <Card className="h-full border-red-900/30 bg-red-950/20">
                <CardContent padding="lg">
                  <h3 className="text-2xl font-bold mb-6 text-red-400">❌ Senza il Nostro Sistema</h3>
                  <ul className="space-y-4">
                    {[
                      'Giorni persi su Google senza risultati chiari',
                      'Dati sparsi, impossibili da confrontare',
                      'Massimo 10-20 siti analizzabili',
                      'Costi alti per consulenti esterni',
                      'Aggiornamenti manuali continui'
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
            </div>

            {/* Dopo: Soluzione */}
            <div>
              <Card className="h-full border-green-900/30 bg-green-950/20">
                <CardContent padding="lg">
                  <h3 className="text-2xl font-bold mb-6 text-green-400">✓ Con Smart Competitor Finder</h3>
                  <ul className="space-y-4">
                    {[
                      'Analisi illimitata: centinaia di siti in pochi minuti',
                      'Report Excel pronti per presentazioni',
                      'Score preciso per ogni competitor (0-100%)',
                      'AI trova opportunità nascoste',
                      'Costo fisso, nessuna sorpresa'
                    ].map((item, i) => (
                      <li key={i} className="flex items-start gap-3 text-slate-300">
                        <CheckCircle2 className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Semplice Come 1-2-3
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Tre passaggi per ottenere il tuo report competitor professionale
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                step: '01',
                title: 'Inserisci il Tuo Sito',
                description: 'Incolla l\'URL del tuo business. L\'AI estrae automaticamente keywords e contesto di mercato in pochi secondi.',
                color: 'from-blue-500 to-cyan-400'
              },
              {
                icon: Brain,
                step: '02',
                title: 'Carica la Lista Competitor',
                description: 'Upload di un file Excel con gli URL da analizzare. Il sistema confronta tutto in tempo reale e calcola i match score.',
                color: 'from-cyan-400 to-teal-400'
              },
              {
                icon: FileSpreadsheet,
                step: '03',
                title: 'Scarica il Report',
                description: 'Ottieni un file Excel completo con score, classifiche e insights strategici pronti per decisioni immediate.',
                color: 'from-teal-400 to-green-400'
              }
            ].map((step, i) => (
              <div key={i}>
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
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Case Studies / Sectors */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Chi Lo Usa Già
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Professionisti in diversi settori si affidano a noi per battere la concorrenza
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: TrendingUp,
                sector: 'Finanza',
                use_case: 'Banche e fintech',
                result: '45 competitor mappati in minuti',
                gradient: 'from-blue-500 to-cyan-400'
              },
              {
                icon: BarChart3,
                sector: 'E-commerce',
                use_case: 'Marketplace e shop online',
                result: '120+ siti analizzati insieme',
                gradient: 'from-cyan-400 to-teal-400'
              },
              {
                icon: Users,
                sector: 'Consulting',
                use_case: 'Report per clienti B2B',
                result: 'Export pronti per presentazioni',
                gradient: 'from-teal-400 to-green-400'
              },
              {
                icon: Target,
                sector: 'SaaS & Tech',
                use_case: 'Intelligence software',
                result: 'Precisione AI al 95%',
                gradient: 'from-green-400 to-emerald-400'
              }
            ].map((item, i) => (
              <div key={i}>
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
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              La Tecnologia che Fa il Lavoro al Posto Tuo
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Niente fuffa: solo risultati misurabili
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {[
              {
                icon: Search,
                title: 'Capisce Chi Sei',
                description: 'Analizza il tuo business e identifica il tuo posizionamento',
                badge: 'Intelligente'
              },
              {
                icon: Brain,
                title: 'Capisce Cosa Fanno gli Altri',
                description: 'Legge e comprende centinaia di siti in automatico',
                badge: 'Semantico'
              },
              {
                icon: Zap,
                title: 'Confronta Tutto in Real-Time',
                description: 'Calcola match score e rilevanza istantaneamente',
                badge: 'Veloce'
              },
              {
                icon: Target,
                title: 'Ti Dice Chi è Competitor Vero',
                description: 'Non "siti simili", ma veri competitor di mercato',
                badge: 'Preciso'
              }
            ].map((feature, i) => (
              <div key={i}>
                <Card className="h-full border-slate-700/50 hover:border-slate-600 transition-all hover:shadow-xl hover:shadow-blue-500/10 group">
                  <CardContent padding="lg">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
                        <feature.icon className="w-6 h-6 text-white" />
                      </div>
                      <Badge className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20 text-xs">
                        {feature.badge}
                      </Badge>
                    </div>
                    <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                    <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Target Audience Section */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              Per Chi è Pensato?
            </h2>
            <p className="text-xl text-slate-400">
              Professionisti che gestiscono analisi competitive di mercato
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: TrendingUp, label: 'Consulenti Finanziari', description: 'Analisi settoriali e benchmarking' },
              { icon: BarChart3, label: 'Business Analyst', description: 'Intelligence competitiva' },
              { icon: Users, label: 'Studi di Consulenza', description: 'Report per clienti corporate' },
              { icon: Target, label: 'Advisor M&A', description: 'Due diligence di mercato' },
              { icon: Database, label: 'Agenzie Dati', description: 'Raccolta e benchmarking dati' },
              { icon: Shield, label: 'Market Intelligence', description: 'Valutazione nuovi mercati' }
            ].map((item, i) => (
              <div key={i}>
                <Card className="h-full border-slate-700/50 hover:border-cyan-500/30 transition-all group">
                  <CardContent padding="md">
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform">
                        <item.icon className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-200 mb-1">{item.label}</h3>
                        <p className="text-sm text-slate-400">{item.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div>
            <Card className="border-slate-700/50 bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-cyan-400/10 blur-3xl" />
              
              <CardContent padding="lg">
                <div className="relative text-center">
                  <h2 className="text-4xl font-bold mb-4">
                    Pronto a Iniziare?
                  </h2>
                  <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
                    Accedi ora e scopri chi sono i tuoi veri competitor. 
                    Primo report pronto in meno di 5 minuti.
                  </p>

                  <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                    <Button 
                      variant="primary" 
                      size="lg"
                      onClick={handleCTA}
                      className="shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 transition-all"
                    >
                      Accedi Subito
                      <ChevronRight className="w-5 h-5 ml-2" />
                    </Button>
                  </div>

                  <div className="flex items-center justify-center gap-8 text-sm text-slate-500">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" />
                      Nessun setup
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" />
                      Risultati immediati
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" />
                      Supporto incluso
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800 py-12 px-4 sm:px-6 lg:px-8 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center relative">
                  {/* Globe */}
                  <svg viewBox="0 0 24 24" className="w-5 h-5 text-white absolute" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="9" strokeWidth="1.8"/>
                    <ellipse cx="12" cy="12" rx="9" ry="4" strokeWidth="1.2"/>
                    <path d="M 12 3 Q 15 12 12 21" strokeWidth="1.2"/>
                    <path d="M 12 3 Q 9 12 12 21" strokeWidth="1.2"/>
                  </svg>
                  {/* Magnifying glass */}
                  <Search className="w-3 h-3 text-white absolute" style={{ transform: 'translate(50%, 50%)' }} />
                </div>
                <span className="text-lg font-bold">Smart Competitor Finder</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                Analisi competitor automatizzata con AI. 
                Trova, confronta e batti la concorrenza.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="font-semibold mb-4">Link Rapidi</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#video-demo" className="hover:text-cyan-400 transition-colors">Guarda Demo</a></li>
                <li><a href="#how-it-works" className="hover:text-cyan-400 transition-colors">Come Funziona</a></li>
                <li><a href="/login" className="hover:text-cyan-400 transition-colors">Accedi</a></li>
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
              Analisi competitor professionale powered by AI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
