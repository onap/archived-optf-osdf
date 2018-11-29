..
 This work is licensed under a Creative Commons Attribution 4.0
 International License.

=============
Release Notes
=============


Version: 1.2.4
--------------

:Release Date: 2018-11-30

**New Features**

The Casablanca release is the second release for ONAP Optimization Framework (OOF).

A summary of features includes

* Homing enhancements for improving service deployability
    * Discovering and reusing shared resources when processing multiple homing requests in parallel
    * Considering Latency Reduction (in addition to geographical distances) for homing optimization
    * Enhanced capacity checks during VNF homing
    * Asynchronous communication between HAS components
* OOF Casablanca S3P Usability enhancement
    * Adherence to ONAP API Common Versioning Strategy (CVS) Proposal
    * Move all internal and external facing APIs to Swagger 2.0
* OOF Casablanca S3P Performance enhancements
    * Creating a plan for performance improvements based on the baseline measured metrics
* OOF development platform hardening
    * Deployment scripts
    * Fix Build Docker image script for supporting multiple versions
    * Fix OOM, HEAT deployment scripts (versioning)
    * CSIT functional tests for each repo
    * CI Jobs for different streams (Beijing, master etc)
    * Clean up nexus binaries and maven versioning
* Integrate OOF with Certificate and Secret Management Service (CSM)
* Support SON (PCI) optimization using OSDF

* Platform Maturity Level 1
    * ~65.1+ unit test coverage
    
The Casablanca release for OOF delivered the following Epics.

    * [OPTFRA-273] - Epic Name: OOF Casablanca S3P Manageability enhancement
    * [OPTFRA-270] - Maintain current S3P levels
    * [OPTFRA-271] - OOF Casablanca S3P Security enhancement
    * [OPTFRA-267] - OOF - HPA Enhancements
    * [OPTFRA-276] - Implementing a POC for 5G SON Optimization


**Bug Fixes**

* The full list of implemented user stories and epics is available on `CASABLANCA RELEASE <https://jira.onap.org/projects/OPTFRA/versions/10445>`_

**Known Issues**

  * [OPTFRA-223] - 	On boarding and testing AAF certificates for OSDF.
  * [OPTFRA-293] - 	Implement encryption for all OSDF internal and external communication
  * [OPTFRA-329] - 	role based access control for OSDF-Policy interface

**Security Notes**

OPTFRA osdf code has been formally scanned during build time using NexusIQ and no Critical vulnerability was found.

Quick Links:
    - `OPTFRA project page <https://wiki.onap.org/display/DW/Optimization+Framework+Project>`_
 	
    - `Passing Badge information for OPTFRA <https://bestpractices.coreinfrastructure.org/en/projects/1720>`_

**Upgrade Notes**

None.

**Deprecation Notes**

None.

**Other**

None
