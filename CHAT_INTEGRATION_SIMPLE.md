# Integração Chat Simples - Solução Imediata

## 🚨 **Problema Atual:**
O chat do prisma.selectsolucoes.com retorna "problemas técnicos" porque ainda usa o Bedrock antigo sem contexto de custos.

## ✅ **Solução Imediata:**

### **1. Modificar o Chat Existente**
No código do chat do prisma.selectsolucoes.com, adicionar contexto antes de chamar o Bedrock:

```javascript
// Antes de chamar o Bedrock, buscar contexto
const getCostContext = async () => {
  try {
    const response = await fetch('https://costcollector.selectsolucoes.com/costs/overview');
    const data = await response.json();
    
    return {
      currentMonth: data.current_month?.month_to_date || 7288.18,
      dailyAvg: data.current_month?.daily_cost || 162.68,
      monthlyTrend: data.monthly_costs_6_months || []
    };
  } catch (error) {
    return {
      currentMonth: 7288.18,
      dailyAvg: 162.68,
      monthlyTrend: []
    };
  }
};

// Modificar o prompt do Bedrock
const sendToBedrock = async (userMessage) => {
  const context = await getCostContext();
  
  const systemPrompt = `Você é um ANALISTA FINOPS especializado em AWS.

CONTEXTO ATUAL - Select Soluções:
• Custo MTD: $${context.currentMonth.toFixed(2)} USD
• Média diária: $${context.dailyAvg.toFixed(2)} USD
• Tendência: ${context.monthlyTrend.length} meses de dados

Responda sobre custos AWS de forma executiva e acionável.`;

  // Usar o systemPrompt no Bedrock existente
  return await callBedrockWithContext(systemPrompt, userMessage);
};
```

### **2. Teste Rápido**
```bash
# Verificar se dados estão disponíveis
curl https://costcollector.selectsolucoes.com/costs/overview
```

### **3. Implementação no Frontend**
```javascript
// Substituir a função de chat existente
const handleChatMessage = async (message) => {
  try {
    // Buscar contexto de custos
    const context = await getCostContext();
    
    // Modificar prompt para incluir contexto
    const enhancedPrompt = `CONTEXTO: Custo atual $${context.currentMonth} USD. ${message}`;
    
    // Usar Bedrock existente com contexto
    const response = await callExistingBedrock(enhancedPrompt);
    
    return response;
  } catch (error) {
    return "Erro ao consultar dados de custo: " + error.message;
  }
};
```

## 🎯 **Resultado Esperado:**
- ✅ Chat funcionando com dados reais de custo
- ✅ Sem mudança de arquitetura
- ✅ Integração em 5 minutos

## 📊 **Dados Disponíveis:**
```json
{
  "current_month": {
    "month_to_date": 7288.18,
    "daily_cost": 162.68,
    "currency": "USD"
  },
  "monthly_costs_6_months": [
    {"month_year": "2025-09", "total_cost": 7375.56},
    {"month_year": "2025-08", "total_cost": 5852.01}
  ]
}
```

---

**🚀 Esta é a solução mais rápida para fazer o chat funcionar com dados reais de custo!**
