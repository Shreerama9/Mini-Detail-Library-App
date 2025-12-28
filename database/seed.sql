INSERT INTO details (id, title, category, tags, description, source) VALUES
(1, 'External Wall – Slab Junction', 'Waterproofing', 
   ARRAY['wall', 'slab', 'waterproofing', 'external'], 
   'Waterproof membrane continuity at external wall and slab junction',
   'standard'),

(2, 'Window Sill Detail with Drip', 'Window', 
   ARRAY['window', 'sill', 'drip', 'external'], 
   'External window sill detail with drip groove',
   'standard'),

(3, 'Internal Wall – Floor Junction', 'Wall', 
   ARRAY['wall', 'floor', 'internal'], 
   'Junction detail between internal wall and finished floor',
   'standard'),

(4, 'Premium Roof Waterproofing Detail', 'Waterproofing',
   ARRAY['roof', 'waterproofing', 'premium', 'external'],
   'Advanced multi-layer roof waterproofing system with drainage mat',
   'premium'),

(5, 'Structural Glazing System', 'Window',
   ARRAY['glazing', 'structural', 'curtain wall', 'external'],
   'Frameless structural glazing system with silicone bonding',
   'premium');



INSERT INTO detail_usage_rules (id, detail_id, host_element, adjacent_element, exposure) VALUES
(1, 1, 'External Wall', 'Slab', 'External'),
(2, 2, 'Window', 'External Wall', 'External'),
(3, 3, 'Internal Wall', 'Floor', 'Internal'),
(4, 4, 'External Wall', 'Roof', 'External'),
(5, 5, 'Window', 'External Wall', 'External');



SELECT setval('details_id_seq', (SELECT MAX(id) FROM details));
SELECT setval('detail_usage_rules_id_seq', (SELECT MAX(id) FROM detail_usage_rules));
