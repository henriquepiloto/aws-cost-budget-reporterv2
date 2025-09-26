# Integração FinOps Chat - Bedrock com Contexto AWS

## 🎯 **Objetivo**
Transformar o chat do prisma.selectsolucoes.com em um **Analista FinOps** especializado em custos AWS.

## 💬 **Endpoint de Chat**

### **URL:**
```
POST https://costcollector.selectsolucoes.com/chat
```

### **Request:**
```json
{
  "message": "Qual é o custo atual do mês e como está a tendência?",
  "session_id": "optional_session_id"
}
```

### **Response:**
```json
{
  "response": "Análise FinOps detalhada...",
  "session_id": "finops_session",
  "context_used": {
    "account_id": "727706432228",
    "data_points": 6,
    "services_analyzed": 10
  }
}
```

## 🧠 **Contexto Automático**

O chat já inclui automaticamente:

### **KPIs Calculados:**
- **MTD Cost**: $7,288.18 USD (mês atual)
- **Média Diária**: $162.68 USD
- **Projeção Mês**: Baseada na tendência
- **Variação MoM**: % de mudança vs mês anterior

### **Dados Históricos:**
- **6 meses de tendência**: Setembro $7,375 | Agosto $5,852 | etc.
- **Top 10 serviços**: EC2, RDS, ECS, S3, etc.
- **Account ID**: 727706432228 (Select Soluções)

## 🔧 **Integração no Frontend**

### **JavaScript/React:**
```javascript
const sendFinOpsMessage = async (message) => {
  try {
    const response = await fetch('https://costcollector.selectsolucoes.com/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        session_id: `user_${Date.now()}`
      })
    });
    
    const data = await response.json();
    return data.response;
  } catch (error) {
    return "Erro ao consultar análise de custos: " + error.message;
  }
};

// Uso no chat existente
const handleChatMessage = async (userMessage) => {
  const finopsResponse = await sendFinOpsMessage(userMessage);
  // Exibir resposta no chat
  displayMessage(finopsResponse);
};
```

## 📊 **Exemplos de Perguntas**

### **Análise Geral:**
- "Como estão os custos este mês?"
- "Qual a tendência dos últimos 6 meses?"
- "Quais são os maiores gastos?"

### **Comparações:**
- "Como setembro compara com agosto?"
- "Qual serviço mais cresceu?"
- "Estamos gastando mais que o normal?"

### **Recomendações:**
- "Como posso reduzir custos?"
- "Quais otimizações recomendam?"
- "Onde focar para economizar?"

## 🎯 **Personalidade do Chat**

### **Tom FinOps:**
- **Executivo**: Resumos claros e diretos
- **Analítico**: Números, percentuais, evidências
- **Acionável**: Recomendações priorizadas
- **Brasileiro**: Linguagem natural em PT-BR

### **Estrutura de Resposta:**
1. **Resumo Executivo** (2-3 frases)
2. **Destaques** (bullets com números)
3. **Recomendações** (economia estimada + esforço)

## 🔄 **Fallback para Chat Geral**

Se o chat atual do prisma.selectsolucoes.com já funciona para outros tópicos, você pode:

### **Detectar Contexto:**
```javascript
const isFinOpsQuestion = (message) => {
  const finopsKeywords = [
    'custo', 'gasto', 'orçamento', 'aws', 'economia', 
    'otimização', 'serviço', 'fatura', 'billing'
  ];
  
  return finopsKeywords.some(keyword => 
    message.toLowerCase().includes(keyword)
  );
};

const handleMessage = async (message) => {
  if (isFinOpsQuestion(message)) {
    return await sendFinOpsMessage(message);
  } else {
    return await sendGeneralChatMessage(message);
  }
};
```

## 🚀 **Implementação Rápida**

### **1. Substituir Endpoint:**
No chat existente, trocar a URL do Bedrock por:
```
https://costcollector.selectsolucoes.com/chat
```

### **2. Manter Interface:**
Usar a mesma interface de chat, apenas mudando o backend.

### **3. Testar:**
```bash
curl -X POST https://costcollector.selectsolucoes.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Resumo dos custos AWS"}'
```

---

**🎯 Com essa integração, o chat se torna um verdadeiro Analista FinOps com dados reais da AWS!**
