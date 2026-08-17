-- VentureLab Database Schema
-- Hermes can write to these tables directly

-- Ideas table
CREATE TABLE IF NOT EXISTS ideas (
    id SERIAL PRIMARY KEY,
    idea_id VARCHAR(100) UNIQUE NOT NULL,
    idea TEXT NOT NULL,
    thesis TEXT,
    category VARCHAR(100),
    status VARCHAR(50) DEFAULT 'seeded',
    scores JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Research table
CREATE TABLE IF NOT EXISTS research (
    id SERIAL PRIMARY KEY,
    idea_id VARCHAR(100) REFERENCES ideas(idea_id),
    arxiv_results JSONB DEFAULT '[]',
    github_results JSONB DEFAULT '[]',
    competitors JSONB DEFAULT '[]',
    evidence JSONB DEFAULT '[]',
    researched_at TIMESTAMP DEFAULT NOW()
);

-- Evaluations table
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    idea_id VARCHAR(100) REFERENCES ideas(idea_id),
    novelty_score FLOAT,
    research_score FLOAT,
    feasibility_score FLOAT,
    overall_score FLOAT,
    verdict VARCHAR(50),
    evaluated_at TIMESTAMP DEFAULT NOW()
);

-- Hypotheses table
CREATE TABLE IF NOT EXISTS hypotheses (
    id SERIAL PRIMARY KEY,
    hypothesis TEXT NOT NULL,
    based_on VARCHAR(100)[],
    confidence FLOAT,
    test_plan TEXT,
    status VARCHAR(50) DEFAULT 'proposed',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50),
    title TEXT,
    content JSONB,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Competitors table
CREATE TABLE IF NOT EXISTS competitors (
    id SERIAL PRIMARY KEY,
    venture VARCHAR(100),
    player VARCHAR(200),
    relation VARCHAR(100),
    what_it_does TEXT,
    capability TEXT,
    business_model TEXT,
    strength TEXT,
    gap TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Evidence table
CREATE TABLE IF NOT EXISTS evidence (
    id SERIAL PRIMARY KEY,
    theme VARCHAR(200),
    finding TEXT,
    applies_to VARCHAR(200),
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Research papers table
CREATE TABLE IF NOT EXISTS research_papers (
    id SERIAL PRIMARY KEY,
    title TEXT,
    authors TEXT[],
    published DATE,
    relevant_venture VARCHAR(100),
    key_finding TEXT,
    product_implication TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- OSS projects table
CREATE TABLE IF NOT EXISTS oss_projects (
    id SERIAL PRIMARY KEY,
    repository VARCHAR(200),
    theme VARCHAR(200),
    what_it_provides TEXT,
    why_useful TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Roadmap table
CREATE TABLE IF NOT EXISTS roadmap (
    id SERIAL PRIMARY KEY,
    phase VARCHAR(100),
    focus TEXT,
    build_plan TEXT,
    exit_criterion TEXT,
    monetization TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas(category);
CREATE INDEX IF NOT EXISTS idx_research_idea_id ON research(idea_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_idea_id ON evaluations(idea_id);
CREATE INDEX IF NOT EXISTS idx_competitors_venture ON competitors(venture);
