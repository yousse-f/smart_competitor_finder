'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import { checkBackendHealth } from '@/lib/api';

export const BackendStatus = () => {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);
  const [showStatus, setShowStatus] = useState(false);

  useEffect(() => {
    const checkConnection = async () => {
      const health = await checkBackendHealth();
      setIsOnline(health);
      
      // Mostra lo status solo se offline o al primo caricamento
      if (!health || isOnline === null) {
        setShowStatus(true);
        setTimeout(() => setShowStatus(false), 5000);
      }
    };

    checkConnection();
    
    // Controlla ogni 30 secondi
    const interval = setInterval(checkConnection, 30000);
    
    return () => clearInterval(interval);
  }, [isOnline]);

  if (isOnline === null || !showStatus) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -50 }}
        className={`fixed top-4 right-4 z-50 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium ${
          isOnline 
            ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
            : 'bg-red-500/20 text-red-400 border border-red-500/30'
        }`}
      >
        {isOnline ? (
          <>
            <Wifi className="w-4 h-4" />
            Backend connesso
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4" />
            Backend offline - usando dati demo
          </>
        )}
      </motion.div>
    </AnimatePresence>
  );
};