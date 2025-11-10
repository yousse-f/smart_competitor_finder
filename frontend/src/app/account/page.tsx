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
  Star
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
  plan: 'free' | 'pro' | 'enterprise';
  creditsUsed: number;
  creditsLimit: number;
  analysesThisMonth: number;
  analysesLimit: number;
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
  const [profile, setProfile] = useState<UserProfile>({
    firstName: 'Mario',
    lastName: 'Rossi',
    email: 'mario.rossi@example.com',
    company: 'Studio Innovativo',
    position: 'Marketing Manager',
    avatar: '',
    registrationDate: '2024-01-15',
    plan: 'free',
    creditsUsed: 15,
    creditsLimit: 50,
    analysesThisMonth: 8,
    analysesLimit: 10
  });

  const [showPasswordChange, setShowPasswordChange] = useState(false);
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
          analysesThisMonth
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

  const getPlanBadge = (planId: string) => {
    switch (planId) {
      case 'free': return 'badge-secondary';
      case 'pro': return 'badge-primary';
      case 'enterprise': return 'badge-success';
      default: return 'badge-secondary';
    }
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'free': return User;
      case 'pro': return Zap;
      case 'enterprise': return Crown;
      default: return User;
    }
  };

  const currentPlan = plans.find(p => p.id === profile.plan);

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
              Account & Impostazioni
            </h1>
            <p className="text-slate-400">
              Gestisci il tuo profilo, piano e preferenze
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={getPlanBadge(profile.plan)}>
              {currentPlan?.name}
            </Badge>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profilo Utente */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2 space-y-6"
          >
            {/* Informazioni Personali */}
            <div className="card p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="relative">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                    {profile.firstName[0]}{profile.lastName[0]}
                  </div>
                  <button className="absolute -bottom-1 -right-1 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center text-white text-xs hover:bg-primary-600 transition-colors">
                    <Camera className="w-3 h-3" />
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Nome</label>
                  <Input
                    value={profile.firstName}
                    onChange={(e) => handleProfileUpdate('firstName', e.target.value)}
                    placeholder="Nome"
                  />
                </div>
                <div>
                  <label className="label">Cognome</label>
                  <Input
                    value={profile.lastName}
                    onChange={(e) => handleProfileUpdate('lastName', e.target.value)}
                    placeholder="Cognome"
                  />
                </div>
                <div>
                  <label className="label">Email</label>
                  <Input
                    type="email"
                    value={profile.email}
                    onChange={(e) => handleProfileUpdate('email', e.target.value)}
                    placeholder="Email"
                  />
                </div>
                <div>
                  <label className="label">Posizione</label>
                  <Input
                    value={profile.position}
                    onChange={(e) => handleProfileUpdate('position', e.target.value)}
                    placeholder="Posizione lavorativa"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="label">Azienda</label>
                  <Input
                    value={profile.company}
                    onChange={(e) => handleProfileUpdate('company', e.target.value)}
                    placeholder="Nome azienda"
                  />
                </div>
              </div>

              <div className="flex justify-end mt-6">
                <Button onClick={handleSaveProfile} variant="primary">
                  <Save className="w-4 h-4 mr-2" />
                  Salva Modifiche
                </Button>
              </div>
            </div>

            {/* Sicurezza */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-6">
                <Shield className="w-6 h-6 text-primary-400" />
                <h3 className="text-lg font-semibold text-slate-100">Sicurezza</h3>
              </div>

              {!showPasswordChange ? (
                <div className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
                  <div>
                    <p className="font-medium text-slate-100">Password</p>
                    <p className="text-sm text-slate-400">Ultima modifica: Mai</p>
                  </div>
                  <Button
                    onClick={() => setShowPasswordChange(true)}
                    variant="secondary"
                    size="sm"
                  >
                    Cambia Password
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="label">Password Attuale</label>
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
                    <label className="label">Nuova Password</label>
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
                    <label className="label">Conferma Password</label>
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
                  <div className="flex gap-3">
                    <Button onClick={handlePasswordChange} variant="primary">
                      Salva Password
                    </Button>
                    <Button onClick={() => setShowPasswordChange(false)} variant="ghost">
                      Annulla
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>

          {/* Sidebar - Piano e Statistiche */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            {/* Piano Attuale */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <CreditCard className="w-6 h-6 text-primary-400" />
                <h3 className="text-lg font-semibold text-slate-100">Piano Attuale</h3>
              </div>

              {currentPlan && (
                <div className="text-center mb-6">
                  <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full mx-auto mb-4">
                    {React.createElement(getPlanIcon(profile.plan), { className: "w-8 h-8 text-white" })}
                  </div>
                  <h4 className="text-xl font-bold text-slate-100">{currentPlan.name}</h4>
                  <p className="text-2xl font-bold text-primary-400 mt-1">
                    {currentPlan.price}
                    <span className="text-sm text-slate-400 font-normal">/{currentPlan.period}</span>
                  </p>
                </div>
              )}

              {/* Utilizzo */}
              <div className="space-y-4 mb-6">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-400">Analisi questo mese</span>
                    <span className="text-slate-300">{profile.analysesThisMonth}/{profile.analysesLimit}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-primary-500 to-secondary-400 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min((profile.analysesThisMonth / profile.analysesLimit) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              <Button 
                className="w-full" 
                variant={profile.plan === 'free' ? 'primary' : 'secondary'}
              >
                {profile.plan === 'free' ? (
                  <>
                    <Crown className="w-4 h-4 mr-2" />
                    Upgrade Piano
                  </>
                ) : (
                  <>
                    <Settings className="w-4 h-4 mr-2" />
                    Gestisci Piano
                  </>
                )}
              </Button>
            </div>

            {/* Statistiche Rapide */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-green-400" />
                <h3 className="text-lg font-semibold text-slate-100">Statistiche</h3>
              </div>

              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-slate-400">Report totali</span>
                  <span className="font-semibold text-slate-100">12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Competitors analizzati</span>
                  <span className="font-semibold text-slate-100">1,247</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Keywords estratte</span>
                  <span className="font-semibold text-slate-100">3,891</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Ultimo accesso</span>
                  <span className="font-semibold text-slate-100">Oggi</span>
                </div>
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