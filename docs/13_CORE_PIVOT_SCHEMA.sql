-- 🧠 CORE PIVOT: FORUMS & FUNCTIONAL IDENTITIES
-- Description: Decoupling from LinkedIn. New focus on Content Ingestion (Forums) and Analysis (Executive Reports).
-- Date: 2026-01-24

-- 1️⃣ TABLA: forums
-- Fuente de contenido externo (foros, comunidades, threads)
CREATE TABLE IF NOT EXISTS forums (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  platform TEXT NOT NULL, -- reddit, discourse, custom, etc
  base_url TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 2️⃣ TABLA: forum_threads
-- Hilos específicos a analizar
CREATE TABLE IF NOT EXISTS forum_threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  forum_id UUID REFERENCES forums(id),
  title TEXT NOT NULL,
  thread_url TEXT NOT NULL,
  extracted_at TIMESTAMP WITH TIME ZONE,
  status TEXT DEFAULT 'pending', -- pending | processed | ignored
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 3️⃣ TABLA: functional_identities
-- 👉 CLAVE: Esto reemplaza LinkedIn mientras tanto.
CREATE TABLE IF NOT EXISTS functional_identities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  role TEXT NOT NULL, -- founder, dev, marketer, executive
  tone TEXT, -- analytical, bold, neutral
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 4️⃣ TABLA: reported_urls
-- URLs detectadas como relevantes (posts, artículos, hilos)
CREATE TABLE IF NOT EXISTS reported_urls (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL, -- forum, manual, crawler
  url TEXT NOT NULL,
  title TEXT,
  relevance_score NUMERIC,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 5️⃣ TABLA: executive_reports
-- 👉 Salida ejecutiva (esto es lo que importa)
CREATE TABLE IF NOT EXISTS executive_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  identity_id UUID REFERENCES functional_identities(id),
  summary TEXT NOT NULL,
  recommendations TEXT,
  source_count INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS (Security Best Practice)
ALTER TABLE forums ENABLE ROW LEVEL SECURITY;
ALTER TABLE forum_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE functional_identities ENABLE ROW LEVEL SECURITY;
ALTER TABLE reported_urls ENABLE ROW LEVEL SECURITY;
ALTER TABLE executive_reports ENABLE ROW LEVEL SECURITY;

-- Create simple policies (Open for MVP/Auth users)
CREATE POLICY "Enable read access for authenticated users" ON forums FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Enable read access for authenticated users" ON forum_threads FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Enable read access for authenticated users" ON functional_identities FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Enable read access for authenticated users" ON reported_urls FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Enable read access for authenticated users" ON executive_reports FOR SELECT USING (auth.role() = 'authenticated');

-- Enable write for authenticated users (MVP)
CREATE POLICY "Enable insert for authenticated users" ON forums FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable insert for authenticated users" ON forum_threads FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable insert for authenticated users" ON functional_identities FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable insert for authenticated users" ON reported_urls FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable insert for authenticated users" ON executive_reports FOR INSERT WITH CHECK (auth.role() = 'authenticated');
