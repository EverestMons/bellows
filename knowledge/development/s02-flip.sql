BEGIN IMMEDIATE;
.output /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/schema02-2026-08-12/outside-range-ids.txt
SELECT id||'|'||category||'|'||status||'|'||COALESCE(route,'')||'|'||COALESCE(status_updated_at,'')||'|'||COALESCE(status_updated_by,'') FROM lesson_proposals WHERE id <= 332 AND id != 330 ORDER BY id;
.output stdout
UPDATE lesson_proposals SET status='implemented', status_updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'), status_updated_by='ceo' WHERE id = 330 AND status='accepted';
SELECT 'CHANGES='||changes();
SELECT 'GLOBOK='||COUNT(*) FROM lesson_proposals WHERE id = 330 AND status_updated_at GLOB '20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z' AND status_updated_at NOT IN ('2026-08-12T17:12:07Z');
COMMIT;
