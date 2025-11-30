# 📊 Report Completo: Account Page & Sidebar Buttons

## 🔍 Analisi Situazione Attuale

### **Account Page** (`/account`)

#### ✅ Cosa Funziona Bene:
1. **UI/UX Professionale**
   - Design moderno con dark theme
   - Animazioni Framer Motion fluide
   - Layout responsive (grid 3 colonne)
   - Card ben strutturate con gerarchie visive chiare

2. **Informazioni Visualizzate**
   - Profilo utente (avatar, nome, email, azienda, posizione)
   - Piano attuale (Free/Pro/Enterprise) con badge colorati
   - Statistiche di utilizzo (analisi mensili, progress bar)
   - Dati mock realistici per demo

3. **Funzionalità UI-Only**
   - Form di modifica profilo (nome, cognome, email, company, position)
   - Cambio password con show/hide toggle
   - Pulsanti "Salva Modifiche" e "Upgrade Piano"

#### ❌ Cosa NON Funziona (Simulato):

1. **Dati Hard-Coded**
   ```tsx
   const [profile, setProfile] = useState<UserProfile>({
     firstName: 'Mario',
     lastName: 'Rossi',
     email: 'mario.rossi@example.com',
     // ... tutti dati fissi
   });
   ```
   - Non legge dati da database
   - Non c'è autenticazione reale
   - Utente sempre "Mario Rossi"

2. **Salvataggio Profilo Simulato**
   ```tsx
   const handleSaveProfile = () => {
     console.log('Profilo salvato:', profile); // Solo console.log!
     alert('Profilo aggiornato con successo!'); // Alert falso
   };
   ```
   - **Nessuna chiamata API** al backend
   - Modifiche si perdono al refresh pagina
   - Solo stato locale React

3. **Cambio Password Finto**
   ```tsx
   const handlePasswordChange = () => {
     // Validazioni client-side OK
     if (passwordData.newPassword !== passwordData.confirmPassword) {...}
     
     console.log('Password cambiata'); // Solo console.log!
     alert('Password cambiata con successo!'); // Non cambia nulla
   };
   ```
   - Nessuna verifica password attuale nel DB
   - Nessun aggiornamento password hash
   - Security theater

4. **Piani Tariffari Non Gestiti**
   - Array `plans` hard-coded nel component
   - Bottone "Upgrade Piano" non collegato a payment gateway (Stripe/PayPal)
   - Nessuna gestione subscription/billing

5. **Statistiche Fake**
   ```tsx
   <span>Report totali</span> → <span>12</span> // Numero inventato
   <span>Competitors analizzati</span> → <span>1,247</span> // Fake
   ```
   - Solo un dato (`analysesThisMonth`) viene letto da `localStorage` dei report
   - Altri numeri sono placeholder

---

### **Sidebar Buttons**

#### 🔘 Bottoni Presenti:

1. **U (Avatar)** 
   - Cerchio gradient con lettera "U"
   - Sotto: "Utente" (bold) + "Consulente" (muted)
   - **Non cliccabile** - solo visualizzazione

2. **Impostazioni** (`Settings` icon)
   ```tsx
   <button className="flex items-center w-full...">
     <Settings className="w-4 h-4 mr-3" />
     Impostazioni
   </button>
   ```
   - **No onClick handler** → Non fa nulla
   - Non ha `href` → Non è un Link

3. **Logout** (`LogOut` icon)
   ```tsx
   <button className="flex items-center w-full...">
     <LogOut className="w-4 h-4 mr-3" />
     Logout
   </button>
   ```
   - **No onClick handler** → Non fa nulla
   - Stile hover rosso (UI-only)

#### ❌ Problemi:
- **Entrambi i bottoni sono "button morti"**: nessuna funzione collegata
- Non c'è sistema di autenticazione (JWT, session, cookie)
- Non c'è pagina `/settings` separata da `/account`
- Logout non può funzionare perché non c'è login reale

---

## 🚀 Implementazione Funzionamento Reale

### **FASE 1: Sistema di Autenticazione Base**

#### 1.1 - Backend API (FastAPI)

**File**: `backend/api/auth.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database mock (sostituire con PostgreSQL/MongoDB)
fake_users_db = {
    "mario.rossi@example.com": {
        "id": "user_001",
        "email": "mario.rossi@example.com",
        "first_name": "Mario",
        "last_name": "Rossi",
        "company": "Studio Innovativo",
        "position": "Marketing Manager",
        "hashed_password": pwd_context.hash("password123"),
        "plan": "free",
        "created_at": "2024-01-15"
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company: str
    position: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    company: str
    position: str
    plan: str
    created_at: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    email = verify_token(token)
    user = fake_users_db.get(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)  # username = email
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout():
    # Con JWT stateless, logout è client-side (rimuove token)
    return {"message": "Logged out successfully"}
```

**File**: `backend/api/user.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from .auth import get_current_user, pwd_context, fake_users_db

router = APIRouter()

class ProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company: str
    position: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    # Aggiorna dati nel database
    user_email = current_user["email"]
    if user_email in fake_users_db:
        fake_users_db[user_email].update({
            "first_name": data.first_name,
            "last_name": data.last_name,
            "email": data.email,
            "company": data.company,
            "position": data.position
        })
        return {"message": "Profile updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    # Verifica password attuale
    if not pwd_context.verify(data.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Valida nuova password
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Aggiorna password hash
    user_email = current_user["email"]
    fake_users_db[user_email]["hashed_password"] = pwd_context.hash(data.new_password)
    
    return {"message": "Password changed successfully"}

@router.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    # Query database per statistiche reali
    return {
        "total_reports": 12,
        "competitors_analyzed": 1247,
        "keywords_extracted": 3891,
        "analyses_this_month": 8,
        "analyses_limit": 10 if current_user["plan"] == "free" else 100
    }
```

**Registra router in** `backend/main.py`:

```python
from api import auth, user

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
```

---

#### 1.2 - Frontend: Context API per Auth

**File**: `frontend/src/contexts/AuthContext.tsx`

```tsx
'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company: string;
  position: string;
  plan: 'free' | 'pro' | 'enterprise';
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<User>) => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Carica token da localStorage al mount
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      fetchUserData(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserData = async (authToken: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setToken(authToken);
      } else {
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    localStorage.setItem('auth_token', data.access_token);
    await fetchUserData(data.access_token);
    router.push('/dashboard');
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    setToken(null);
    router.push('/login');
  };

  const updateProfile = async (data: Partial<User>) => {
    if (!token) throw new Error('Not authenticated');

    const response = await fetch('http://localhost:8000/api/user/profile', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error('Update failed');
    }

    setUser(prev => prev ? { ...prev, ...data } : null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, updateProfile, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

**Wrap app in** `frontend/src/app/layout.tsx`:

```tsx
import { AuthProvider } from '@/contexts/AuthContext';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

---

#### 1.3 - Sidebar con Funzioni Reali

**File**: `frontend/src/components/layout/Sidebar.tsx` (aggiornato)

```tsx
'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { clsx } from 'clsx';
import { 
  LayoutDashboard, 
  Search, 
  FileText, 
  User, 
  Settings,
  LogOut,
  Activity
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext'; // Import context

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Analisi', href: '/analyze', icon: Search },
  { name: 'Report', href: '/reports', icon: FileText },
  { name: 'Account', href: '/account', icon: User },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth(); // Usa context

  const handleLogout = () => {
    if (confirm('Sei sicuro di voler uscire?')) {
      logout(); // Chiama funzione reale
    }
  };

  return (
    <div className="flex flex-col w-64 bg-surface border-r border-border h-screen">
      {/* Logo & Brand */}
      <div className="flex items-center px-6 py-4 border-b border-border">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-text-primary">Smart Competitor</h1>
            <p className="text-xs text-text-muted">Finder</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200',
                {
                  'bg-primary-500/10 text-primary-400 border border-primary-500/20': isActive,
                  'text-text-secondary hover:text-text-primary hover:bg-surface-hover': !isActive,
                }
              )}
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User Section - AGGIORNATA */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center px-3 py-2 text-sm">
          <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center mr-3">
            <span className="text-white font-medium">
              {user?.first_name?.[0] || 'U'}{user?.last_name?.[0] || ''}
            </span>
          </div>
          <div className="flex-1">
            <p className="text-text-primary font-medium">
              {user?.first_name || 'Utente'}
            </p>
            <p className="text-text-muted text-xs">
              {user?.position || 'Consulente'}
            </p>
          </div>
        </div>
        
        <div className="mt-2 pt-2 border-t border-border">
          {/* BOTTONE IMPOSTAZIONI - ORA FUNZIONANTE */}
          <Link
            href="/account"
            className="flex items-center w-full px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded-lg transition-colors duration-200"
          >
            <Settings className="w-4 h-4 mr-3" />
            Impostazioni
          </Link>

          {/* BOTTONE LOGOUT - ORA FUNZIONANTE */}
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm text-text-secondary hover:text-error hover:bg-error/10 rounded-lg transition-colors duration-200"
          >
            <LogOut className="w-4 h-4 mr-3" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

#### 1.4 - Account Page con API Reali

**File**: `frontend/src/app/account/page.tsx` (aggiornato)

```tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
// ... import esistenti ...

export default function AccountPage() {
  const { user, token, updateProfile } = useAuth(); // Usa context
  const [profile, setProfile] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    position: ''
  });
  const [stats, setStats] = useState({
    totalReports: 0,
    competitorsAnalyzed: 0,
    keywordsExtracted: 0,
    analysesThisMonth: 0,
    analysesLimit: 10
  });

  // Carica dati utente dal context
  useEffect(() => {
    if (user) {
      setProfile({
        firstName: user.first_name,
        lastName: user.last_name,
        email: user.email,
        company: user.company,
        position: user.position
      });
    }
  }, [user]);

  // Carica statistiche da API
  useEffect(() => {
    const fetchStats = async () => {
      if (!token) return;

      try {
        const response = await fetch('http://localhost:8000/api/user/stats', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Error loading stats:', error);
      }
    };

    fetchStats();
  }, [token]);

  // SALVATAGGIO PROFILO REALE
  const handleSaveProfile = async () => {
    try {
      await updateProfile({
        first_name: profile.firstName,
        last_name: profile.lastName,
        email: profile.email,
        company: profile.company,
        position: profile.position
      });
      
      alert('Profilo aggiornato con successo!');
    } catch (error) {
      alert('Errore durante l\'aggiornamento del profilo');
    }
  };

  // CAMBIO PASSWORD REALE
  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('Le password non coincidono');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/user/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      alert('Password cambiata con successo!');
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      setShowPasswordChange(false);
    } catch (error: any) {
      alert(error.message || 'Errore durante il cambio password');
    }
  };

  // Usa `stats.totalReports` invece di numeri hard-coded
  return (
    <DashboardLayout>
      {/* ... resto del template esistente ... */}
      
      {/* Statistiche Reali */}
      <div className="space-y-4">
        <div className="flex justify-between">
          <span className="text-slate-400">Report totali</span>
          <span className="font-semibold text-slate-100">{stats.totalReports}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Competitors analizzati</span>
          <span className="font-semibold text-slate-100">{stats.competitorsAnalyzed}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Keywords estratte</span>
          <span className="font-semibold text-slate-100">{stats.keywordsExtracted}</span>
        </div>
      </div>
    </DashboardLayout>
  );
}
```

---

### **FASE 2: Protected Routes**

**File**: `frontend/src/middleware.ts`

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;
  const { pathname } = request.nextUrl;

  // Protected routes
  const protectedPaths = ['/dashboard', '/analyze', '/reports', '/account'];
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));

  // Se non autenticato e cerca di accedere a route protetta
  if (isProtectedPath && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Se autenticato e cerca di accedere a /login
  if (pathname === '/login' && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
};
```

---

### **FASE 3: Gestione Piani (Stripe Integration)**

**File**: `backend/api/billing.py`

```python
import stripe
from fastapi import APIRouter, Depends
from .auth import get_current_user

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,  # 'pro' or 'enterprise'
    current_user: dict = Depends(get_current_user)
):
    prices = {
        'pro': 'price_XXX',  # Stripe Price ID
        'enterprise': 'price_YYY'
    }
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': prices[plan],
            'quantity': 1,
        }],
        mode='subscription',
        success_url='http://localhost:3000/account?success=true',
        cancel_url='http://localhost:3000/account?canceled=true',
        client_reference_id=current_user['id']
    )
    
    return {"url": session.url}
```

**Frontend Button**:

```tsx
const handleUpgrade = async () => {
  const response = await fetch('http://localhost:8000/api/billing/create-checkout-session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ plan: 'pro' })
  });
  
  const { url } = await response.json();
  window.location.href = url; // Redirect a Stripe Checkout
};
```

---

## 📋 Checklist Implementazione

### Backend
- [ ] Installare dipendenze: `pip install passlib[bcrypt] python-jose[cryptography] python-multipart stripe`
- [ ] Creare `backend/api/auth.py`
- [ ] Creare `backend/api/user.py`
- [ ] Creare `backend/api/billing.py`
- [ ] Registrare router in `main.py`
- [ ] Configurare `JWT_SECRET_KEY` in `.env`
- [ ] Setup database reale (PostgreSQL + SQLAlchemy) al posto di `fake_users_db`

### Frontend
- [ ] Creare `AuthContext.tsx`
- [ ] Wrap app in `AuthProvider`
- [ ] Aggiornare `Sidebar.tsx` con `useAuth()` e onClick handlers
- [ ] Aggiornare `account/page.tsx` con API calls reali
- [ ] Creare `middleware.ts` per protected routes
- [ ] Aggiungere Stripe integration per upgrade piano

### Testing
- [ ] Test login flow
- [ ] Test logout (verifica redirect)
- [ ] Test salvataggio profilo
- [ ] Test cambio password
- [ ] Test protected routes (accesso negato senza token)
- [ ] Test upgrade piano (Stripe Checkout)

---

## 🎯 Priorità Implementazione

### **HIGH PRIORITY** (MVP Funzionante):
1. ✅ Sistema auth base (login/logout)
2. ✅ Context API + token management
3. ✅ Protected routes middleware
4. ✅ Sidebar logout funzionante
5. ✅ Account page - salvataggio profilo reale

### **MEDIUM PRIORITY** (Professionale):
6. Cambio password con verifica backend
7. Statistiche utente da database reale
8. Avatar upload (AWS S3 o Cloudinary)

### **LOW PRIORITY** (Monetizzazione):
9. Stripe integration per upgrade
10. Gestione subscription/billing
11. Limiti uso basati su piano (rate limiting)

---

## 💡 Note Finali

**Situazione Attuale**: Sistema demo con UI professionale ma **ZERO backend connectivity**.

**Dopo Implementazione**: SaaS B2B funzionante con:
- Login/Logout reale
- Dati utente persistenti
- Protected routes
- Cambio profilo/password
- (Opzionale) Billing Stripe

**Tempo Stimato**: 
- Fase 1 (Auth base): **4-6 ore**
- Fase 2 (Protected routes): **1-2 ore**
- Fase 3 (Stripe): **3-4 ore**

**TOTALE**: ~8-12 ore per sistema completamente funzionante.
