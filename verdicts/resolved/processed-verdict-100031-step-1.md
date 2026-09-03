stop

STOP — a deposit defect, not a work defect. The plan content met the bar at walk 8 and is unchanged.

The Cycle Manifest was never emitted: the placeholder "*(emitted at BAR_MET)*" survived the freeze. So parse_manifest_stanza returned NO MANIFEST and the depositor fell back to gates._extract_plan_required_deposits, which yields only the two declared knowledge/ deposits and omits tools/mutation_check.py and tests/test_mutation_check.py.

With every parsed write under knowledge/, _assign_class's infra rule (project_is_infra AND not startswith "knowledge/") never fired. The plan was assigned app-feature, which auto-clears, and dispatched without the shop-infra human release act (RULINGS fork 4). The collision check also ran on 2 of 4 writes — no live collision, in-flight was zero, but the check was blind.

CEO ruled stop and re-deposit. It will be re-deposited with the manifest emitted, the write set complete, and class: shop-infra declared.
