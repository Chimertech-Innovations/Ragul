-- =====================================================================
-- RAGUL AI - SUPABASE / POSTGRESQL DATABASE SCHEMA
-- DAIRY FARM TELEMETRY, CCTV AI VISION, AND IOT SENSOR ARCHITECTURE
-- =====================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. FARMS TABLE
CREATE TABLE IF NOT EXISTS farms (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(150),
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    total_cameras INT DEFAULT 6,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. CCTV CAMERAS REGISTRY
CREATE TABLE IF NOT EXISTS cctv_cameras (
    camera_id VARCHAR(20) PRIMARY KEY,
    farm_id VARCHAR(50) REFERENCES farms(id) ON DELETE CASCADE,
    coverage_zone VARCHAR(150) NOT NULL,
    resolution VARCHAR(50) DEFAULT '4K / 30fps AI Stream',
    status VARCHAR(50) DEFAULT 'Online',
    installed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. WORKERS MASTER ROSTER
CREATE TABLE IF NOT EXISTS workers (
    worker_id VARCHAR(20) PRIMARY KEY,
    farm_id VARCHAR(50) REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    shift_hours VARCHAR(100),
    duties TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. CATTLE HERD MASTER ROSTER
CREATE TABLE IF NOT EXISTS cattle (
    cattle_id VARCHAR(20) PRIMARY KEY,
    farm_id VARCHAR(50) REFERENCES farms(id) ON DELETE CASCADE,
    rfid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    pen_group VARCHAR(50) NOT NULL, -- 'Pen 1', 'Pen 2'
    lactation_status VARCHAR(50) NOT NULL, -- 'Lactating', 'Heifer', 'Dry', 'Pregnant'
    breed VARCHAR(100) DEFAULT 'Jersey / HF Cross',
    parity INT DEFAULT 2,
    baseline_daily_yield_litres NUMERIC(5,2) DEFAULT 18.00,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. WORKER DAILY ATTENDANCE (CCTV CAM01 Gate Entry/Exit Vision Logs)
CREATE TABLE IF NOT EXISTS worker_attendance (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    worker_id VARCHAR(20) REFERENCES workers(worker_id) ON DELETE CASCADE,
    worker_name VARCHAR(100),
    status VARCHAR(30) NOT NULL, -- 'Present', 'Absent', 'On Leave'
    first_seen TIMESTAMPTZ, -- Check-in timestamp
    last_seen TIMESTAMPTZ,  -- Check-out timestamp
    detected_by VARCHAR(20) DEFAULT 'CAM01',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (date, worker_id)
);

-- 6. DAILY MILKING SESSIONS & HERD TOTALS
CREATE TABLE IF NOT EXISTS daily_milking_totals (
    date DATE PRIMARY KEY,
    morning_session_start TIMESTAMPTZ,
    evening_session_start TIMESTAMPTZ,
    total_milk_litres NUMERIC(7,2) NOT NULL,
    camera_id VARCHAR(20) DEFAULT 'CAM02',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. INDIVIDUAL COW DAILY MILK YIELD
CREATE TABLE IF NOT EXISTS cattle_milk_yields (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    cattle_id VARCHAR(20) REFERENCES cattle(cattle_id) ON DELETE CASCADE,
    yield_litres NUMERIC(5,2) NOT NULL,
    fat_percentage NUMERIC(4,2) DEFAULT 4.10,
    snf_percentage NUMERIC(4,2) DEFAULT 8.50,
    conductivity_ms NUMERIC(5,2) DEFAULT 5.20,
    somatic_cell_count INT DEFAULT 140000,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (date, cattle_id)
);

-- 8. FEEDING SESSIONS (CCTV CAM05 & Feed Scale IoT)
CREATE TABLE IF NOT EXISTS feeding_events (
    event_id VARCHAR(50) PRIMARY KEY,
    date DATE NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    worker_id VARCHAR(20) REFERENCES workers(worker_id),
    location VARCHAR(100) DEFAULT 'Feed alley',
    camera_id VARCHAR(20) DEFAULT 'CAM05',
    cattle_group VARCHAR(50) DEFAULT 'Pen 1',
    tmr_kg NUMERIC(6,2) NOT NULL,
    green_fodder_kg NUMERIC(6,2) NOT NULL,
    concentrate_kg NUMERIC(6,2) NOT NULL,
    camera_observation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. PEN CLEANING & HYGIENE EVENTS (CCTV CAM03 & CAM04 AI Dung Vision)
CREATE TABLE IF NOT EXISTS cleaning_events (
    event_id VARCHAR(50) PRIMARY KEY,
    date DATE NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    worker_id VARCHAR(20) REFERENCES workers(worker_id),
    camera_id VARCHAR(20) NOT NULL,
    area VARCHAR(50) NOT NULL, -- 'Pen 1', 'Pen 2'
    status VARCHAR(50) NOT NULL, -- 'Completed on time', 'Completed', 'Delayed'
    camera_observation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. CATTLE ACTIVITY & COLLAR SENSORS (Steps, Rest, Rumination)
CREATE TABLE IF NOT EXISTS cattle_activity (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    cattle_id VARCHAR(20) REFERENCES cattle(cattle_id) ON DELETE CASCADE,
    steps INT NOT NULL,
    rest_hours NUMERIC(4,2) NOT NULL,
    rumination_minutes INT NOT NULL,
    activity_status VARCHAR(30) DEFAULT 'Normal', -- 'Normal', 'Low', 'High'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (date, cattle_id)
);

-- 11. ENVIRONMENT & IOT SENSOR TELEMETRY
CREATE TABLE IF NOT EXISTS environment_iot (
    date DATE PRIMARY KEY,
    average_temperature_c NUMERIC(4,2) NOT NULL,
    average_humidity_percent NUMERIC(4,2) NOT NULL,
    water_consumption_litres NUMERIC(7,2) NOT NULL,
    feed_distributed_kg NUMERIC(7,2) NOT NULL,
    power_status VARCHAR(30) DEFAULT 'Normal',
    network_status VARCHAR(30) DEFAULT 'Online',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. CCTV CAMERA AI VISION EVENTS STREAM
CREATE TABLE IF NOT EXISTS cctv_camera_events (
    id BIGSERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    camera_id VARCHAR(20) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_description TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. FARM ALERTS (Mastitis, Estrus / Heat, Hygiene Delays, IoT Disconnects)
CREATE TABLE IF NOT EXISTS farm_alerts (
    alert_id VARCHAR(50) PRIMARY KEY,
    date DATE NOT NULL,
    type VARCHAR(100) NOT NULL,
    severity VARCHAR(30) NOT NULL, -- 'Low', 'Medium', 'High', 'Critical'
    cattle_id VARCHAR(20) REFERENCES cattle(cattle_id),
    source VARCHAR(100) NOT NULL, -- 'CCTV AI', 'Activity collar + CAM03', 'Inline mastitis sensor'
    details TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 14. DAILY FARM EXECUTIVE BRIEFINGS
CREATE TABLE IF NOT EXISTS daily_summaries (
    date DATE PRIMARY KEY,
    weekday VARCHAR(30) NOT NULL,
    summary_text TEXT NOT NULL,
    total_workers_present INT DEFAULT 5,
    total_milk_litres NUMERIC(7,2),
    total_water_litres NUMERIC(7,2),
    actionable_alerts_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------- PERFORMANCE INDICES FOR AI AGENT QUERIES -----------------
CREATE INDEX IF NOT EXISTS idx_worker_att_date ON worker_attendance(date);
CREATE INDEX IF NOT EXISTS idx_milk_yield_date ON cattle_milk_yields(date, cattle_id);
CREATE INDEX IF NOT EXISTS idx_feed_date ON feeding_events(date);
CREATE INDEX IF NOT EXISTS idx_clean_date ON cleaning_events(date);
CREATE INDEX IF NOT EXISTS idx_activity_date ON cattle_activity(date, cattle_id);
CREATE INDEX IF NOT EXISTS idx_alerts_date ON farm_alerts(date, severity);
CREATE INDEX IF NOT EXISTS idx_cctv_time ON cctv_camera_events(time);
