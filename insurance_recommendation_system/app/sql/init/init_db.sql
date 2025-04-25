-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users(is_verified);

-- Create user_info table
CREATE TABLE IF NOT EXISTS user_info (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,

    first_name TEXT,
    last_name TEXT,
    age INT,
    gender TEXT,
    occupation TEXT,
    income DOUBLE PRECISION,
    marital_status TEXT,
    has_children BOOLEAN default false,
    has_vehicle BOOLEAN default false,
    has_home BOOLEAN default false,
    has_medical_conditions BOOLEAN default false,
    travel_frequency TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_age ON user_info(age);
CREATE INDEX IF NOT EXISTS idx_users_id ON user_info(user_id);
CREATE INDEX IF NOT EXISTS idx_users_gender ON user_info(gender);

-- Create insurance_categories table
CREATE TABLE IF NOT EXISTS insurance_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insurance_categories_name ON insurance_categories(name);

-- Create insurances table
CREATE TABLE IF NOT EXISTS insurances (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    premium DECIMAL(10, 2) NOT NULL,
    coverage DECIMAL(15, 2) NOT NULL,
    duration INTEGER,
    category_id INTEGER REFERENCES insurance_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insurances_name ON insurances(name);
CREATE INDEX IF NOT EXISTS idx_insurance_coverage ON insurances(coverage);
CREATE INDEX IF NOT EXISTS idx_insurances_created_at ON insurances(created_at);
CREATE INDEX IF NOT EXISTS idx_insurances_category_id ON insurances(category_id);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    insurance_id INTEGER REFERENCES insurances(id) ON DELETE CASCADE,
    score DECIMAL(3, 2) NOT NULL,
    is_viewed BOOLEAN DEFAULT FALSE,
    is_purchased BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, insurance_id)
);

CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_insurance_id ON recommendations(insurance_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_score ON recommendations(score);
CREATE INDEX IF NOT EXISTS idx_recommendations_is_viewed ON recommendations(is_viewed);
CREATE INDEX IF NOT EXISTS idx_recommendations_is_purchased ON recommendations(is_purchased);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON recommendations(created_at);

-- function to create user_info row
CREATE OR REPLACE FUNCTION create_user_info()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_info (user_id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- trigger to create user_info row after user is created
CREATE TRIGGER trg_create_user_info
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_user_info();

-- Insert default insurance categories
INSERT INTO insurance_categories (name, description) VALUES
    ('Life Insurance', 'Insurance that pays out a sum of money either on the death of the insured person or after a set period.'),
    ('Health Insurance', 'Insurance coverage that pays for medical and surgical expenses incurred by the insured.'),
    ('Auto Insurance', 'Insurance for cars, trucks, motorcycles, and other road vehicles.'),
    ('Home Insurance', 'Insurance that covers losses and damages to an individual''s house and assets in the home.'),
    ('Travel Insurance', 'Insurance that covers the costs and losses associated with traveling.')
ON CONFLICT DO NOTHING;

-- Insert sample insurance products
INSERT INTO insurances (name, description, premium, coverage, duration, category_id) VALUES
    ('Term Life Insurance', 'Provides coverage at a fixed rate of payments for a limited period of time.', 5000, 1000000, 120, 1),
    ('Whole Life Insurance', 'Permanent life insurance that remains in force for the insured''s entire lifetime.', 12000, 2000000, NULL, 1),
    ('Individual Health Insurance', 'Health insurance coverage for an individual that covers medical expenses.', 8000, 500000, 12, 2),
    ('Family Health Insurance', 'Health insurance coverage for the entire family under a single premium.', 15000, 1000000, 12, 2),
    ('Comprehensive Auto Insurance', 'Covers damages to your vehicle along with third-party liability.', 6000, 300000, 12, 3),
    ('Third-Party Auto Insurance', 'Covers damages to third-party vehicles and property.', 3000, 150000, 12, 3),
    ('Basic Home Insurance', 'Covers basic damages to your home due to fire, theft, etc.', 4000, 500000, 12, 4),
    ('Premium Home Insurance', 'Comprehensive coverage for your home including natural disasters.', 9000, 1500000, 12, 4),
    ('Single Trip Travel Insurance', 'Coverage for a single trip including medical emergencies and trip cancellation.', 1500, 100000, 1, 5),
    ('Annual Multi-Trip Travel Insurance', 'Coverage for multiple trips within a year.', 5000, 300000, 12, 5)
ON CONFLICT DO NOTHING;


