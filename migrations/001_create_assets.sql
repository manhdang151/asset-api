CREATE TABLE IF NOT EXISTS assets (
    id         UUID PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    type       VARCHAR(50)  NOT NULL,
    status     VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_type   ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
CREATE INDEX IF NOT EXISTS idx_assets_tags ON assets USING GIN (tags);