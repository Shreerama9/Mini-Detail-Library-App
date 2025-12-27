-- Data was provided in assignment 
-- seed data for details
INSERT INTO details (id, title, category, tags, description) VALUES
(1, 'External Wall – Slab Junction', 'Waterproofing', 
   ARRAY['wall', 'slab', 'waterproofing', 'external'], 
   'Waterproof membrane continuity at external wall and slab junction'),

(2, 'Window Sill Detail with Drip', 'Window', 
   ARRAY['window', 'sill', 'drip', 'external'], 
   'External window sill detail with drip groove'),

(3, 'Internal Wall – Floor Junction', 'Wall', 
   ARRAY['wall', 'floor', 'internal'], 
   'Junction detail between internal wall and finished floor');


-- seed data for detail_usage_rules
INSERT INTO detail_usage_rules (id, detail_id, host_element, adjacent_element, exposure) VALUES
(1, 1, 'External Wall', 'Slab', 'External'),
(2, 2, 'Window', 'External Wall', 'External'),
(3, 3, 'Internal Wall', 'Floor', 'Internal');




SELECT setval('details_id_seq', (SELECT MAX(id) FROM details));
SELECT setval('detail_usage_rules_id_seq', (SELECT MAX(id) FROM detail_usage_rules));
