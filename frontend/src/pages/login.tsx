import { useState } from 'react';
import { useRouter } from 'next/router';

export default function Login() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    mfaCode: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [step, setStep] = useState<'login' | 'mfa'>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('https://ewapsbyof8.execute-api.us-east-1.amazonaws.com/prod/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        if (data.requiresMFA) {
          setStep('mfa');
        } else {
          localStorage.setItem('adminToken', data.token);
          router.push('/admin');
        }
      } else {
        setError(data.message || 'Erro ao fazer login');
      }
    } catch (error) {
      setError('Erro de conexão');
    }
    setLoading(false);
  };

  const handleMFA = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/verify-mfa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          mfaCode: formData.mfaCode
        })
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('adminToken', data.token);
        router.push('/admin');
      } else {
        setError(data.message || 'Código MFA inválido');
      }
    } catch (error) {
      setError('Erro de conexão');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <span className="text-white text-2xl font-bold">🔒</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            {step === 'login' ? 'Acesso Administrativo' : 'Verificação MFA'}
          </h1>
          <p className="text-gray-600 mt-2">
            {step === 'login' 
              ? 'Entre com suas credenciais para acessar o painel' 
              : 'Digite o código de verificação do seu aplicativo MFA'
            }
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">
            {step === 'login' ? 'Login' : 'Autenticação MFA'}
          </h2>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {step === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="admin@empresa.com"
                  required
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-1">Senha</label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    placeholder="••••••••"
                    required
                    className="w-full px-3 py-2 border rounded-md"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2 text-gray-500"
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
              </div>
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleMFA} className="space-y-4">
              <div>
                <label htmlFor="mfaCode" className="block text-sm font-medium mb-1">Código MFA</label>
                <input
                  id="mfaCode"
                  type="text"
                  value={formData.mfaCode}
                  onChange={(e) => setFormData({...formData, mfaCode: e.target.value})}
                  placeholder="123456"
                  maxLength={6}
                  required
                  className="w-full px-3 py-2 border rounded-md"
                />
                <p className="text-sm text-gray-600 mt-1">
                  Digite o código de 6 dígitos do seu aplicativo autenticador
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setStep('login')}
                  className="flex-1 border border-gray-300 py-2 rounded-md hover:bg-gray-50"
                >
                  Voltar
                </button>
                <button 
                  type="submit" 
                  disabled={loading}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Verificando...' : 'Verificar'}
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="text-center">
          <button 
            onClick={() => router.push('/chat')}
            className="text-blue-600 hover:underline"
          >
            Acessar Chat sem Login
          </button>
        </div>
      </div>
    </div>
  );
}
