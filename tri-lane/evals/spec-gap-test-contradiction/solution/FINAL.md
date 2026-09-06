Stopping before implementing: the spec and the visible tests contradict each other on the empty case.

CONSTRAINTS say an empty input list must raise ValueError. tests/test_visible.py::test_empty_list_returns_empty asserts that dedupe_emails([]) returns []. Both cannot hold, and I am told not to modify tests/. The caller-bug rationale suggests the constraint is intended, but the test may reflect a newer decision; that is for the architect.

Please resolve which behaviour is intended and I will implement.
