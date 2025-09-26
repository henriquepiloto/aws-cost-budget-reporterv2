import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  mfaEnabled: boolean;
  createdAt: string;
}

interface ChatConfig {
  primaryColor: string;
  secondaryColor: string;
  botName: string;
  welcomeMessage: string;
  theme: 'light' | 'dark';
}

export default function AdminPanel() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [chatConfig, setChatConfig] = useState<ChatConfig>({
    primaryColor: '#3b82f6',
    secondaryColor: '#1e40af',
    botName: 'Cloudinho',
    welcomeMessage: 'Olá! Como posso ajudar com análise de custos AWS?',
    theme: 'light'
  });
  const [newUser, setNewUser] = useState({ email: '', name: '', role: 'user' as 'admin' | 'user' });
  const [activeTab, setActiveTab] = useState('users');

  useEffect(() => {
    checkAuth();
    loadUsers();
    loadChatConfig();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      if (!token) {
        router.push('/login');
        return;
      }
      
      const response = await fetch('https://ewapsbyof8.execute-api.us-east-1.amazonaws.com/prod/auth/verify', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!response.ok) {
        router.push('/login');
      }
    } catch (error) {
      router.push('/login');
    }
  };

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch('/api/admin/users', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const loadChatConfig = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch('/api/admin/config', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.config) {
        setChatConfig(data.config);
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const createUser = async () => {
    if (!newUser.email || !newUser.name) return;
    
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch('/api/admin/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(newUser)
      });
      
      if (response.ok) {
        setNewUser({ email: '', name: '', role: 'user' });
        loadUsers();
      }
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  const updateChatConfig = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      await fetch('/api/admin/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(chatConfig)
      });
    } catch (error) {
      console.error('Error updating config:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Painel Administrativo</h1>
          <p className="text-gray-600">Gerencie usuários e configurações do chatbot</p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('users')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'users'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Usuários
              </button>
              <button
                onClick={() => setActiveTab('customization')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'customization'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Personalização
              </button>
            </nav>
          </div>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium mb-4">Criar Novo Usuário</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input
                  type="email"
                  placeholder="Email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  className="border rounded-md px-3 py-2"
                />
                <input
                  type="text"
                  placeholder="Nome"
                  value={newUser.name}
                  onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                  className="border rounded-md px-3 py-2"
                />
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value as 'admin' | 'user'})}
                  className="border rounded-md px-3 py-2"
                >
                  <option value="user">Usuário</option>
                  <option value="admin">Administrador</option>
                </select>
                <button
                  onClick={createUser}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Criar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium mb-4">Usuários Cadastrados</h2>
              <div className="space-y-3">
                {users.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">{user.name}</p>
                      <p className="text-sm text-gray-600">{user.email}</p>
                      <p className="text-xs text-gray-500">
                        {user.role} • Criado em: {new Date(user.createdAt).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs rounded ${user.role === 'admin' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                        {user.role}
                      </span>
                      {user.mfaEnabled && (
                        <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-800">
                          MFA
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Customization Tab */}
        {activeTab === 'customization' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-6">Personalização do Chatbot</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Nome do Bot</label>
                  <input
                    type="text"
                    value={chatConfig.botName}
                    onChange={(e) => setChatConfig({...chatConfig, botName: e.target.value})}
                    className="w-full border rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Mensagem de Boas-vindas</label>
                  <textarea
                    value={chatConfig.welcomeMessage}
                    onChange={(e) => setChatConfig({...chatConfig, welcomeMessage: e.target.value})}
                    className="w-full border rounded-md px-3 py-2"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Cor Primária</label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={chatConfig.primaryColor}
                      onChange={(e) => setChatConfig({...chatConfig, primaryColor: e.target.value})}
                      className="w-16 h-10 border rounded"
                    />
                    <input
                      type="text"
                      value={chatConfig.primaryColor}
                      onChange={(e) => setChatConfig({...chatConfig, primaryColor: e.target.value})}
                      className="flex-1 border rounded-md px-3 py-2"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Cor Secundária</label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={chatConfig.secondaryColor}
                      onChange={(e) => setChatConfig({...chatConfig, secondaryColor: e.target.value})}
                      className="w-16 h-10 border rounded"
                    />
                    <input
                      type="text"
                      value={chatConfig.secondaryColor}
                      onChange={(e) => setChatConfig({...chatConfig, secondaryColor: e.target.value})}
                      className="flex-1 border rounded-md px-3 py-2"
                    />
                  </div>
                </div>
                <button
                  onClick={updateChatConfig}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Salvar Configurações
                </button>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-4">Preview do Chat</h3>
                <div 
                  className="bg-white rounded-lg shadow-sm border p-4"
                  style={{ 
                    borderTopColor: chatConfig.primaryColor,
                    borderTopWidth: '3px'
                  }}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <div 
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                      style={{ backgroundColor: chatConfig.primaryColor }}
                    >
                      {chatConfig.botName.charAt(0)}
                    </div>
                    <span className="font-medium">{chatConfig.botName}</span>
                  </div>
                  <div className="bg-gray-100 p-3 rounded-lg text-sm">
                    {chatConfig.welcomeMessage}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
