-- ============================================================================
-- Cold Chain Integrity & Spoilage Risk Analytics
-- STEP 3: MYSQL DATABASE SCHEMA
-- ============================================================================
-- Run this first to create the database and all tables with proper primary
-- keys and foreign-key relationships. Load order matters because of FKs:
--   products, suppliers, routes  -->  shipments  -->  temperature_readings
-- ============================================================================

CREATE DATABASE IF NOT EXISTS cold_chain_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cold_chain_analytics;

DROP TABLE IF EXISTS temperature_readings;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS routes;

-- ----------------------------------------------------------------------------
-- PRODUCTS
-- ----------------------------------------------------------------------------
CREATE TABLE products (
    product_id           VARCHAR(10)     NOT NULL,
    product_name         VARCHAR(100)    NOT NULL,
    product_category     VARCHAR(50)     NOT NULL,
    required_temp_min    DECIMAL(5,2)    NOT NULL,
    required_temp_max    DECIMAL(5,2)    NOT NULL,
    unit_cost            DECIMAL(10,2)   NOT NULL,
    shelf_life_hours     INT             NOT NULL,
    PRIMARY KEY (product_id),
    CHECK (required_temp_max >= required_temp_min)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- SUPPLIERS
-- ----------------------------------------------------------------------------
CREATE TABLE suppliers (
    supplier_id           VARCHAR(10)    NOT NULL,
    supplier_name         VARCHAR(100)   NOT NULL,
    supplier_country       VARCHAR(50)   NOT NULL,
    supplier_rating        DECIMAL(3,1)  NULL,
    contract_start_year    INT           NULL,
    PRIMARY KEY (supplier_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- ROUTES
-- ----------------------------------------------------------------------------
CREATE TABLE routes (
    route_id         VARCHAR(10)    NOT NULL,
    origin           VARCHAR(100)   NOT NULL,
    destination      VARCHAR(100)   NOT NULL,
    distance_km       INT           NOT NULL,
    transport_mode    VARCHAR(30)   NOT NULL,
    PRIMARY KEY (route_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- SHIPMENTS (fact table)
-- ----------------------------------------------------------------------------
CREATE TABLE shipments (
    shipment_id                  VARCHAR(10)     NOT NULL,
    product_id                   VARCHAR(10)     NOT NULL,
    supplier_id                  VARCHAR(10)     NOT NULL,
    route_id                     VARCHAR(10)     NOT NULL,
    shipment_date                DATE            NOT NULL,
    expected_delivery_date       DATETIME        NOT NULL,
    actual_delivery_date         DATETIME        NULL,
    shipment_status               VARCHAR(20)    NOT NULL,
    transit_hours                 DECIMAL(6,1)   NOT NULL,
    quantity                      INT            NOT NULL,
    unit_cost                     DECIMAL(10,2)  NOT NULL,
    recorded_temperature          DECIMAL(5,1)   NOT NULL,
    required_temp_min             DECIMAL(5,2)   NOT NULL,
    required_temp_max             DECIMAL(5,2)   NOT NULL,
    deviation_c                   DECIMAL(5,1)   NOT NULL,
    temperature_excursion_flag     TINYINT(1)    NOT NULL,
    excursion_severity             VARCHAR(10)   NOT NULL,
    excursion_duration_hours       DECIMAL(6,1)  NOT NULL,
    delay_flag                     TINYINT(1)    NULL,
    delay_duration_hours           DECIMAL(6,1)  NULL,
    spoilage_risk_score             INT          NOT NULL,
    spoilage_risk_category           VARCHAR(20) NOT NULL,
    estimated_spoilage_qty           INT         NOT NULL,
    estimated_financial_loss         DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (shipment_id),
    CONSTRAINT fk_shipments_product  FOREIGN KEY (product_id)  REFERENCES products(product_id),
    CONSTRAINT fk_shipments_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    CONSTRAINT fk_shipments_route    FOREIGN KEY (route_id)    REFERENCES routes(route_id),
    INDEX idx_shipments_date (shipment_date),
    INDEX idx_shipments_risk (spoilage_risk_category),
    INDEX idx_shipments_status (shipment_status)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- TEMPERATURE READINGS (IoT sensor log, many-to-one with shipments)
-- ----------------------------------------------------------------------------
CREATE TABLE temperature_readings (
    reading_id           VARCHAR(10)    NOT NULL,
    shipment_id          VARCHAR(10)    NOT NULL,
    reading_timestamp    DATETIME       NULL,
    sensor_temperature   DECIMAL(6,1)   NULL,
    sensor_id            VARCHAR(10)    NOT NULL,
    PRIMARY KEY (reading_id),
    CONSTRAINT fk_readings_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id),
    INDEX idx_readings_shipment (shipment_id)
) ENGINE=InnoDB;
