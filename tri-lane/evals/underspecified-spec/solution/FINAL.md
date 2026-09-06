Stopping before implementing: the spec is inconsistent and incomplete.

1. Contradiction: INTERFACES says a negative qty returns 0, while CONSTRAINTS says a negative qty must raise ValueError. These cannot both hold; the caller-bug rationale suggests ValueError, but that is a decision for the architect.
2. Missing rule: the rounding of the discounted amount is not specified (round half up, floor, or banker's). The visible test expects 899 for 899.1, which is consistent with floor or round-half-up but the spec does not say which, and they differ for .5 cases.

Please resolve both and I will implement.
