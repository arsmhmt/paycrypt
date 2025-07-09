-- Add commission fields to clients table
ALTER TABLE clients ADD COLUMN deposit_commission NUMERIC(5,4) DEFAULT 0.035 NOT NULL;
ALTER TABLE clients ADD COLUMN withdrawal_commission NUMERIC(5,4) DEFAULT 0.015 NOT NULL;
ALTER TABLE clients ADD COLUMN deposit_commission_rate FLOAT DEFAULT 0.035 NOT NULL;
ALTER TABLE clients ADD COLUMN withdrawal_commission_rate FLOAT DEFAULT 0.015 NOT NULL;
ALTER TABLE clients ADD COLUMN balance NUMERIC(18,8) DEFAULT 0 NOT NULL;
