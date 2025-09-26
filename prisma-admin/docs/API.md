# 📡 API Documentation - Prisma Admin

Base URL: `https://m153no51s0.execute-api.us-east-1.amazonaws.com/prod`

## 🔐 **Autenticação**

### POST `/login`
Autentica usuário e retorna JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "admin"
}
```

### POST `/verify`
Verifica validade do token JWT.

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "valid": true,
  "user": {
    "user_id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

### POST `/reset-password`
Reseta senha do usuário para "temp123".

**Request:**
```json
{
  "username": "admin"
}
```

## 💬 **Chat**

### POST `/chat`
Envia mensagem para IA e recebe resposta.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "message": "Olá, como você pode me ajudar?"
}
```

**Response:**
```json
{
  "response": "Olá! Sou o Cloudinho, seu assistente IA..."
}
```

## 👥 **Usuários**

### GET `/users`
Lista todos os usuários (apenas admin).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@selectsolucoes.com",
    "role": "admin",
    "status": "active",
    "permissions": "all",
    "created_at": "2025-01-01T00:00:00"
  }
]
```

### POST `/users`
Cria novo usuário (apenas admin).

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "username": "novo_user",
  "password": "senha123",
  "email": "user@exemplo.com",
  "role": "user",
  "status": "active",
  "permissions": "chat"
}
```

### PUT `/users`
Atualiza usuário existente (apenas admin).

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "id": 2,
  "email": "novo_email@exemplo.com",
  "role": "admin",
  "status": "blocked",
  "permissions": "all"
}
```

### DELETE `/users?id=<user_id>`
Remove usuário (apenas admin).

**Headers:** `Authorization: Bearer <token>`

## ⚙️ **Configurações**

### GET `/config`
Obtém configurações do usuário logado.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "aiModel": "claude-3-5-sonnet",
  "temperature": "0.7",
  "maxTokens": "1000"
}
```

### POST `/config`
Salva configurações do usuário.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "aiModel": "claude-3-haiku",
  "temperature": "0.5",
  "maxTokens": "500"
}
```

## 🎨 **Configurações Visuais**

### GET `/visual-config`
Obtém configurações visuais globais (público).

**Response:**
```json
{
  "app_name": "Cloudinho",
  "logo_url": "https://exemplo.com/logo.png",
  "primary_color": "#667eea",
  "secondary_color": "#764ba2",
  "sidebar_color": "#2c3e50"
}
```

### POST `/visual-config`
Salva configurações visuais (apenas admin).

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "app_name": "Minha Empresa",
  "logo_url": "https://exemplo.com/logo.png",
  "primary_color": "#ff6b6b",
  "secondary_color": "#4ecdc4",
  "sidebar_color": "#2c3e50"
}
```

## 🚨 **Códigos de Erro**

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Requisição inválida |
| 401 | Não autorizado |
| 403 | Acesso negado (não é admin) |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

## 🔒 **Segurança**

### **Headers CORS**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type,Authorization
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
```

### **Autenticação JWT**
- **Algoritmo:** HS256
- **Secret:** `secret_key` (configurável)
- **Expiração:** 24 horas
- **Header:** `Authorization: Bearer <token>`

### **Validações**
- Senhas são hasheadas com SHA256
- Tokens JWT verificados em todas as rotas protegidas
- Controle de acesso baseado em roles
- Sanitização de inputs

## 📝 **Exemplos de Uso**

### **Login e Chat**
```javascript
// 1. Login
const loginResponse = await fetch('/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});
const { token } = await loginResponse.json();

// 2. Chat
const chatResponse = await fetch('/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    message: 'Olá!'
  })
});
const { response } = await chatResponse.json();
```

### **Gerenciar Usuários**
```javascript
// Listar usuários
const users = await fetch('/users', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Criar usuário
await fetch('/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    username: 'novo_user',
    password: 'senha123',
    role: 'user'
  })
});
```

### **Customizar Aparência**
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
    primary_color: '#ff6b6b',
    sidebar_color: '#2c3e50'
  })
});
```
