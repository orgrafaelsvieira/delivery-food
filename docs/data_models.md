# 🗄️ Modelos de Dados - Plataforma de Delivery

---

## 1. RESTAURANT SERVICE DATABASE

### 📋 Tabela: `restaurants`
```sql
CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(500) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    cuisine_type VARCHAR(100),
    rating DECIMAL(2,1) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT true,
    opening_time TIME,
    closing_time TIME,
    delivery_fee DECIMAL(10,2) DEFAULT 0.00,
    minimum_order DECIMAL(10,2) DEFAULT 0.00,
    average_preparation_time INTEGER, -- em minutos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT rating_range CHECK (rating >= 0 AND rating <= 5)
);

CREATE INDEX idx_restaurants_cuisine ON restaurants(cuisine_type);
CREATE INDEX idx_restaurants_active ON restaurants(is_active);
```

### 🍕 Tabela: `menu_items`
```sql
CREATE TABLE menu_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- 'main', 'dessert', 'drink', 'appetizer'
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    is_available BOOLEAN DEFAULT true,
    preparation_time INTEGER, -- em minutos
    calories INTEGER,
    allergens TEXT[], -- array de alérgenos
    is_vegetarian BOOLEAN DEFAULT false,
    is_vegan BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    CONSTRAINT price_positive CHECK (price > 0)
);

CREATE INDEX idx_menu_items_restaurant ON menu_items(restaurant_id);
CREATE INDEX idx_menu_items_category ON menu_items(category);
CREATE INDEX idx_menu_items_available ON menu_items(is_available);
```

### ⏰ Tabela: `restaurant_hours`
```sql
CREATE TABLE restaurant_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0=domingo, 6=sábado
    opening_time TIME NOT NULL,
    closing_time TIME NOT NULL,
    is_closed BOOLEAN DEFAULT false,
    
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    CONSTRAINT day_range CHECK (day_of_week >= 0 AND day_of_week <= 6),
    UNIQUE (restaurant_id, day_of_week)
);
```

---

## 2. ORDER SERVICE DATABASE

### 📦 Tabela: `orders`
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(20) UNIQUE NOT NULL, -- ORD-20250101-001
    restaurant_id UUID NOT NULL,
    customer_id UUID NOT NULL, -- referência externa (user service)
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    
    -- Dados do cliente (snapshot)
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_email VARCHAR(255),
    
    -- Endereço de entrega
    delivery_address VARCHAR(500) NOT NULL,
    delivery_neighborhood VARCHAR(100),
    delivery_city VARCHAR(100) NOT NULL,
    delivery_state VARCHAR(2) NOT NULL,
    delivery_zipcode VARCHAR(10) NOT NULL,
    delivery_latitude DECIMAL(10,8),
    delivery_longitude DECIMAL(11,8),
    
    -- Valores
    subtotal DECIMAL(10,2) NOT NULL,
    delivery_fee DECIMAL(10,2) DEFAULT 0.00,
    discount DECIMAL(10,2) DEFAULT 0.00,
    tax DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL,
    
    -- Informações adicionais
    payment_method VARCHAR(50) NOT NULL, -- 'credit_card', 'debit_card', 'cash', 'pix'
    payment_status VARCHAR(50) DEFAULT 'PENDING',
    notes TEXT,
    
    -- Timestamps
    estimated_delivery_time TIMESTAMP,
    confirmed_at TIMESTAMP,
    preparing_at TIMESTAMP,
    ready_at TIMESTAMP,
    picked_up_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (status IN (
        'PENDING', 'CONFIRMED', 'PREPARING', 'READY', 
        'IN_DELIVERY', 'DELIVERED', 'CANCELLED', 'COMPLETED'
    )),
    CONSTRAINT valid_payment_method CHECK (payment_method IN (
        'credit_card', 'debit_card', 'cash', 'pix', 'wallet'
    ))
);

CREATE INDEX idx_orders_restaurant ON orders(restaurant_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_orders_number ON orders(order_number);
```

### 🛒 Tabela: `order_items`
```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL,
    menu_item_id UUID NOT NULL,
    
    -- Snapshot dos dados do item (para histórico)
    item_name VARCHAR(255) NOT NULL,
    item_description TEXT,
    unit_price DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    subtotal DECIMAL(10,2) NOT NULL,
    
    -- Customizações
    special_instructions TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT quantity_positive CHECK (quantity > 0),
    CONSTRAINT subtotal_check CHECK (subtotal = unit_price * quantity)
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
```

### 📊 Tabela: `order_status_history`
```sql
CREATE TABLE order_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL,
    previous_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    changed_by VARCHAR(100), -- 'system', 'restaurant', 'courier', 'customer'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_status_history_order ON order_status_history(order_id);
```

---

## 3. DELIVERY SERVICE DATABASE

### 🚗 Tabela: `couriers`
```sql
CREATE TABLE couriers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    document_number VARCHAR(20) UNIQUE NOT NULL, -- CPF/CNPJ
    
    -- Informações do veículo
    vehicle_type VARCHAR(50) NOT NULL, -- 'bicycle', 'motorcycle', 'car'
    vehicle_plate VARCHAR(10),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_available BOOLEAN DEFAULT true,
    current_latitude DECIMAL(10,8),
    current_longitude DECIMAL(11,8),
    
    -- Métricas
    total_deliveries INTEGER DEFAULT 0,
    rating DECIMAL(2,1) DEFAULT 5.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT rating_range CHECK (rating >= 0 AND rating <= 5),
    CONSTRAINT vehicle_type_valid CHECK (vehicle_type IN (
        'bicycle', 'motorcycle', 'car', 'scooter'
    ))
);

CREATE INDEX idx_couriers_available ON couriers(is_available);
CREATE INDEX idx_couriers_active ON couriers(is_active);
```

### 🚚 Tabela: `deliveries`
```sql
CREATE TABLE deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID UNIQUE NOT NULL,
    courier_id UUID,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    
    -- Endereços
    pickup_address VARCHAR(500) NOT NULL,
    pickup_latitude DECIMAL(10,8),
    pickup_longitude DECIMAL(11,8),
    
    delivery_address VARCHAR(500) NOT NULL,
    delivery_latitude DECIMAL(10,8),
    delivery_longitude DECIMAL(11,8),
    
    -- Distância e tempo
    estimated_distance DECIMAL(10,2), -- em km
    estimated_time INTEGER, -- em minutos
    actual_distance DECIMAL(10,2),
    actual_time INTEGER,
    
    -- Timestamps
    assigned_at TIMESTAMP,
    picked_up_at TIMESTAMP,
    in_transit_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Informações adicionais
    delivery_fee DECIMAL(10,2) NOT NULL,
    courier_earnings DECIMAL(10,2),
    notes TEXT,
    proof_of_delivery_url VARCHAR(500), -- foto da entrega
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE SET NULL,
    CONSTRAINT valid_status CHECK (status IN (
        'PENDING', 'ASSIGNED', 'PICKED_UP', 'IN_TRANSIT', 
        'DELIVERED', 'CANCELLED', 'FAILED'
    ))
);

CREATE INDEX idx_deliveries_order ON deliveries(order_id);
CREATE INDEX idx_deliveries_courier ON deliveries(courier_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
CREATE INDEX idx_deliveries_created ON deliveries(created_at);
```

### 📍 Tabela: `delivery_tracking`
```sql
CREATE TABLE delivery_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    accuracy DECIMAL(10,2), -- precisão em metros
    speed DECIMAL(10,2), -- velocidade em km/h
    bearing DECIMAL(5,2), -- direção em graus
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE
);

CREATE INDEX idx_tracking_delivery ON delivery_tracking(delivery_id);
CREATE INDEX idx_tracking_created ON delivery_tracking(created_at);
```

### ⭐ Tabela: `delivery_ratings`
```sql
CREATE TABLE delivery_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID UNIQUE NOT NULL,
    courier_id UUID NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE,
    FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE CASCADE,
    CONSTRAINT rating_range CHECK (rating >= 1 AND rating <= 5)
);

CREATE INDEX idx_ratings_courier ON delivery_ratings(courier_id);
```

---

## 4. NOTIFICATION SERVICE DATABASE

### 📧 Tabela: `notifications`
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificação
    event_id UUID UNIQUE NOT NULL, -- correlation com evento Kafka
    event_type VARCHAR(100) NOT NULL,
    
    -- Destinatário
    recipient_type VARCHAR(50) NOT NULL, -- 'customer', 'restaurant', 'courier'
    recipient_id UUID NOT NULL,
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(20),
    recipient_name VARCHAR(255),
    
    -- Conteúdo
    channel VARCHAR(50) NOT NULL, -- 'email', 'sms', 'push', 'whatsapp'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    template_name VARCHAR(100),
    
    -- Dados contextuais
    order_id UUID,
    restaurant_id UUID,
    delivery_id UUID,
    metadata JSONB, -- dados adicionais do evento
    
    -- Status de envio
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    failed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_channel CHECK (channel IN (
        'email', 'sms', 'push', 'whatsapp', 'in_app'
    )),
    CONSTRAINT valid_status CHECK (status IN (
        'PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED', 'CANCELLED'
    )),
    CONSTRAINT valid_recipient CHECK (recipient_type IN (
        'customer', 'restaurant', 'courier', 'admin'
    ))
);

CREATE INDEX idx_notifications_event ON notifications(event_id);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_id);
CREATE INDEX idx_notifications_order ON notifications(order_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created ON notifications(created_at);
CREATE INDEX idx_notifications_channel ON notifications(channel);
```

### 📋 Tabela: `notification_templates`
```sql
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    
    -- Conteúdo do template
    title_template VARCHAR(255) NOT NULL,
    body_template TEXT NOT NULL,
    
    -- Variáveis disponíveis (para documentação)
    available_variables TEXT[],
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_templates_event ON notification_templates(event_type);
```

### 📊 Tabela: `notification_preferences`
```sql
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    user_type VARCHAR(50) NOT NULL, -- 'customer', 'restaurant', 'courier'
    
    -- Preferências por canal
    email_enabled BOOLEAN DEFAULT true,
    sms_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    whatsapp_enabled BOOLEAN DEFAULT false,
    
    -- Preferências por tipo de evento
    order_updates BOOLEAN DEFAULT true,
    promotional BOOLEAN DEFAULT true,
    marketing BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (user_id, user_type)
);

CREATE INDEX idx_preferences_user ON notification_preferences(user_id);
```

---

## 📊 RESUMO DE RELACIONAMENTOS

### Cross-Service References (via eventos Kafka)
```
restaurant_id → Usado em Order Service
order_id → Usado em Delivery Service e Notification Service
courier_id → Usado em Delivery Service
customer_id → Usado em Order Service
```

### Totais por Serviço
- **Restaurant Service**: 3 tabelas, ~15 campos principais
- **Order Service**: 3 tabelas, ~50 campos principais
- **Delivery Service**: 5 tabelas, ~45 campos principais
- **Notification Service**: 3 tabelas, ~25 campos principais

**Total**: 14 tabelas, ~135 campos

---

## 🔑 Principais Constraints e Validações

### Restaurant Service
- ✅ Rating entre 0-5
- ✅ Preços positivos
- ✅ Dias da semana 0-6
- ✅ Cascade delete em menu items

### Order Service
- ✅ Status válidos (máquina de estados)
- ✅ Métodos de pagamento válidos
- ✅ Subtotal = preço × quantidade
- ✅ Histórico de mudanças de status

### Delivery Service
- ✅ Tipos de veículo válidos
- ✅ Rating entre 0-5
- ✅ Status de entrega válidos
- ✅ Tracking com timestamps

### Notification Service
- ✅ Canais válidos
- ✅ Status de envio válidos
- ✅ Tipos de destinatários válidos
- ✅ Retry com contador

---

## 💾 Estratégia de Cache Redis

### Restaurant Service
```
Key: restaurant:{id}
TTL: 15 minutos
Invalida: ao atualizar restaurante

Key: restaurant:{id}:menu
TTL: 15 minutos
Invalida: ao atualizar itens do menu

Key: restaurants:active
TTL: 5 minutos
```

### Order Service
```
Key: order:{id}
TTL: 1 hora
Invalida: ao mudar status

Key: customer:{id}:orders
TTL: 30 minutos
Invalida: ao criar novo pedido
```

### Delivery Service
```
Key: courier:{id}:location
TTL: 30 segundos
Atualiza: tempo real

Key: delivery:{id}
TTL: 1 hora
Invalida: ao mudar status
```