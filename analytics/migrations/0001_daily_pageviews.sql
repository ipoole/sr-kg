CREATE TABLE daily_pageviews (
    day TEXT NOT NULL,
    page TEXT NOT NULL CHECK (page IN ('home', 'atlas', 'guide')),
    views INTEGER NOT NULL CHECK (views > 0),
    PRIMARY KEY (day, page)
) WITHOUT ROWID;
