CREATE TABLE IF NOT EXISTS project (
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entry (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	project INTEGER NOT NULL,
	start_time TEXT NOT NULL,
	start_offset INTEGER NOT NULL,
	stop_time TEXT NOT NULL,
	stop_offset INTEGER NOT NULL,
	comments TEXT,
	FOREIGN KEY(project) REFERENCES project(id) ON DELETE CASCADE
);
-- select count(*) as nb, project.name from entry
-- inner join project on entry.project=project.id
-- group by project order by nb desc;
