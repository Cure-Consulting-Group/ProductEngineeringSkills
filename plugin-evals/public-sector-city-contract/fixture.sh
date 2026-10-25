#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). A fictional city's standard consultant agreement,
# in the 00-source/extracted/ layout the skill's auto-context expects, with the clauses the skill
# triages: "directly or indirectly" indemnity + duty to defend, contradictory IP language, 5-day
# termination for convenience, non-appropriation, and a cyber policy naming the City as
# additional insured.
set -euo pipefail
mkdir -p 00-source/extracted
cat > 00-source/extracted/city-contract.txt <<'__FIXTURE_EOF__'
CITY OF WESTBROOK — STANDARD CONSULTANT AGREEMENT (Form CA-7, rev. 2024)
Project: Resident Benefits Eligibility Portal. Term: three (3) years from the Effective Date,
with two (2) one-year renewal options exercisable by the City in its sole discretion.

ARTICLE FOURTH — INDEMNIFICATION
The Consultant shall defend, indemnify and hold harmless the City, its officers, agents and
employees from and against any and all claims, suits, losses, damages, costs and expenses,
including attorneys' fees, arising directly or indirectly out of this Agreement or the services
performed hereunder.

ARTICLE FIFTH — OWNERSHIP OF WORK PRODUCT
All deliverables, records and recorded data produced under this Agreement are works made for
hire and shall be the sole property of the City. Notwithstanding the foregoing, the Consultant
retains title to software tools and methods that it developed prior to this Agreement.

ARTICLE SIXTH — TERMINATION
The City may terminate this Agreement for its convenience upon five (5) days' written notice.
Upon such termination the Consultant shall be paid only for services rendered to the date of
termination, in an amount determined by the Corporation Counsel, whose determination is final.

ARTICLE SEVENTH — APPROPRIATION OF FUNDS
The City's obligations hereunder are subject to annual appropriation by the Common Council. If
funds are not appropriated for any fiscal year, the City may terminate this Agreement or
renegotiate rates upon release of the proposed budget, without penalty.

ARTICLE EIGHTH — PAYMENT
Invoices are payable net forty-five (45) days after the City's written acceptance of the
deliverable. Acceptance of final payment constitutes a release of all claims by the Consultant.

ARTICLE NINTH — INSURANCE
Before beginning work the Consultant shall maintain, with carriers rated A- or better by A.M. Best:
(a) Commercial General Liability $1,000,000 per occurrence / $2,000,000 aggregate;
(b) Professional Liability $3,000,000 per claim;
(c) Cyber Liability $2,000,000, naming the City of Westbrook as an additional insured on a
    primary and non-contributory basis;
(d) Workers' Compensation and Disability as required by State law.

ARTICLE TENTH — GENERAL
The Consultant shall comply with the City's non-discrimination, EEO and non-collusion
requirements and all applicable laws. The Consultant may not assign this Agreement or
subcontract any portion of the work without the City's prior written consent.
__FIXTURE_EOF__
