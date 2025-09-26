import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Palette, 
  Upload, 
  Save, 
  Eye, 
  Monitor,
  Smartphone,
  Tablet,
  RefreshCw
} from 'lucide-react';

interface BrandingConfig {
  company_name: string;
  logo_url: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  font_family: string;
  cloudinho_avatar?: string;
}

interface AdminPanelProps {
  onConfigChange?: (config: BrandingConfig) => void;
}

export default function AdminPanel({ onConfigChange }: AdminPanelProps) {
  const [config, setConfig] = useState<BrandingConfig>({
    company_name: 'Select Soluções',
    logo_url: 'https://prisma.selectsolucoes.com/assets/logo.png',
    primary_color: '#1f2937',
    secondary_color: '#3b82f6',
    accent_color: '#10b981',
    font_family: 'Inter, sans-serif',
    cloudinho_avatar: 'https://prisma.selectsolucoes.com/assets/cloudinho-avatar.png'
  });

  const [previewMode, setPreviewMode] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Load current configuration
  useEffect(() => {
    loadBrandingConfig();
  }, []);

  const loadBrandingConfig = async () => {
    try {
      const response = await fetch('/api/admin/branding');
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      }
    } catch (error) {
      console.error('Failed to load branding config:', error);
    }
  };

  const saveBrandingConfig = async () => {
    setIsSaving(true);
    try {
      const response = await fetch('/api/admin/branding', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant: 'default',
          config: config
        })
      });

      if (response.ok) {
        setLastSaved(new Date());
        onConfigChange?.(config);
      }
    } catch (error) {
      console.error('Failed to save branding config:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfigChange = (key: keyof BrandingConfig, value: string) => {
    setConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const presetColors = [
    { name: 'Select Blue', primary: '#1f2937', secondary: '#3b82f6', accent: '#10b981' },
    { name: 'Corporate', primary: '#1e293b', secondary: '#0f172a', accent: '#0ea5e9' },
    { name: 'Modern Green', primary: '#064e3b', secondary: '#059669', accent: '#34d399' },
    { name: 'Purple Pro', primary: '#581c87', secondary: '#7c3aed', accent: '#a855f7' },
    { name: 'Orange Energy', primary: '#9a3412', secondary: '#ea580c', accent: '#fb923c' },
  ];

  const fontOptions = [
    'Inter, sans-serif',
    'Roboto, sans-serif',
    'Open Sans, sans-serif',
    'Lato, sans-serif',
    'Montserrat, sans-serif',
    'Poppins, sans-serif'
  ];

  const getPreviewSize = () => {
    switch (previewMode) {
      case 'mobile': return 'w-80 h-96';
      case 'tablet': return 'w-96 h-[500px]';
      default: return 'w-full h-[600px]';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Settings className="mr-3" />
            Painel Administrativo
          </h1>
          <p className="text-gray-600 mt-2">
            Personalize a aparência e configurações da plataforma Prisma
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Company Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Monitor className="mr-2" />
                Configurações da Empresa
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nome da Empresa
                  </label>
                  <input
                    type="text"
                    value={config.company_name}
                    onChange={(e) => handleConfigChange('company_name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL do Logo
                  </label>
                  <input
                    type="url"
                    value={config.logo_url}
                    onChange={(e) => handleConfigChange('logo_url', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Avatar do Cloudinho
                  </label>
                  <input
                    type="url"
                    value={config.cloudinho_avatar}
                    onChange={(e) => handleConfigChange('cloudinho_avatar', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </motion.div>

            {/* Color Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Palette className="mr-2" />
                Cores do Tema
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cor Primária
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="color"
                      value={config.primary_color}
                      onChange={(e) => handleConfigChange('primary_color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={config.primary_color}
                      onChange={(e) => handleConfigChange('primary_color', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cor Secundária
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="color"
                      value={config.secondary_color}
                      onChange={(e) => handleConfigChange('secondary_color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={config.secondary_color}
                      onChange={(e) => handleConfigChange('secondary_color', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cor de Destaque
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="color"
                      value={config.accent_color}
                      onChange={(e) => handleConfigChange('accent_color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={config.accent_color}
                      onChange={(e) => handleConfigChange('accent_color', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Color Presets */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Temas Predefinidos
                  </label>
                  <div className="grid grid-cols-1 gap-2">
                    {presetColors.map((preset) => (
                      <button
                        key={preset.name}
                        onClick={() => {
                          handleConfigChange('primary_color', preset.primary);
                          handleConfigChange('secondary_color', preset.secondary);
                          handleConfigChange('accent_color', preset.accent);
                        }}
                        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex space-x-1">
                          <div 
                            className="w-4 h-4 rounded"
                            style={{ backgroundColor: preset.primary }}
                          />
                          <div 
                            className="w-4 h-4 rounded"
                            style={{ backgroundColor: preset.secondary }}
                          />
                          <div 
                            className="w-4 h-4 rounded"
                            style={{ backgroundColor: preset.accent }}
                          />
                        </div>
                        <span className="text-sm">{preset.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Typography */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h2 className="text-xl font-semibold mb-4">Tipografia</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Família da Fonte
                </label>
                <select
                  value={config.font_family}
                  onChange={(e) => handleConfigChange('font_family', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {fontOptions.map((font) => (
                    <option key={font} value={font}>
                      {font.split(',')[0]}
                    </option>
                  ))}
                </select>
              </div>
            </motion.div>

            {/* Save Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <button
                onClick={saveBrandingConfig}
                disabled={isSaving}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
              >
                {isSaving ? (
                  <RefreshCw className="animate-spin mr-2" size={20} />
                ) : (
                  <Save className="mr-2" size={20} />
                )}
                {isSaving ? 'Salvando...' : 'Salvar Configurações'}
              </button>

              {lastSaved && (
                <p className="text-sm text-gray-500 text-center mt-2">
                  Última atualização: {lastSaved.toLocaleString('pt-BR')}
                </p>
              )}
            </motion.div>
          </div>

          {/* Preview Panel */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold flex items-center">
                  <Eye className="mr-2" />
                  Visualização
                </h2>

                {/* Preview Mode Selector */}
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPreviewMode('desktop')}
                    className={`p-2 rounded-lg transition-colors ${
                      previewMode === 'desktop' 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <Monitor size={20} />
                  </button>
                  <button
                    onClick={() => setPreviewMode('tablet')}
                    className={`p-2 rounded-lg transition-colors ${
                      previewMode === 'tablet' 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <Tablet size={20} />
                  </button>
                  <button
                    onClick={() => setPreviewMode('mobile')}
                    className={`p-2 rounded-lg transition-colors ${
                      previewMode === 'mobile' 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <Smartphone size={20} />
                  </button>
                </div>
              </div>

              {/* Preview Container */}
              <div className="flex justify-center">
                <div className={`${getPreviewSize()} border border-gray-200 rounded-lg overflow-hidden bg-gray-50`}>
                  <iframe
                    src={`/preview?config=${encodeURIComponent(JSON.stringify(config))}`}
                    className="w-full h-full"
                    title="Preview"
                  />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
