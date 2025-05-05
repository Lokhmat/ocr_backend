ALTER TABLE app.images
ADD workload TEXT NOT NULL CHECK (workload IN ('on_premise', 'cloud')) DEFAULT 'cloud';
