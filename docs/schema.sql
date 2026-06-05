CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    source_customer_id INTEGER,
    gender VARCHAR(20),
    owns_car BOOLEAN,
    owns_realty BOOLEAN,
    income_total NUMERIC(15,2),
    education_type VARCHAR(100),
    family_status VARCHAR(100),
    housing_type VARCHAR(100),
    occupation_type VARCHAR(100),
    cnt_children INTEGER,
    family_members INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loan_applications (
    application_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(customer_id),
    credit_amount NUMERIC(15,2),
    annuity_amount NUMERIC(15,2),
    goods_price NUMERIC(15,2),
    loan_type VARCHAR(50),
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50)
);

CREATE TABLE model_predictions (
    prediction_id UUID PRIMARY KEY,
    application_id UUID REFERENCES loan_applications(application_id),
    probability_default FLOAT,
    risk_category VARCHAR(50),
    model_version VARCHAR(50),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admin_users (
    admin_id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password_hash TEXT,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY,
    admin_id UUID REFERENCES admin_users(admin_id),
    action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE model_registry (
    model_id UUID PRIMARY KEY,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    roc_auc FLOAT,
    deployed BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
