-- Packages
INSERT INTO packages (name, slug, description, is_active, is_default, price_monthly, price_yearly, sort_order, created_at, updated_at)
VALUES ('Starter Flat Rate', 'starter_flat_rate', 'Perfect for small businesses and startups', 1, 1, 9.99, 99.99, 1, datetime('now'), datetime('now'));

INSERT INTO packages (name, slug, description, is_active, is_default, price_monthly, price_yearly, sort_order, created_at, updated_at)
VALUES ('Business Flat Rate', 'business_flat_rate', 'Ideal for growing businesses', 1, 0, 29.99, 299.99, 2, datetime('now'), datetime('now'));

INSERT INTO packages (name, slug, description, is_active, is_default, price_monthly, price_yearly, sort_order, created_at, updated_at)
VALUES ('Enterprise Flat Rate', 'enterprise_flat_rate', 'For large businesses with high volume', 1, 0, 99.99, 999.99, 3, datetime('now'), datetime('now'));

-- Features
INSERT INTO features (name, description, display_name, is_parameterized, default_value, is_active, created_at, updated_at)
VALUES 
('max_wallets', 'Maximum number of wallets', 'Maximum Wallets', 1, '5', 1, datetime('now'), datetime('now')),
('api_access', 'API Access', 'API Access', 0, NULL, 1, datetime('now'), datetime('now')),
('priority_support', 'Priority Support', 'Priority Support', 0, NULL, 1, datetime('now'), datetime('now')),
('custom_checkout', 'Custom Checkout Page', 'Custom Checkout', 0, NULL, 1, datetime('now'), datetime('now')),
('multi_currency', 'Multi-Currency Support', 'Multi-Currency', 0, NULL, 1, datetime('now'), datetime('now'));

-- Assign features to packages
-- Starter package features
INSERT INTO package_features (package_id, feature_id, value, created_at, updated_at)
SELECT 
    (SELECT id FROM packages WHERE slug = 'starter_flat_rate') as package_id,
    id as feature_id,
    CASE 
        WHEN name = 'max_wallets' THEN '5'
        ELSE NULL
    END as value,
    datetime('now'),
    datetime('now')
FROM features
WHERE name IN ('max_wallets', 'api_access');

-- Business package features
INSERT INTO package_features (package_id, feature_id, value, created_at, updated_at)
SELECT 
    (SELECT id FROM packages WHERE slug = 'business_flat_rate') as package_id,
    id as feature_id,
    CASE 
        WHEN name = 'max_wallets' THEN '15'
        ELSE NULL
    END as value,
    datetime('now'),
    datetime('now')
FROM features
WHERE name IN ('max_wallets', 'api_access', 'priority_support', 'multi_currency');

-- Enterprise package features
INSERT INTO package_features (package_id, feature_id, value, created_at, updated_at)
SELECT 
    (SELECT id FROM packages WHERE slug = 'enterprise_flat_rate') as package_id,
    id as feature_id,
    CASE 
        WHEN name = 'max_wallets' THEN 'Unlimited'
        ELSE NULL
    END as value,
    datetime('now'),
    datetime('now')
FROM features;

-- Add coins
INSERT INTO coin_metadata (symbol, name, is_active, decimals, min_confirmations, created_at, updated_at)
VALUES 
('BTC', 'Bitcoin', 1, 8, 6, datetime('now'), datetime('now')),
('ETH', 'Ethereum', 1, 18, 12, datetime('now'), datetime('now')),
('USDT', 'Tether', 1, 6, 6, datetime('now'), datetime('now')),
('USDC', 'USD Coin', 1, 6, 6, datetime('now'), datetime('now')),
('BNB', 'Binance Coin', 1, 18, 12, datetime('now'), datetime('now')),
('XRP', 'Ripple', 1, 6, 6, datetime('now'), datetime('now')),
('SOL', 'Solana', 1, 9, 12, datetime('now'), datetime('now')),
('DOGE', 'Dogecoin', 1, 8, 6, datetime('now'), datetime('now')),
('TRX', 'TRON', 1, 6, 12, datetime('now'), datetime('now')),
('ADA', 'Cardano', 1, 6, 6, datetime('now'), datetime('now')),
('LTC', 'Litecoin', 1, 8, 6, datetime('now'), datetime('now')),
('AVAX', 'Avalanche', 1, 18, 6, datetime('now'), datetime('now')),
('MATIC', 'Polygon', 1, 18, 12, datetime('now'), datetime('now')),
('SHIB', 'Shiba Inu', 1, 18, 12, datetime('now'), datetime('now')),
('DOT', 'Polkadot', 1, 10, 6, datetime('now'), datetime('now')),
('LINK', 'Chainlink', 1, 18, 6, datetime('now'), datetime('now')),
('XLM', 'Stellar', 1, 7, 6, datetime('now'), datetime('now')),
('DAI', 'Dai', 1, 18, 6, datetime('now'), datetime('now')),
('ARB', 'Arbitrum', 1, 18, 6, datetime('now'), datetime('now')),
('OP', 'Optimism', 1, 18, 6, datetime('now'), datetime('now')),
('TON', 'Toncoin', 1, 9, 6, datetime('now'), datetime('now')),
('CRO', 'Cronos', 1, 8, 6, datetime('now'), datetime('now')),
('FTM', 'Fantom', 1, 18, 6, datetime('now'), datetime('now')),
('APE', 'ApeCoin', 1, 18, 6, datetime('now'), datetime('now')),
('BCH', 'Bitcoin Cash', 1, 8, 6, datetime('now'), datetime('now'));

-- Verify data
SELECT 'Packages:' as '';
SELECT * FROM packages;

SELECT '\nFeatures:' as '';
SELECT * FROM features;

SELECT '\nPackage Features:' as '';
SELECT p.name as package, f.name as feature, pf.value 
FROM package_features pf
JOIN packages p ON pf.package_id = p.id
JOIN features f ON pf.feature_id = f.id;

SELECT '\nCoins:' as '';
SELECT * FROM coin_metadata;