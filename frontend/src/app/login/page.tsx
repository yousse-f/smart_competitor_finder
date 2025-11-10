'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { Activity, Mail, Lock, Eye, EyeOff, AlertCircle, ExternalLink } from 'lucide-react';
import { Button, Input, Card, CardContent } from '@/components/ui';

interface LoginForm {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    
    try {
      // Mock authentication - in production, this would call your auth API
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
      
      if (data.email === 'federico@smartcompetitor.com' && data.password === 'federico999!') {
        // Store auth state (in production, use proper auth management)
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('userEmail', data.email);
        
        router.push('/dashboard');
      } else {
        setError('root', {
          type: 'manual',
          message: 'Credenziali non valide. Usa federico@smartcompetitor.com / federico999!'
        });
      }
    } catch (error) {
      setError('root', {
        type: 'manual',
        message: 'Errore durante il login. Riprova.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, #00B4D8 0%, transparent 50%),
                           radial-gradient(circle at 75% 75%, #38BDF8 0%, transparent 50%)`
        }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-md"
      >
        <Card className="shadow-hard">
          <CardContent padding="lg">
            {/* Logo & Brand */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="inline-flex items-center justify-center w-16 h-16 bg-gradient-primary rounded-2xl mb-4 shadow-glow-primary"
              >
                <Activity className="w-8 h-8 text-white" />
              </motion.div>
              
              <h1 className="text-2xl font-bold text-gradient mb-2">
                Smart Competitor Finder
              </h1>
              <p className="text-slate-400 text-sm">
                Accesso riservato ai consulenti registrati
              </p>
            </div>

            {/* Info Box - Richiesta Accesso */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-blue-300 mb-2">
                    Non hai ancora le credenziali di accesso?
                  </h3>
                  <p className="text-xs text-slate-300 mb-3">
                    Contatta Studio Innovativo per richiedere l'attivazione del tuo account e scoprire come Smart Competitor Finder può aiutarti.
                  </p>
                  <div className="space-y-2">
                    <a 
                      href="mailto:info@studioinnovativo.it"
                      className="flex items-center gap-2 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      <Mail className="w-3 h-3" />
                      info@studioinnovativo.it
                    </a>
                    <a 
                      href="https://www.studioinnovativo.it"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Visita il sito per maggiori informazioni
                    </a>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Login Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                type="email"
                label="Email"
                placeholder="tua@email.com"
                {...register('email', {
                  required: 'Email è obbligatoria',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email non valida'
                  }
                })}
                error={errors.email?.message}
              />

              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  label="Password"
                  placeholder="La tua password"
                  {...register('password', {
                    required: 'Password è obbligatoria',
                    minLength: {
                      value: 6,
                      message: 'Password deve essere di almeno 6 caratteri'
                    }
                  })}
                  error={errors.password?.message}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 mt-3 text-text-muted hover:text-text-primary transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {errors.root && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg"
                >
                  <p className="text-sm text-red-400">{errors.root.message}</p>
                </motion.div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full mt-6"
                isLoading={isLoading}
              >
                Accedi alla Dashboard
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center mt-6"
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
      </motion.div>
    </div>
  );
};

export default LoginPage;