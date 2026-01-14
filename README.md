# 🌦️ Weather Analytics Dashboard

Aplicação completa de análise de clima com Streamlit, incluindo dados em tempo real, gráficos comparativos, análise semanal e muito mais!

## 📋 Funcionalidades

✅ **Clima Atual em Tempo Real**
- Temperatura atual, máxima e mínima
- Sensação térmica
- Umidade e pressão atmosférica
- Velocidade e direção do vento
- Visibilidade e cobertura de nuvens
- Horários de nascer e pôr do sol

✅ **Geolocalização Automática**
- Detecta localização do usuário por IP
- Usa APIs de geolocalização confiáveis (ipapi.co e ipinfo.io)
- Fallback para Goiânia caso não detecte
- Permite buscar qualquer outra localização manualmente

✅ **Análise de Previsão (5 dias)**
- Previsão de temperatura
- Previsão de precipitação
- Comparativo temperatura vs chuva
- Análise semanal com agregações diárias

✅ **Gráficos Interativos**
- 📈 Evolução de temperatura
- 🌧️ Previsão de chuva
- 📊 Gráficos comparativos
- 📅 Análise semanal com estatísticas

✅ **Funcionalidades Avançadas**
- 🔍 Busca de qualquer localização do mundo
- 📊 Estatísticas automáticas
- 📥 Download de dados em CSV
- 🎨 Interface moderna e responsiva
- 💾 Cache automático (1 hora)
- 🌐 Geolocalização automática por IP

## 🚀 Como Instalar e Rodar Localmente

### 1. Clone ou crie o repositório

```bash
git clone seu-repositorio-url
cd seu-repositorio
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a chave de API

Crie um arquivo `.streamlit/secrets.toml`:

```toml
OPENWEATHER_API_KEY = "sua_chave_aqui"
```

### 5. Execute a aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

---

## 🌐 Deploy no Streamlit Cloud

### 1. Faça push do repositório no GitHub

Certifique-se de que seu repositório contém:
- `app.py` (arquivo principal)
- `requirements.txt`
- `.streamlit/secrets.toml` (NÃO faça commit disso!)

### 2. Configure os Secrets no Streamlit Cloud

1. Acesse [https://share.streamlit.io](https://share.streamlit.io)
2. Clique em "New app" → "From GitHub repository"
3. Selecione seu repositório
4. Selecione o branch `main` e arquivo `app.py`
5. Clique em "Deploy"
6. Após deploy, vá em "Settings" → "Secrets"
7. Cole o conteúdo do seu `secrets.toml`:

```toml
OPENWEATHER_API_KEY = "sua_chave_aqui"
```

### 3. Acesse sua aplicação

Você receberá uma URL pública para compartilhar!

---

## 📁 Estrutura do Projeto

```
seu-repositorio/
├── app.py                    # Aplicação principal
├── requirements.txt          # Dependências Python
├── .streamlit/
│   └── secrets.toml         # Chaves (NÃO fazer commit!)
└── README.md                # Este arquivo
```

---

## 🔑 Obtendo a Chave de API OpenWeatherMap

1. Acesse [https://openweathermap.org/api](https://openweathermap.org/api)
2. Clique em "Sign Up" e crie uma conta gratuita
3. Vá para "API keys" no seu dashboard
4. Copie sua chave padrão (Default key)
5. Use essa chave na configuração de secrets

**Plano Gratuito Inclui:**
- Até 1.000 chamadas por dia
- Dados atuais e previsão de 5 dias
- Sem limitações de localização

---

## 📊 Tipos de Gráficos Disponíveis

### 🌡️ Temperatura
- Evolução de temperatura em 5 dias
- Temperatura máxima e mínima
- Estatísticas de temperatura

### 🌧️ Precipitação
- Previsão de chuva acumulada
- Dias com e sem chuva
- Máximas de precipitação

### 📊 Comparativo
- Gráfico com eixos duplos
- Temperatura vs Precipitação
- Relação visual entre os dois

### 📅 Análise Semanal
- Agregação por dia
- Temperatura média, máxima e mínima
- Chuva acumulada por dia
- Tabela resumida com estatísticas

---

## 🌐 Geolocalização Automática

A aplicação detecta automaticamente a localização do usuário através do seu endereço IP usando duas APIs confiáveis:

1. **ipapi.co** - API gratuita e confiável
2. **ipinfo.io** - Fallback secundário

### Como Funciona:

1. ✅ Ao acessar o app, a localização é detectada automaticamente
2. ✅ Os dados do clima são carregados para sua localização
3. ✅ Você pode mudar para qualquer outra cidade manualmente
4. ✅ Se a detecção falhar, usa Goiânia como padrão

### Privacidade:

- Nenhum dado pessoal é armazenado
- A localização é apenas para melhorar a experiência
- Você pode sempre mudar manualmente para outra localização
- As APIs usam apenas informações públicas de IP

---

1. **Mudar Localização**: Use a barra lateral para buscar qualquer cidade do mundo
2. **Salvar Dados**: Baixe os dados em CSV para análises posteriores
3. **Caching**: Os dados são cacheados por 1 hora para melhor desempenho
4. **Análise Histórica**: Selecione o período desejado na barra lateral
5. **Compartilhar**: A URL gerada no Streamlit Cloud é pública e compartilhável

---

## 🐛 Troubleshooting

**Erro: "Configure a chave OPENWEATHER_API_KEY"**
- Verifique se `secrets.toml` está configurado corretamente
- Reinicie o Streamlit: `streamlit run app.py`

**Erro: "Localização não encontrada"**
- A busca usa a API Nominatim (Open Street Map)
- Tente com nome de cidade mais genérico
- Usa a localização padrão (Goiânia) automaticamente

**Dados não atualizam**
- Aguarde 1 hora (cache) ou reinicie a aplicação
- Pressione `R` no Streamlit para recarregar

---

## 📝 Licença

Este projeto é de código aberto e pode ser usado livremente.

---

## 🌍 Desenvolvido com

- [Streamlit](https://streamlit.io) - Framework web
- [OpenWeatherMap API](https://openweathermap.org/api) - Dados de clima
- [Geopy](https://geopy.readthedocs.io) - Geolocalização
- [Pandas](https://pandas.pydata.org) - Análise de dados
- [Matplotlib & Seaborn](https://matplotlib.org) - Visualizações

---

**Última atualização:** Janeiro de 2026
