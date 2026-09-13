# Tri-Lane cost proxy: Claude billable per merged commit

Windows: pre `2026-08-25` to `2026-09-04`; post `2026-09-04` to `2026-09-14`.

**Proxy, not the rule.** Work mix differs between windows. The post window includes review and documentation sessions. Commits are counted on every branch (--all) and include lane and salvage commits. Claude billable includes cache creation, which scales with context size. This is not the pre-registered rule; only the manual arm can return a verdict.

Two commit denominators, because the answer depends on it: *branch* counts first-parent commits on the checked-out branch (changes that landed); *all* counts every branch, which after adoption includes one commit per lane run and every salvage branch, so it flatters the post window.

| Repository | Claude billable, pre | Claude billable, post | Per branch commit, pre → post | Change | Per commit (all branches), pre → post | Change |
|---|---:|---:|---|---:|---|---:|
| statledger | 24,807,766 | 59,313,447 | 354,397 (70) → 429,808 (138) | +21% | 112,763 (220) → 108,039 (549) | -4% |
| iep-and-thrive | 657,614 | 33,731,821 | — (0) → 602,354 (56) | — | — (0) → 301,177 (112) | — |
| cannabis-retail-platform | 52,842,348 | 35,713,773 | 412,831 (128) → — (0) | — | 116,393 (454) → 476,184 (75) | +309% |
| Finality | 0 | 5,399,916 | — (0) → 257,139 (21) | — | 0 (2) → 91,524 (59) | — |
| cure-finops-watchdog | 2,216,743 | 2,945,629 | 554,186 (4) → 327,292 (9) | -41% | 277,093 (8) → 245,469 (12) | -11% |
| DistrictZero | 25,030,988 | 9,849,701 | 658,710 (38) → 579,394 (17) | -12% | 301,578 (83) → 223,857 (44) | -26% |
| initiated-recruiting | 84,202,628 | 39,389,617 | 1,137,873 (74) → 2,073,138 (19) | +82% | 673,621 (125) → 410,309 (96) | -39% |
| NationalLacrosseTourApp | 0 | 27,029,171 | 0 (30) → 1,126,215 (24) | — | 0 (152) → 355,647 (76) | — |
