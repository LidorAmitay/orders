-- ============================================================
-- Order Service - Initial Database Schema
-- Phase 1: Minimal Orders Table
-- ============================================================
-- This script creates the orders table for the Order Service.
-- It is executed automatically when the PostgreSQL container
-- starts for the first time (via /docker-entrypoint-initdb.d/).
--
-- Schema matches the minimal Phase 1 requirements:
-- - Supports basic order creation with user_id, product_id, quantity
-- - Default status is 'created'
-- - Timestamps track when orders are created
-- ============================================================

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'created',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create an index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);

-- Create an index on status for filtering orders by status
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

