# Guia de Integração - Prisma + Cost Reporter

## 🔗 Integração com Sistema Existente

### **Frontend Existente:**
- **URL**: https://prisma.selectsolucoes.com
- **Recursos**: Usuários, Chat, Interface, Configurações

### **Backend Novo:**
- **URL**: https://costcollector.selectsolucoes.com
- **Recursos**: APIs de custos AWS completas

## 🌐 Endpoints para Integração

### **Endpoints Implementados:**
```javascript
// Visão geral dos custos
GET https://costcollector.selectsolucoes.com/costs/overview

// Resposta:
{
  "monthly_costs_6_months": [...],
  "current_month": {...},
  "status": "ready_for_finops_chat"
}

// Chat FinOps (principal funcionalidade)
POST https://costcollector.selectsolucoes.com/chat

// Health check
GET https://costcollector.selectsolucoes.com/health
```

## 💬 Integração do Chat FinOps

### **Funcionalidade Principal:**
```javascript
// Função para usar o Chat FinOps
async function sendFinOpsMessage(message) {
  const response = await fetch('https://costcollector.selectsolucoes.com/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      session_id: `user_${Date.now()}`
    })
  });
  
  const data = await response.json();
  return data.response; // Resposta inteligente do Bedrock
}

// Integrar no chat existente
const handleChatMessage = async (userMessage) => {
  const finopsResponse = await sendFinOpsMessage(userMessage);
  displayMessage(finopsResponse);
};
```

### **Contexto Automático:**
O chat já inclui automaticamente:
- Custos atuais da conta 727706432228
- Tendência dos últimos 6 meses
- Análise executiva com recomendações

## 📊 Componentes de Dashboard

### **Widget de Custo Atual:**
```javascript
// Componente React/Vue para custo do mês
const CurrentMonthCost = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('https://costcollector.selectsolucoes.com/costs/overview')
      .then(res => res.json())
      .then(data => setData(data.current_month));
  }, []);
  
  return (
    <div className="cost-widget">
      <h3>Custo do Mês</h3>
      <p>Atual: ${data?.month_to_date}</p>
      <p>Diário: ${data?.daily_cost}</p>
    </div>
  );
};
```

### **Chat FinOps Widget:**
```javascript
// Widget de chat integrado
const FinOpsChat = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  
  const sendMessage = async () => {
    const result = await fetch('https://costcollector.selectsolucoes.com/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await result.json();
    setResponse(data.response);
  };
  
  return (
    <div className="finops-chat">
      <input value={message} onChange={e => setMessage(e.target.value)} />
      <button onClick={sendMessage}>Perguntar ao FinOps</button>
      <div className="response">{response}</div>
    </div>
  );
};
```

## 🔧 Configuração CORS

### **Se necessário, adicionar CORS no backend:**
```python
# No main.py da API
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://prisma.selectsolucoes.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🎯 Plano de Implementação

### **Fase 1: Chat FinOps (Pronto)**
1. ✅ Integrar endpoint `/chat` no sistema existente
2. ✅ Chat inteligente com contexto AWS automático
3. ✅ Respostas executivas com recomendações

### **Fase 2: Dashboard Básico**
1. Integrar endpoint `/costs/overview` no dashboard
2. Mostrar custo atual do mês
3. Exibir tendência dos últimos 6 meses

### **Fase 3: Expansão (Futuro)**
1. Implementar coleta de orçamentos
2. Adicionar alertas de custo
3. Detalhamento por serviço AWS

## 🧪 Testes de Integração

```bash
# Testar endpoints
make integration-test

# Verificar CORS
curl -H "Origin: https://prisma.selectsolucoes.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS https://costcollector.selectsolucoes.com/costs/overview
```

## 📱 Exemplo de Interface

### **Dashboard Card:**
```html
<div class="cost-summary-card">
  <h3>Resumo de Custos</h3>
  <div class="current-month">
    <span>Mês Atual: $7,288.18</span>
    <span>Média Diária: $162.68</span>
  </div>
  <div class="finops-chat">
    <button onclick="openFinOpsChat()">💬 Perguntar ao FinOps</button>
  </div>
</div>
```

### **Chat FinOps Integrado:**
```html
<div class="finops-chat-widget">
  <h4>🤖 Analista FinOps</h4>
  <input id="finops-input" placeholder="Ex: Como estão os custos este mês?" />
  <button onclick="sendFinOpsMessage()">Enviar</button>
  <div id="finops-response" class="response-area"></div>
</div>
```

---

**🔗 Integração pronta: Chat FinOps + Dados básicos de custo**
