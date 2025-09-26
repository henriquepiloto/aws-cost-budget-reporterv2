# Guia de Integração - Prisma + Cost Reporter

## 🔗 Integração com Sistema Existente

### **Frontend Existente:**
- **URL**: https://prisma.selectsolucoes.com
- **Recursos**: Usuários, Chat, Interface, Configurações

### **Backend Novo:**
- **URL**: https://costcollector.selectsolucoes.com
- **Recursos**: APIs de custos AWS completas

## 🌐 Endpoints para Integração

### **Análise Completa:**
```javascript
// Visão geral completa
GET https://costcollector.selectsolucoes.com/costs/overview

// Resposta:
{
  "monthly_costs_6_months": [...],
  "current_month": {...},
  "budgets": [...],
  "alerts_this_month": {...}
}
```

### **Endpoints Específicos:**
```javascript
// Custos mensais (6 meses)
GET https://costcollector.selectsolucoes.com/costs/monthly

// Mês atual
GET https://costcollector.selectsolucoes.com/costs/current-month

// Orçamentos
GET https://costcollector.selectsolucoes.com/budgets

// Alertas
GET https://costcollector.selectsolucoes.com/alerts

// Detalhamento por serviço
GET https://costcollector.selectsolucoes.com/costs/by-service
```

## 💬 Integração do Chat

### **Contexto para Bedrock:**
```javascript
// Função para buscar contexto de custos
async function getCostContext() {
  const response = await fetch('https://costcollector.selectsolucoes.com/costs/overview');
  const data = await response.json();
  
  return {
    currentMonth: data.current_month,
    budgets: data.budgets,
    monthlyTrend: data.monthly_costs_6_months
  };
}

// Integrar no prompt do chat existente
const systemPrompt = `Você é um assistente de custos AWS.
Contexto atual: ${JSON.stringify(await getCostContext())}
Responda sobre custos, orçamentos e otimizações.`;
```

## 📊 Componentes de Dashboard

### **Widget de Custo Atual:**
```javascript
// Componente React/Vue para custo do mês
const CurrentMonthCost = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('https://costcollector.selectsolucoes.com/costs/current-month')
      .then(res => res.json())
      .then(data => setData(data.current_month[0]));
  }, []);
  
  return (
    <div className="cost-widget">
      <h3>Custo do Mês</h3>
      <p>Atual: ${data?.month_to_date}</p>
      <p>Previsão: ${data?.forecasted_month}</p>
    </div>
  );
};
```

### **Gráfico de Tendência:**
```javascript
// Dados para gráfico mensal
const MonthlyChart = () => {
  const [chartData, setChartData] = useState([]);
  
  useEffect(() => {
    fetch('https://costcollector.selectsolucoes.com/costs/monthly')
      .then(res => res.json())
      .then(data => {
        const formatted = data.monthly_costs.map(item => ({
          month: item.year_month,
          cost: item.total_cost
        }));
        setChartData(formatted);
      });
  }, []);
  
  // Usar com Chart.js, D3, ou biblioteca de gráficos
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

### **Fase 1: Dados Básicos**
1. Integrar endpoint `/costs/overview` no dashboard
2. Mostrar custo atual do mês
3. Exibir orçamentos e % de uso

### **Fase 2: Chat Inteligente**
1. Atualizar chat para usar contexto de custos
2. Implementar perguntas sobre orçamentos
3. Alertas proativos de custos

### **Fase 3: Dashboard Avançado**
1. Gráficos de tendência mensal
2. Breakdown por serviço AWS
3. Alertas visuais de orçamento

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
    <span>Mês Atual: $4,230.45</span>
    <span>Previsão: $4,950.00</span>
  </div>
  <div class="budget-status">
    <span>Orçamento: 84.6% usado</span>
    <div class="progress-bar">
      <div class="progress" style="width: 84.6%"></div>
    </div>
  </div>
</div>
```

---

**🔗 Integração pronta para conectar prisma.selectsolucoes.com com costcollector.selectsolucoes.com**
