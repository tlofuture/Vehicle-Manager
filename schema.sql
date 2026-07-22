-- Run this in the Supabase SQL Editor to set up your database.

-- Create Vehicles table
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_number TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    model_year INT,
    make TEXT,
    model TEXT,
    vin TEXT,
    odometer NUMERIC DEFAULT 0,
    odometer_unit TEXT DEFAULT 'Kilometres',
    color TEXT,
    driver TEXT,
    department TEXT,
    vehicle_type TEXT,
    plate_tag TEXT,
    renewal_date DATE,
    insurance_company TEXT,
    insurance_account TEXT,
    insurance_premium NUMERIC,
    insurance_due DATE,
    engine TEXT,
    transmission TEXT,
    tire_size TEXT,
    notes TEXT,
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Fuel Logs table
CREATE TABLE fuel_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    odometer NUMERIC,
    gallons NUMERIC,
    price_per_gallon NUMERIC,
    total_cost NUMERIC,
    fuel_type TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Service Schedule table
CREATE TABLE service_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    service_type TEXT NOT NULL,
    interval_miles INT,
    interval_months INT,
    last_service_date DATE,
    last_service_odometer NUMERIC,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Service Log table
CREATE TABLE service_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    service_date DATE NOT NULL,
    odometer NUMERIC,
    service_type TEXT,
    vendor TEXT,
    cost NUMERIC,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Parts table
CREATE TABLE parts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    part_number TEXT,
    quantity INT DEFAULT 0,
    unit_cost NUMERIC DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Personnel table
CREATE TABLE personnel (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    role TEXT,
    phone TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Vendors table
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
