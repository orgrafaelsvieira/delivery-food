# 🚀 Plano de Desenvolvimento - Plataforma de Delivery
## Event-Driven Architecture com Kafka

---

## 📐 Visão Arquitetural

### Microserviços
1. **Restaurant Service** - Gerencia restaurantes, cardápios e disponibilidade
2. **Order Service** - Processa e orquestra pedidos
3. **Delivery Service** - Gerencia entregadores e rastreamento
4. **Notification Service** - Envia notificações em tempo real

### Infraestrutura
- **Apache Kafka** - Message Broker para comunicação assíncrona
- **PostgreSQL** - Banco de dados relacional (um DB por serviço)
- **Redis** - Cache distribuído
- **Docker & Docker Compose** - Containerização
- **GitHub Actions** - CI/CD Pipeline

---

## 📋 FASE 1: Planejamento e Setup Inicial (Semana 1)

### 1.1 Definição da Arquitetura
**Entregáveis:**
- [ ] Diagrama de arquitetura de microserviços
- [ ] Diagrama de fluxo de eventos Kafka
- [ ] Modelo de dados de cada serviço
- [ ] Documentação de APIs (OpenAPI/Swagger)

**Atividades:**
- Definir tópicos Kafka (events)
- Mapear comunicação síncrona vs assíncrona
- Definir estrutura de pastas do monorepo
- Criar repositório GitHub com estrutura base

### 1.2 Setup do Ambiente de Desenvolvimento
**Entregáveis:**
- [ ] docker-compose.yml com todos os serviços
- [ ] Configuração de networks Docker
- [ ] Kafka + Zookeeper configurados
- [ ] PostgreSQL instances (4 databases)
- [ ] Redis configurado

**Estrutura de Pastas:**
```
delivery-platform/
├── restaurant-service/
├── order-service/
├── delivery-service/
├── notification-service/
├── docker-compose.yml
├── .github/
│   └── workflows/
├── docs/
└── README.md
```

---

## 🏗️ FASE 2: Restaurant Service (Semana 2)

### 2.1 Desenvolvimento do Serviço
**Entregáveis:**
- [ ] API REST completa (FastAPI/Flask)
- [ ] Modelos de dados (SQLAlchemy)
- [ ] CRUD de restaurantes
- [ ] CRUD de cardápios/itens
- [ ] Gestão de disponibilidade

**Endpoints:**
```
POST   /api/restaurants
GET    /api/restaurants
GET    /api/restaurants/{id}
PUT    /api/restaurants/{id}
DELETE /api/restaurants/{id}

POST   /api/restaurants/{id}/menu-items
GET    /api/restaurants/{id}/menu-items
PUT    /api/menu-items/{id}
DELETE /api/menu-items/{id}
```

### 2.2 Integração com Kafka
**Eventos Produzidos:**
- `restaurant.created`
- `restaurant.updated`
- `menu-item.availability.changed`

### 2.3 Cache com Redis
**Estratégia:**
- Cache de cardápios completos (TTL: 15min)
- Cache de restaurantes mais acessados
- Invalidação ao atualizar dados

### 2.4 Containerização
**Entregáveis:**
- [ ] Dockerfile otimizado (multi-stage)
- [ ] requirements.txt
- [ ] .dockerignore
- [ ] Health check endpoint

---

## 📦 FASE 3: Order Service (Semana 3-4)

### 3.1 Desenvolvimento do Serviço
**Entregáveis:**
- [ ] API REST para pedidos
- [ ] Máquina de estados do pedido
- [ ] Validação de itens/restaurante
- [ ] Cálculo de valores

**Estados do Pedido:**
```
PENDING → CONFIRMED → PREPARING → 
READY → IN_DELIVERY → DELIVERED → COMPLETED
              ↓
          CANCELLED
```

**Endpoints:**
```
POST   /api/orders
GET    /api/orders/{id}
GET    /api/orders/user/{user_id}
PUT    /api/orders/{id}/status
DELETE /api/orders/{id}
```

### 3.2 Event-Driven Integration
**Eventos Consumidos:**
- `restaurant.menu-item.availability.changed`

**Eventos Produzidos:**
- `order.created`
- `order.confirmed`
- `order.preparing`
- `order.ready`
- `order.cancelled`

### 3.3 Saga Pattern
**Implementar:**
- Orquestração de pedido
- Compensação em caso de falha
- Idempotência de eventos

### 3.4 Testes
**Entregáveis:**
- [ ] Testes unitários (pytest)
- [ ] Testes de integração
- [ ] Testes de eventos Kafka
- [ ] Cobertura mínima: 80%

---

## 🚗 FASE 4: Delivery Service (Semana 5)

### 4.1 Desenvolvimento do Serviço
**Entregáveis:**
- [ ] API REST para entregas
- [ ] Gestão de entregadores
- [ ] Atribuição automática de pedidos
- [ ] Rastreamento de localização

**Endpoints:**
```
POST   /api/deliveries
GET    /api/deliveries/{id}
PUT    /api/deliveries/{id}/location
PUT    /api/deliveries/{id}/status

POST   /api/couriers
GET    /api/couriers
GET    /api/couriers/{id}/available
```

### 4.2 Event-Driven Integration
**Eventos Consumidos:**
- `order.ready`

**Eventos Produzidos:**
- `delivery.assigned`
- `delivery.picked-up`
- `delivery.in-transit`
- `delivery.delivered`

### 4.3 Lógica de Negócio
**Implementar:**
- Algoritmo de atribuição de entregador
- Cálculo de tempo estimado
- Validação de disponibilidade

---

## 🔔 FASE 5: Notification Service (Semana 6)

### 5.1 Desenvolvimento do Serviço
**Entregáveis:**
- [ ] Consumer Kafka dedicado
- [ ] Sistema de templates
- [ ] Múltiplos canais (email/SMS simulado)
- [ ] Log de notificações enviadas

### 5.2 Event-Driven Integration
**Eventos Consumidos (todos):**
- `order.confirmed`
- `order.preparing`
- `order.ready`
- `delivery.assigned`
- `delivery.picked-up`
- `delivery.in-transit`
- `delivery.delivered`

### 5.3 Implementação
**Features:**
- Dead Letter Queue para falhas
- Retry com backoff exponencial
- Rate limiting
- Dedução de notificações duplicadas

---

## 🔧 FASE 6: Infraestrutura e DevOps (Semana 7)

### 6.1 Docker Compose Completo
**Entregáveis:**
- [ ] Todos os serviços orquestrados
- [ ] Networks customizadas
- [ ] Volumes persistentes
- [ ] Health checks
- [ ] Logging centralizado

### 6.2 Observabilidade
**Implementar:**
- [ ] Prometheus para métricas
- [ ] Grafana para dashboards
- [ ] Logging estruturado (JSON)
- [ ] Correlation IDs

### 6.3 GitHub Actions
**Pipelines:**

**Pipeline 1: CI (Continuous Integration)**
```yaml
Trigger: Push/PR
Steps:
  - Lint (flake8/black)
  - Unit tests
  - Integration tests
  - Code coverage report
  - Build Docker images
```

**Pipeline 2: CD (Continuous Deployment)**
```yaml
Trigger: Merge to main
Steps:
  - Build images
  - Push to registry
  - Deploy to staging
  - Run smoke tests
```

---

## 🧪 FASE 7: Testes e Qualidade (Semana 8)

### 7.1 Testes por Serviço
**Cada microserviço deve ter:**
- [ ] Testes unitários (80%+ cobertura)
- [ ] Testes de integração
- [ ] Testes de contrato (Consumer/Producer)
- [ ] Testes de eventos Kafka

### 7.2 Testes End-to-End
**Cenários:**
- [ ] Fluxo completo: Criar pedido → Entrega
- [ ] Cancelamento de pedido
- [ ] Indisponibilidade de item
- [ ] Falha de comunicação entre serviços

### 7.3 Testes de Performance
**Implementar:**
- [ ] Load testing (Locust/K6)
- [ ] Teste de throughput Kafka
- [ ] Teste de cache Redis
- [ ] Análise de bottlenecks

---

## 📚 FASE 8: Documentação (Semana 9)

### 8.1 Documentação Técnica
**Entregáveis:**
- [ ] README principal
- [ ] README por serviço
- [ ] Guia de setup local
- [ ] Guia de deploy
- [ ] Troubleshooting

### 8.2 Documentação de APIs
**Entregáveis:**
- [ ] OpenAPI/Swagger specs
- [ ] Postman collections
- [ ] Exemplos de requests/responses
- [ ] Documentação de eventos Kafka

### 8.3 Diagramas
**Criar:**
- [ ] Diagrama de arquitetura atualizado
- [ ] Diagrama de fluxo de eventos
- [ ] Diagrama de sequência (principais fluxos)
- [ ] Diagrama de estados do pedido

---

## 🎯 FASE 9: Refinamento e Melhorias (Semana 10)

### 9.1 Performance
- [ ] Otimização de queries SQL
- [ ] Índices de banco de dados
- [ ] Otimização de cache
- [ ] Connection pooling

### 9.2 Segurança
- [ ] Validação de inputs
- [ ] Rate limiting
- [ ] CORS configurado
- [ ] Secrets management

### 9.3 Features Extras (Opcional)
- [ ] Autenticação JWT
- [ ] Sistema de avaliações
- [ ] Histórico de pedidos
- [ ] Painel administrativo

---

## 📊 Definições Técnicas Importantes

### Tópicos Kafka
```
- restaurant.events
- order.events
- delivery.events
- notification.events
```

### Schema de Eventos (exemplo)
```json
{
  "event_id": "uuid",
  "event_type": "order.confirmed",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "order_id": "uuid",
    "restaurant_id": "uuid",
    "items": [...],
    "total": 0.00
  }
}
```

### Cache Strategy (Redis)
```
Keys Pattern:
- restaurant:{id}:menu (TTL: 15min)
- order:{id} (TTL: 1h)
- courier:{id}:location (TTL: 30s)
```

---

## ⚠️ Pontos de Atenção

### Desafios Técnicos
1. **Consistência Eventual** - Aceitar que dados podem estar temporariamente inconsistentes
2. **Idempotência** - Garantir que processar o mesmo evento duas vezes não cause problemas
3. **Ordenação de Eventos** - Garantir que eventos sejam processados na ordem correta
4. **Dead Letter Queue** - Tratar eventos que falharam após múltiplas tentativas

### Best Practices
- Usar correlation IDs em todas as requisições
- Implementar circuit breaker para chamadas síncronas
- Versionar eventos Kafka
- Manter logs estruturados
- Implementar graceful shutdown

---

## 📈 Métricas de Sucesso

### Técnicas
- ✅ Todos os serviços rodando via docker-compose
- ✅ Pipeline CI/CD funcionando
- ✅ Cobertura de testes > 80%
- ✅ Tempo de resposta APIs < 200ms
- ✅ Zero downtime em deployments

### Aprendizado
- ✅ Compreensão de arquitetura event-driven
- ✅ Domínio de Docker e containerização
- ✅ Experiência com mensageria (Kafka)
- ✅ Práticas de CI/CD
- ✅ Design de microserviços

---

## 🎓 Próximos Passos Após Conclusão

1. **Adicionar Kubernetes** - Orquestração de containers
2. **API Gateway** - Kong ou NGINX
3. **Service Mesh** - Istio para observabilidade
4. **Autenticação** - OAuth2/JWT
5. **Deploy em Cloud** - AWS/GCP/Azure

---

**Tempo Total Estimado:** 10 semanas
**Nível de Esforço:** 15-20h por semana
**Resultado:** Projeto portfolio completo com arquitetura profissional