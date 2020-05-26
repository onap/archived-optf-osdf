..
 This work is licensed under a Creative Commons Attribution 4.0
 International License.

================
Upgrade Strategy
================

OSDF can be upgraded in place(remove and replace) or in a blue-green
strategy.

There is no need for database migration. Since, there is no database
being used by OSDF.

Supporting Facts
================

OSDF is a stateless component. It doesn't store any information in the
database. It holds on to the optimization request in memory only until
the optimization process is complete. The optimization is done either by
OSDF itself or other external components(such as HAS) are leveraged for
optimization.
