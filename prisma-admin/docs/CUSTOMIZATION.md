# 🎨 Guia de Customização - Prisma Admin

Este guia explica como personalizar completamente a aparência e funcionalidades do sistema Prisma Admin.

## 🎨 **Customização Visual**

### **Configurações Disponíveis**

#### **1. Nome da Aplicação**
- **Localização:** Aparece em toda interface
- **Padrão:** "Cloudinho"
- **Onde aparece:**
  - Tela de login
  - Menu lateral
  - Mensagens do chat
  - Título das páginas

#### **2. Logo Personalizado**
- **Formato:** URL de imagem externa
- **Formatos suportados:** PNG, JPG, SVG, WebP
- **Tamanho recomendado:** 150x50px
- **Onde aparece:**
  - Tela de login (60px altura máx)
  - Menu lateral (40px altura máx)

#### **3. Cores Personalizáveis**

**Cor Primária**
- **Uso:** Botões, links, elementos ativos
- **Padrão:** `#667eea`
- **Aplicação:** CSS variable `--primary-color`

**Cor Secundária**
- **Uso:** Gradientes, elementos secundários
- **Padrão:** `#764ba2`
- **Aplicação:** CSS variable `--secondary-color`

**Cor do Menu Lateral**
- **Uso:** Fundo do sidebar
- **Padrão:** `#2c3e50`
- **Aplicação:** CSS variable `--sidebar-color`

### **Como Personalizar**

#### **Via Interface Admin**
1. Acesse https://prisma.selectsolucoes.com
2. Faça login com credenciais admin
3. Vá em "🎨 Aparência"
4. Altere as configurações desejadas
5. Clique "💾 Salvar Alterações"

#### **Via API**
```javascript
// Obter configurações atuais
const config = await fetch('/visual-config').then(r => r.json());

// Salvar novas configurações
await fetch('/visual-config', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    app_name: 'Minha Empresa',
    logo_url: 'https://exemplo.com/logo.png',
    primary_color: '#ff6b6b',
    secondary_color: '#4ecdc4',
    sidebar_color: '#2c3e50'
  })
});
```

#### **Diretamente no Banco**
```sql
-- Atualizar nome da aplicação
INSERT INTO chatbot_visual_config (config_key, config_value) 
VALUES ('app_name', 'Minha Empresa') 
ON DUPLICATE KEY UPDATE config_value = 'Minha Empresa';

-- Atualizar logo
INSERT INTO chatbot_visual_config (config_key, config_value) 
VALUES ('logo_url', 'https://exemplo.com/logo.png') 
ON DUPLICATE KEY UPDATE config_value = 'https://exemplo.com/logo.png';

-- Atualizar cores
INSERT INTO chatbot_visual_config (config_key, config_value) 
VALUES ('primary_color', '#ff6b6b') 
ON DUPLICATE KEY UPDATE config_value = '#ff6b6b';
```

## 🎨 **Exemplos de Customização**

### **Tema Corporativo Azul**
```json
{
  "app_name": "Assistente Corporativo",
  "logo_url": "https://exemplo.com/logo-corp.png",
  "primary_color": "#1e3a8a",
  "secondary_color": "#3b82f6",
  "sidebar_color": "#1e293b"
}
```

### **Tema Verde Sustentável**
```json
{
  "app_name": "EcoAssistente",
  "logo_url": "https://exemplo.com/eco-logo.png",
  "primary_color": "#059669",
  "secondary_color": "#10b981",
  "sidebar_color": "#064e3b"
}
```

### **Tema Roxo Criativo**
```json
{
  "app_name": "Creative AI",
  "logo_url": "https://exemplo.com/creative-logo.png",
  "primary_color": "#7c3aed",
  "secondary_color": "#a855f7",
  "sidebar_color": "#581c87"
}
```

## 🔧 **Customização Avançada**

### **Modificar CSS Diretamente**

#### **Adicionar Novas Variáveis CSS**
```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --sidebar-color: #2c3e50;
  
  /* Novas variáveis personalizadas */
  --accent-color: #f59e0b;
  --text-color: #374151;
  --border-color: #d1d5db;
  --success-color: #10b981;
  --error-color: #ef4444;
}
```

#### **Personalizar Componentes**
```css
/* Customizar botões */
.btn {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* Customizar sidebar */
.sidebar {
  background: linear-gradient(180deg, var(--sidebar-color), #1a202c);
  border-right: 3px solid var(--primary-color);
}

/* Customizar chat */
.message.user {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 18px 18px 4px 18px;
}

.message.bot {
  background: #f7fafc;
  border: 1px solid var(--border-color);
  border-radius: 18px 18px 18px 4px;
}
```

### **Adicionar Animações**
```css
/* Animação de entrada */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.config-section {
  animation: slideIn 0.5s ease-out;
}

/* Animação de hover nos itens do menu */
.menu-item {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.menu-item::before {
  content: '';
  position: absolute;
  left: -100%;
  top: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.5s;
}

.menu-item:hover::before {
  left: 100%;
}
```

### **Customizar Responsividade**
```css
/* Tablet */
@media (max-width: 1024px) {
  .sidebar {
    width: 250px;
  }
  
  .main-content {
    padding: 15px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    order: 2;
  }
  
  .main-content {
    order: 1;
  }
  
  .login-box {
    width: 90%;
    padding: 20px;
  }
}
```

## 🌟 **Funcionalidades Personalizáveis**

### **Modificar Mensagens do Sistema**
```javascript
// No arquivo JavaScript, localizar e modificar:
const systemMessages = {
  welcome: `Bem-vindo ao ${visualConfig.app_name || 'Cloudinho'}! Como posso ajudar você hoje?`,
  loginSuccess: 'Login realizado com sucesso!',
  configSaved: 'Configurações salvas com sucesso!',
  userCreated: 'Usuário criado com sucesso!',
  // Adicionar mais mensagens...
};
```

### **Personalizar Modelos de IA**
```javascript
// Adicionar novos modelos no select
const aiModels = [
  { value: 'claude-3-5-sonnet', label: 'Claude 3.5 Sonnet (Recomendado)' },
  { value: 'claude-3-haiku', label: 'Claude 3 Haiku (Rápido)' },
  { value: 'claude-3-opus', label: 'Claude 3 Opus (Avançado)' },
  // Adicionar novos modelos...
];
```

### **Customizar Permissões**
```javascript
// Definir níveis de permissão personalizados
const permissionLevels = {
  'chat': ['chat'],
  'chat_config': ['chat', 'config'],
  'user_manager': ['chat', 'config', 'users'],
  'admin': ['chat', 'config', 'users', 'visual', 'system'],
  'super_admin': ['all']
};
```

## 🔌 **Integrações Personalizadas**

### **Adicionar Novos Endpoints**
```python
# No arquivo lambda_function.py
def handle_custom_endpoint(event, cors_headers):
    # Sua lógica personalizada aqui
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({'message': 'Custom endpoint response'})
    }

# Adicionar no lambda_handler
elif path == '/custom-endpoint' and method == 'POST':
    return handle_custom_endpoint(event, cors_headers)
```

### **Integrar com Serviços Externos**
```python
import requests

def integrate_external_service(data):
    # Exemplo: integração com CRM
    response = requests.post('https://api.crm.com/leads', {
        'name': data.get('name'),
        'email': data.get('email'),
        'source': 'Prisma Admin'
    })
    return response.json()
```

### **Adicionar Webhooks**
```python
def send_webhook(event_type, data):
    webhook_url = os.environ.get('WEBHOOK_URL')
    if webhook_url:
        payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        requests.post(webhook_url, json=payload)
```

## 📱 **Customização Mobile**

### **PWA (Progressive Web App)**
```json
// manifest.json
{
  "name": "Prisma Admin",
  "short_name": "Prisma",
  "description": "Painel Administrativo Cloudinho",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#667eea",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### **Service Worker**
```javascript
// sw.js
const CACHE_NAME = 'prisma-admin-v1';
const urlsToCache = [
  '/',
  '/index.html',
  // Adicionar recursos para cache offline
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});
```

## 🎯 **Melhores Práticas**

### **Performance**
- Otimizar imagens do logo (WebP, tamanho adequado)
- Usar CSS variables para mudanças dinâmicas
- Implementar lazy loading para componentes pesados
- Minimizar requests desnecessários

### **Acessibilidade**
- Manter contraste adequado nas cores
- Adicionar alt text em imagens
- Usar semantic HTML
- Implementar navegação por teclado

### **Segurança**
- Validar URLs de logos antes de usar
- Sanitizar inputs de customização
- Implementar rate limiting
- Usar HTTPS sempre

### **Manutenibilidade**
- Documentar customizações
- Usar versionamento para mudanças
- Manter backup das configurações
- Testar em diferentes dispositivos

## 🔄 **Backup e Restore**

### **Backup das Configurações**
```bash
# Backup via MySQL
mysqldump -h HOST -u USER -p DATABASE chatbot_visual_config > visual_config_backup.sql

# Backup via API
curl -H "Authorization: Bearer $TOKEN" \
  https://api.exemplo.com/visual-config > config_backup.json
```

### **Restore das Configurações**
```bash
# Restore via MySQL
mysql -h HOST -u USER -p DATABASE < visual_config_backup.sql

# Restore via API
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @config_backup.json \
  https://api.exemplo.com/visual-config
```
