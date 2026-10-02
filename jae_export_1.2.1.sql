-- ============================================================
-- JAE-EXPORT v1.2.1
-- PostgreSQL Database Schema
-- ============================================================

CREATE SCHEMA IF NOT EXISTS jae_export;

SET search_path TO jae_export;

-- ============================================================
-- 1. 出口行业
-- ============================================================

CREATE TABLE export_industry (
    industry_id BIGSERIAL PRIMARY KEY,
    industry_code VARCHAR(20) NOT NULL UNIQUE,
    industry_name VARCHAR(100) NOT NULL,
    parent_code VARCHAR(20),
    industry_level SMALLINT NOT NULL DEFAULT 1,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. 指标
-- ============================================================

CREATE TABLE export_indicator (
    indicator_id BIGSERIAL PRIMARY KEY,
    indicator_code VARCHAR(20) NOT NULL UNIQUE,
    indicator_name VARCHAR(100) NOT NULL,
    indicator_type VARCHAR(30) NOT NULL,
    unit VARCHAR(50),
    direction SMALLINT NOT NULL DEFAULT 1,
    default_decay_days INTEGER NOT NULL DEFAULT 30,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_indicator_direction
        CHECK (direction IN (-1, 1))
);

-- ============================================================
-- 3. 行业指标权重
-- ============================================================

CREATE TABLE industry_indicator_weight (
    weight_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,
    indicator_id BIGINT NOT NULL,

    weight DECIMAL(8,5) NOT NULL,

    model_version VARCHAR(20) NOT NULL DEFAULT 'v1.2',
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to DATE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_weight_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT fk_weight_indicator
        FOREIGN KEY (indicator_id)
        REFERENCES export_indicator(indicator_id),

    CONSTRAINT chk_weight
        CHECK (weight >= 0 AND weight <= 100),

    CONSTRAINT uq_weight_version
        UNIQUE (
            industry_id,
            indicator_id,
            model_version
        )
);

-- ============================================================
-- 4. HS编码
-- ============================================================

CREATE TABLE hs_code (
    hs_id BIGSERIAL PRIMARY KEY,

    hs_code VARCHAR(10) NOT NULL UNIQUE,
    hs_version VARCHAR(20) NOT NULL,

    hs_level SMALLINT NOT NULL,

    hs_name_cn VARCHAR(300),
    hs_name_en VARCHAR(300),

    parent_hs_code VARCHAR(10),

    valid_from DATE,
    valid_to DATE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_hs_level
        CHECK (hs_level IN (2,4,6))
);

-- ============================================================
-- 5. 行业-HS映射
-- ============================================================

CREATE TABLE industry_hs_mapping (
    mapping_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,
    hs_id BIGINT NOT NULL,

    mapping_weight DECIMAL(8,5) NOT NULL,

    mapping_type VARCHAR(30) NOT NULL DEFAULT 'DIRECT',

    confidence DECIMAL(8,5) NOT NULL DEFAULT 1.0,

    source_id BIGINT,

    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to DATE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_mapping_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT fk_mapping_hs
        FOREIGN KEY (hs_id)
        REFERENCES hs_code(hs_id),

    CONSTRAINT chk_mapping_weight
        CHECK (
            mapping_weight >= 0
            AND mapping_weight <= 1
        ),

    CONSTRAINT chk_mapping_confidence
        CHECK (
            confidence >= 0
            AND confidence <= 1
        )
);

-- ============================================================
-- 6. 数据源
-- ============================================================

CREATE TABLE data_source (
    source_id BIGSERIAL PRIMARY KEY,

    source_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    organization VARCHAR(200),

    url TEXT,
    api_endpoint TEXT,

    frequency VARCHAR(30),

    reliability_score DECIMAL(8,5)
        NOT NULL DEFAULT 0.8,

    priority SMALLINT
        NOT NULL DEFAULT 50,

    active BOOLEAN
        NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 7. 原始出口数据
-- ============================================================

CREATE TABLE export_raw_data (
    raw_id BIGSERIAL PRIMARY KEY,

    source_id BIGINT NOT NULL,
    hs_id BIGINT NOT NULL,

    period DATE NOT NULL,

    country_code VARCHAR(10),

    export_value DECIMAL(20,4),
    currency VARCHAR(10) DEFAULT 'USD',

    quantity DECIMAL(20,6),
    quantity_unit VARCHAR(30),

    unit_price DECIMAL(20,8),

    yoy_value DECIMAL(12,6),
    yoy_quantity DECIMAL(12,6),
    yoy_price DECIMAL(12,6),

    data_date TIMESTAMP,

    ingested_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    raw_hash VARCHAR(128),

    quality_flag VARCHAR(30)
        DEFAULT 'NORMAL',

    CONSTRAINT fk_raw_source
        FOREIGN KEY (source_id)
        REFERENCES data_source(source_id),

    CONSTRAINT fk_raw_hs
        FOREIGN KEY (hs_id)
        REFERENCES hs_code(hs_id)
);

-- ============================================================
-- 8. 行业观察值
-- ============================================================

CREATE TABLE export_observation (
    observation_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,

    period DATE NOT NULL,

    export_value DECIMAL(20,4),
    export_quantity DECIMAL(20,6),

    quantity_unit VARCHAR(30),

    export_price DECIMAL(20,8),

    value_yoy DECIMAL(12,6),
    quantity_yoy DECIMAL(12,6),
    price_yoy DECIMAL(12,6),

    market_share DECIMAL(12,6),

    destination_count INTEGER,

    confidence DECIMAL(8,5),
    freshness_score DECIMAL(8,5),

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_observation_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT uq_observation
        UNIQUE(industry_id, period)
);

-- ============================================================
-- 9. 出口目的地
-- ============================================================

CREATE TABLE export_destination (
    destination_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,

    country_code VARCHAR(10) NOT NULL,
    region_code VARCHAR(30),

    period DATE NOT NULL,

    export_value DECIMAL(20,4),

    share DECIMAL(12,6),

    value_yoy DECIMAL(12,6),
    quantity_yoy DECIMAL(12,6),
    price_yoy DECIMAL(12,6),

    risk_score DECIMAL(8,5),

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_destination_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT uq_destination
        UNIQUE(
            industry_id,
            country_code,
            period
        )
);

-- ============================================================
-- 10. 标准化指标
-- ============================================================

CREATE TABLE normalized_indicator (
    normalized_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,
    indicator_id BIGINT NOT NULL,

    period DATE NOT NULL,

    raw_value DECIMAL(20,8),

    yoy_value DECIMAL(12,8),
    mom_value DECIMAL(12,8),

    z_score DECIMAL(12,8),
    percentile DECIMAL(8,6),

    normalized_score DECIMAL(8,5),

    direction_adjusted_score DECIMAL(8,5),

    freshness_score DECIMAL(8,5),
    confidence DECIMAL(8,5),

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_norm_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT fk_norm_indicator
        FOREIGN KEY (indicator_id)
        REFERENCES export_indicator(indicator_id),

    CONSTRAINT uq_normalized
        UNIQUE(
            industry_id,
            indicator_id,
            period
        )
);

-- ============================================================
-- 11. 贸易事件
-- ============================================================

CREATE TABLE export_event (
    event_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT,

    country_code VARCHAR(10),

    event_type VARCHAR(50) NOT NULL,

    event_date TIMESTAMP NOT NULL,

    severity DECIMAL(8,5),

    direction SMALLINT NOT NULL,

    impact_score DECIMAL(8,5),

    duration_days INTEGER,

    source_id BIGINT,

    description TEXT,

    confidence DECIMAL(8,5),

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_event_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT fk_event_source
        FOREIGN KEY (source_id)
        REFERENCES data_source(source_id),

    CONSTRAINT chk_event_direction
        CHECK(direction IN (-1,1))
);

-- ============================================================
-- 12. 行业评分
-- ============================================================

CREATE TABLE industry_score (
    score_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,

    period DATE NOT NULL,

    model_version VARCHAR(20) NOT NULL,

    demand_score DECIMAL(8,5),
    order_score DECIMAL(8,5),
    quantity_score DECIMAL(8,5),
    price_score DECIMAL(8,5),
    cycle_score DECIMAL(8,5),
    margin_score DECIMAL(8,5),
    competitiveness_score DECIMAL(8,5),
    technology_score DECIMAL(8,5),
    risk_score DECIMAL(8,5),
    sustainability_score DECIMAL(8,5),

    raw_score DECIMAL(8,5),

    event_adjustment DECIMAL(8,5),
    freshness_adjustment DECIMAL(8,5),
    confidence_adjustment DECIMAL(8,5),

    final_score DECIMAL(8,5),

    acceleration DECIMAL(8,5),

    rank INTEGER,

    confidence DECIMAL(8,5),

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_score_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT uq_score
        UNIQUE(
            industry_id,
            period,
            model_version
        )
);

-- ============================================================
-- 13. 行业信号
-- ============================================================

CREATE TABLE industry_signal (
    signal_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,

    period DATE NOT NULL,

    score_id BIGINT NOT NULL,

    regime VARCHAR(30),
    trend VARCHAR(30),

    acceleration_state VARCHAR(30),

    risk_level VARCHAR(30),

    signal_strength DECIMAL(8,5),

    confidence DECIMAL(8,5),

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_signal_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id),

    CONSTRAINT fk_signal_score
        FOREIGN KEY (score_id)
        REFERENCES industry_score(score_id),

    CONSTRAINT uq_signal
        UNIQUE(industry_id, period)
);

-- ============================================================
-- 14. 股票-行业映射
-- ============================================================

CREATE TABLE stock_industry_mapping (
    mapping_id BIGSERIAL PRIMARY KEY,

    industry_id BIGINT NOT NULL,

    stock_code VARCHAR(30) NOT NULL,
    market VARCHAR(20) NOT NULL,

    company_name VARCHAR(200) NOT NULL,

    exposure_weight DECIMAL(8,5),

    export_revenue_ratio DECIMAL(8,5),
    domestic_revenue_ratio DECIMAL(8,5),

    destination_exposure JSONB,

    confidence DECIMAL(8,5),

    valid_from DATE,
    valid_to DATE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_stock_industry
        FOREIGN KEY (industry_id)
        REFERENCES export_industry(industry_id)
);