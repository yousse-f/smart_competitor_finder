'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Mail, 
  Building2, 
  Shield, 
  CreditCard, 
  Settings,
  Camera,
  Save,
  Eye,
  EyeOff,
  Crown,
  Zap,
  TrendingUp,
  Calendar,
  Check,
  Star,
  Lock,
  ShieldCheck,
  FileText,
  Users,
  BarChart3,
  Search,
  Database,
  Briefcase
} from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';

interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  company: string;
  position: string;
  avatar: string;
  registrationDate: string;
  licenseType: string;
  licenseValidUntil: string;
  licenseUsers: number;
  analysesThisMonth: number;
  totalReports: number;
  totalCompetitors: number;
  totalKeywords: number;
  lastAccess: string;
}

interface PlanFeature {
  name: string;
  included: boolean;
}

interface Plan {
  id: 'free' | 'pro' | 'enterprise';
  name: string;
  price: string;
  period: string;
  description: string;
  features: PlanFeature[];
  popular?: boolean;
}

export default function AccountPage() {
  const [isMounted, setIsMounted] = useState(false);
  const [profile, setProfile] = useState<UserProfile>({
    firstName: 'Federico',
    lastName: '',
    email: 'federico@example.com',
    company: 'Studio Innovativo',
    position: 'Consulente',
    avatar: '',
    registrationDate: '2024-01-15',
    licenseType: 'Professional License – Consultant Access',
    licenseValidUntil: '2026-11-14',
    licenseUsers: 1,
    analysesThisMonth: 8,
    totalReports: 12,
    totalCompetitors: 1247,
    totalKeywords: 3891,
    lastAccess: 'Oggi'
  });

  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [show2FASetup, setShow2FASetup] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  // Evita hydration mismatch - monta solo lato client
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const plans: Plan[] = [
    {
      id: 'free',
      name: 'Free',
      price: '€0',
      period: 'per sempre',
      description: 'Perfetto per iniziare',
      features: [
        { name: '10 analisi al mese', included: true },
        { name: '50 competitors per analisi', included: true },
        { name: 'Export Excel/PDF', included: true },
        { name: 'Keywords AI extraction', included: true },
        { name: 'Support email', included: false },
        { name: 'API access', included: false },
        { name: 'Team collaboration', included: false }
      ]
    },
    {
      id: 'pro',
      name: 'Pro',
      price: '€29',
      period: 'al mese',
      description: 'Per professionisti e PMI',
      popular: true,
      features: [
        { name: '100 analisi al mese', included: true },
        { name: '500 competitors per analisi', included: true },
        { name: 'Export Excel/PDF', included: true },
        { name: 'Keywords AI extraction', included: true },
        { name: 'Support email prioritario', included: true },
        { name: 'API access', included: true },
        { name: 'Team collaboration (5 utenti)', included: true }
      ]
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: '€99',
      period: 'al mese',
      description: 'Per grandi aziende',
      features: [
        { name: 'Analisi illimitate', included: true },
        { name: 'Competitors illimitati', included: true },
        { name: 'Export Excel/PDF', included: true },
        { name: 'Keywords AI extraction', included: true },
        { name: 'Support dedicato 24/7', included: true },
        { name: 'API access completo', included: true },
        { name: 'Team collaboration illimitata', included: true }
      ]
    }
  ];

  // Carica statistiche da localStorage
  useEffect(() => {
    try {
      const savedReports = localStorage.getItem('competitorReports');
      if (savedReports) {
        const reports = JSON.parse(savedReports);
        const thisMonth = new Date().getMonth();
        const thisYear = new Date().getFullYear();
        
        const analysesThisMonth = reports.filter((report: any) => {
          const reportDate = new Date(report.date);
          return reportDate.getMonth() === thisMonth && reportDate.getFullYear() === thisYear;
        }).length;

        setProfile(prev => ({
          ...prev,
          analysesThisMonth,
          totalReports: reports.length
        }));
      }
    } catch (error) {
      console.error('Error loading account stats:', error);
    }
  }, []);

  const handleProfileUpdate = (field: keyof UserProfile, value: string) => {
    setProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveProfile = () => {
    // Qui si salverebbero i dati su server/database
    console.log('Profilo salvato:', profile);
    alert('Profilo aggiornato con successo!');
  };

  const handlePasswordChange = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('Le password non coincidono');
      return;
    }
    if (passwordData.newPassword.length < 8) {
      alert('La password deve essere di almeno 8 caratteri');
      return;
    }
    
    // Qui si cambierebbe la password
    console.log('Password cambiata');
    alert('Password cambiata con successo!');
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    setShowPasswordChange(false);
  };

  const handle2FASetup = () => {
    // Qui si attiverebbe la 2FA
    console.log('2FA attivata');
    alert('Autenticazione a due fattori attivata con successo!');
    setShow2FASetup(false);
  };

  const licenseFeatures = [
    { icon: Check, text: 'Analisi illimitate' },
    { icon: Check, text: 'Bulk analysis (fino a 1000 URL)' },
    { icon: Check, text: 'Report Excel & PDF professionali' },
    { icon: Check, text: 'AI Semantica per match score e classificazione' },
    { icon: Check, text: 'Storage sicuro dei report' },
    { icon: Check, text: 'Aggiornamenti inclusi' },
    { icon: Check, text: 'Supporto dedicato via email' }
  ];

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Account & Impostazioni
          </h1>
          <p className="text-slate-400">
            Gestisci il tuo profilo, la sicurezza e la tua licenza professionale.
          </p>
        </motion.div>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* 1. PROFILO UTENTE */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="card p-6"
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                  {profile.firstName[0]}{profile.lastName[0]}
                </div>
                <button className="absolute -bottom-1 -right-1 w-7 h-7 bg-blue-500 rounded-full flex items-center justify-center text-white hover:bg-blue-600 transition-colors shadow-lg">
                  <Camera className="w-4 h-4" />
                </button>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-slate-100">
                  {profile.firstName} {profile.lastName}
                </h2>
                <p className="text-slate-400">{profile.position}</p>
                <p className="text-sm text-slate-500">
                  Membro dal {new Date(profile.registrationDate).toLocaleDateString('it-IT')}
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label flex items-center gap-2">
                    <User className="w-4 h-4 text-slate-400" />
                    Nome
                  </label>
                  <Input
                    value={profile.firstName}
                    onChange={(e) => handleProfileUpdate('firstName', e.target.value)}
                    placeholder="Nome"
                  />
                </div>
                <div>
                  <label className="label flex items-center gap-2">
                    <User className="w-4 h-4 text-slate-400" />
                    Cognome
                  </label>
                  <Input
                    value={profile.lastName}
                    onChange={(e) => handleProfileUpdate('lastName', e.target.value)}
                    placeholder="Cognome"
                  />
                </div>
              </div>

              <div>
                <label className="label flex items-center gap-2">
                  <Mail className="w-4 h-4 text-slate-400" />
                  Email
                </label>
                <Input
                  type="email"
                  value={profile.email}
                  onChange={(e) => handleProfileUpdate('email', e.target.value)}
                  placeholder="Email"
                />
              </div>

              <div>
                <label className="label flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-slate-400" />
                  Azienda
                </label>
                <Input
                  value={profile.company}
                  onChange={(e) => handleProfileUpdate('company', e.target.value)}
                  placeholder="Nome azienda"
                />
              </div>

              <div>
                <label className="label flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-slate-400" />
                  Ruolo
                </label>
                <Input
                  value={profile.position}
                  onChange={(e) => handleProfileUpdate('position', e.target.value)}
                  placeholder="Ruolo lavorativo"
                />
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <Button onClick={handleSaveProfile} variant="primary">
                <Save className="w-4 h-4 mr-2" />
                Salva Modifiche
              </Button>
            </div>

            {/* Nota microcopy */}
            <div className="mt-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
              <p className="text-xs text-slate-400">
                <span className="text-slate-300 font-medium">ℹ️ Nota:</span> I dati del tuo profilo verranno usati nei report generati dalla piattaforma.
              </p>
            </div>
          </motion.div>

          {/* 2. SICUREZZA ACCOUNT */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="card p-6"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-100">Sicurezza</h3>
                <p className="text-sm text-slate-400">Proteggi il tuo account e mantieni al sicuro i tuoi dati.</p>
              </div>
            </div>

            <div className="space-y-4">
              {/* Password */}
              <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <Lock className="w-5 h-5 text-slate-400" />
                    <div>
                      <p className="font-medium text-slate-100">Password</p>
                      <p className="text-sm text-slate-400">Ultima modifica: Mai</p>
                    </div>
                  </div>
                  <Button
                    onClick={() => setShowPasswordChange(!showPasswordChange)}
                    variant="secondary"
                    size="sm"
                  >
                    {showPasswordChange ? 'Annulla' : 'Cambia Password'}
                  </Button>
                </div>

                {showPasswordChange && (
                  <div className="mt-4 space-y-3 pt-4 border-t border-slate-700">
                    <div>
                      <label className="label text-xs">Password Attuale</label>
                      <div className="relative">
                        <Input
                          type={showPasswords.current ? 'text' : 'password'}
                          value={passwordData.currentPassword}
                          onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                          placeholder="Password attuale"
                        />
                        <button
                          onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                        >
                          {showPasswords.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="label text-xs">Nuova Password</label>
                      <div className="relative">
                        <Input
                          type={showPasswords.new ? 'text' : 'password'}
                          value={passwordData.newPassword}
                          onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                          placeholder="Nuova password (min. 8 caratteri)"
                        />
                        <button
                          onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                        >
                          {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="label text-xs">Conferma Password</label>
                      <div className="relative">
                        <Input
                          type={showPasswords.confirm ? 'text' : 'password'}
                          value={passwordData.confirmPassword}
                          onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                          placeholder="Conferma nuova password"
                        />
                        <button
                          onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                        >
                          {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    <Button onClick={handlePasswordChange} variant="primary" size="sm" className="w-full">
                      Salva Password
                    </Button>
                  </div>
                )}
              </div>

              {/* 2FA */}
              <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <ShieldCheck className="w-5 h-5 text-slate-400" />
                    <div>
                      <p className="font-medium text-slate-100">Autenticazione a due fattori</p>
                      <p className="text-sm text-slate-400">Non attiva</p>
                    </div>
                  </div>
                  <Button
                    onClick={() => setShow2FASetup(!show2FASetup)}
                    variant="secondary"
                    size="sm"
                  >
                    {show2FASetup ? 'Annulla' : 'Attiva 2FA'}
                  </Button>
                </div>

                {show2FASetup && (
                  <div className="mt-4 pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-3">
                      L'autenticazione a due fattori aggiunge un ulteriore livello di sicurezza al tuo account.
                    </p>
                    <Button onClick={handle2FASetup} variant="primary" size="sm" className="w-full">
                      Conferma Attivazione 2FA
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* 3. LICENZA PROFESSIONALE */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2 card p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-blue-500/20"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg">
                <Crown className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-slate-100">Licenza Attuale</h3>
                <Badge className="mt-1 bg-blue-500/10 text-blue-400 border-blue-500/30">
                  <Star className="w-3 h-3 mr-1" />
                  Professionale
                </Badge>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-6">
              <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <FileText className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-slate-100">{profile.licenseType}</p>
                <p className="text-sm text-slate-400 mt-1">Tipo Licenza</p>
              </div>
              <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <Calendar className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-slate-100">
                  {new Date(profile.licenseValidUntil).toLocaleDateString('it-IT')}
                </p>
                <p className="text-sm text-slate-400 mt-1">Valida fino al</p>
              </div>
              <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <Users className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-slate-100">{profile.licenseUsers}</p>
                <p className="text-sm text-slate-400 mt-1">Utenti inclusi</p>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="text-lg font-semibold text-slate-100 mb-4">Cosa include la tua licenza</h4>
              <div className="grid md:grid-cols-2 gap-3">
                {licenseFeatures.map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/30 rounded-lg">
                    <div className="w-5 h-5 rounded-full bg-green-500/10 flex items-center justify-center flex-shrink-0">
                      <Check className="w-3 h-3 text-green-400" />
                    </div>
                    <span className="text-sm text-slate-300">{feature.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-700 pt-6">
              <h4 className="text-lg font-semibold text-slate-100 mb-4">Gestione Licenza</h4>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary" size="md">
                  <Settings className="w-4 h-4 mr-2" />
                  Gestisci Licenza
                </Button>
                <Button variant="secondary" size="md">
                  <Users className="w-4 h-4 mr-2" />
                  Aggiungi Utenti
                  <span className="ml-2 text-xs text-slate-400">(per team e agenzie)</span>
                </Button>
                <Button variant="secondary" size="md">
                  <Crown className="w-4 h-4 mr-2" />
                  Richiedi Upgrade
                </Button>
              </div>
              
              <div className="mt-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <p className="text-xs text-slate-400">
                  <span className="text-slate-300 font-medium">ℹ️ Nota:</span> Le licenze professionali sono personalizzate in base al volume di analisi e al numero di utenti.
                </p>
              </div>
            </div>
          </motion.div>

          {/* 4. STATISTICHE UTENTE */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-2 card p-6"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-400 flex items-center justify-center shadow-lg">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-slate-100">Attività del tuo account</h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <FileText className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-slate-100">{profile.totalReports}</p>
                <p className="text-sm text-slate-400 mt-1">Report totali</p>
              </div>
              <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <TrendingUp className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-slate-100">
                  {isMounted ? profile.totalCompetitors.toLocaleString('it-IT') : profile.totalCompetitors}
                </p>
                <p className="text-sm text-slate-400 mt-1">Competitor analizzati</p>
              </div>
              <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <Search className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-slate-100">
                  {isMounted ? profile.totalKeywords.toLocaleString('it-IT') : profile.totalKeywords}
                </p>
                <p className="text-sm text-slate-400 mt-1">Keywords estratte</p>
              </div>
              <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <Calendar className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-slate-100">{profile.lastAccess}</p>
                <p className="text-sm text-slate-400 mt-1">Ultimo accesso</p>
              </div>
            </div>
          </motion.div>

        </div>
        
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
