..
 This work is licensed under a Creative Commons Attribution 4.0
 International License.

=============
Release Notes
=============
..      ===========================
..      * * *    FRANKFURT    * * *
..      ===========================

Abstract
========

This document provides the release notes for the Frankfurt release.

Summary
=======


Release Data
============


+--------------------------------------+--------------------------------------+
| **OOF Project**                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Docker images**                    |   optf-osdf 2.0.2                    |
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | 6.0.0 frankfurt                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2020-05-07 (TBD)                     |
|                                      |                                      |
+--------------------------------------+--------------------------------------+


New features
------------



Known Limitations, Issues and Workarounds
=========================================

System Limitations
------------------


Known Vulnerabilities
---------------------


Workarounds
-----------


Security Notes
--------------


References
==========

For more information on the ONAP Frankfurt release, please see:

#. `ONAP Home Page`_
#. `ONAP Documentation`_
#. `ONAP Release Downloads`_
#. `ONAP Wiki Page`_


.. _`ONAP Home Page`: https://www.onap.org
.. _`ONAP Wiki Page`: https://wiki.onap.org
.. _`ONAP Documentation`: https://docs.onap.org
.. _`ONAP Release Downloads`: https://git.onap.org

Quick Links:
    - `OOF project page`_
    - `Passing Badge information for OOF`_


Version: 5.0.1
--------------

:Release Date: 2019-09-30 (El Alto Release)

The El Alto release is the fourth release for ONAP Optimization Framework (OOF).

Artifacts released:

optf-has:1.3.3
optf-osdf:1.3.4
optf-cmso:2.1.1

**New Features**

While no new features were added in the release, the following Stories were delivered as enhancements.

    * [OPTFRA-415] Automation on policy model uploading
    * [OPTFRA-427] CMSO - Schedule a workflow in SO and track status to completion

* Platform Maturity Level 1
    * ~65.1+ unit test coverage


**Bug Fixes**

The El Alto release for OOF fixed the following Bugs.

    * [OPTFRA-579] Json error in homing solution
    * [OPTFRA-521] oof-has-api exposes plain text HTTP endpoint using port 30275
    * [OPTFRA-522] oof-osdf exposes plain text HTTP endpoint using port 30248
    * [OPTFRA-577] Need for "ReadWriteMany" access on storage when deploying on Kubernetes?
    * [OPTFRA-517] Clean up optf/cmso in integration/csit for Dublin
    * [OPTFRA-486] Support "identifiers" field as a list of values
    * [OPTFRA-403] OOF CMSO Service kubernetes resources allocation is not done
    * [OPTFRA-526] OOF pods not running
    * [OPTFRA-409] Template example : purpose to be explained
    * [OPTFRA-593] OOF-CSMO healthcheck is failing in Master


**Known Issues**

    * [OPTFRA-576] optf-has-master-csit-has is testing Dublin image
    * [OPTFRA-596] CMSO - Sonar and CSIT jobs failing
    * [OPTFRA-608] Error in Homing with multiple policies

**Security Notes**

*Fixed Security Issues*

    * [OJSI-122] In default deployment OPTFRA (oof-osdf) exposes HTTP port 30248 outside of cluster.
    * [OPTFRA-521] oof-has-api exposes plain text HTTP endpoint using port 30275
    * [OPTFRA-522] oof-osdf exposes plain text HTTP endpoint using port 30248
    * [OPTFRA-455] CMSO - Mitigate License Threat tomcat-embed-core

*Known Security Issues*

    * [OPTFRA-481] Fix Vulnerability with spring-data-jpa package
    * [OPTFRA-431] Fix Vulnerability with spring-security-web package

*Known Vulnerabilities in Used Modules*

**Upgrade Notes**


**Deprecation Notes**


**Other**


Version: 4.0.0
--------------

:Release Date: 2019-06-06 (Dublin Release)

**New Features**

The Dublin release is the third release for ONAP Optimization Framework (OOF).

A summary of features includes

* Support SON (PCI/ANR) optimization using OSDF
* Implement encryption for OSDF internal and external communication

* Platform Maturity Level 1
    * ~65.1+ unit test coverage

The Dublin release for OOF delivered the following Epics.

    * [OPTFRA-426]	Track the changes to CMSO to support change management schedule optimization
    * [OPTFRA-424]	Extend OOF to support traffic distribution optimization
    * [OPTFRA-422]	Move OOF projects' CSIT to run on OOM
    * [OPTFRA-276]	Implementing a POC for 5G SON Optimization
    * [OPTFRA-270]	This epic captures stories related to maintaining current S3P levels of the project as new functional requirements are supported


**Bug Fixes**

* The full list of implemented user stories and epics is available on `DUBLIN RELEASE <https://jira.onap.org/projects/OPTFRA/versions/10463>`_

**Known Issues**



**Security Notes**

*Fixed Security Issues*

*Known Security Issues*

    * [`OJSI-122 <https://jira.onap.org/browse/OJSI-122>`_] In default deployment OPTFRA (oof-osdf) exposes HTTP port 30248 outside of cluster.

*Known Vulnerabilities in Used Modules*

OPTFRA osdf code has been formally scanned during build time using NexusIQ and no Critical vulnerability was found.
The OPTF open Critical security vulnerabilities and their risk assessment have been documented as part of the `project <https://wiki.onap.org/pages/viewpage.action?pageId=64005463>`_.

Quick Links:
    - `OPTFRA project page <https://wiki.onap.org/display/DW/Optimization+Framework+Project>`_
    - `Passing Badge information for OPTFRA <https://bestpractices.coreinfrastructure.org/en/projects/1720>`_
    - `Project Vulnerability Review Table for OPTF <https://wiki.onap.org/pages/viewpage.action?pageId=64005463>`_

**Upgrade Notes**

None.

**Deprecation Notes**

None.

**Other**

None

Version: 3.0.1
--------------

:Release Date: 2019-01-31 (Casablanca Maintenance Release)

The following items were deployed with the Casablanca Maintenance Release:


**New Features**

None.

**Bug Fixes**

* [OPTFRA-401] - 	Need flavor id while launching vm.



Version: 3.0.0
--------------

:Release Date: 2018-11-30 (Casablanca Release)

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
The OPTF open Critical security vulnerabilities and their risk assessment have been documented as part of the `project <https://wiki.onap.org/pages/viewpage.action?pageId=43385924>`_.

Quick Links:
    - `OPTFRA project page <https://wiki.onap.org/display/DW/Optimization+Framework+Project>`_
    - `Passing Badge information for OPTFRA <https://bestpractices.coreinfrastructure.org/en/projects/1720>`_
    - `Project Vulnerability Review Table for OPTF <https://wiki.onap.org/pages/viewpage.action?pageId=43385924>`_

**Upgrade Notes**

None.

**Deprecation Notes**

None.

**Other**

None

Version: 2.0.0
--------------

:Release Date: 2018-06-07

**New Features**


The ONAP Optimization Framework (OOF) is new in Beijing. A summary of features includes:

* Baseline HAS functionality
    * support for VCPE use case
    * support for HPA (Hardware Platform Awareness)
* Integration with OOF OSDF, SO, Policy, AAI, and Multi-Cloud
* Platform Maturity Level 1
    * ~50%+ unit test coverage

The Beijing release for OOF delivered the following Epics.

    * [OPTFRA-2] - On-boarding and Stabilization of the OOF seed code
    * [OPTFRA-6] - Integrate OOF with other ONAP components
    * [OPTFRA-7] - Integration with R2 Use Cases [HPA, Change Management, Scaling]
    * [OPTFRA-20] - OOF Adapters for Retrieving and Resolving Policies
    * [OPTFRA-21] - OOF Packaging
    * [OPTFRA-28] - OOF Adapters for Beijing Release (Policy, SDC, A&AI, Multi Cloud, etc.)
    * [OPTFRA-29] - Policies and Specifications for Initial Applications [Change Management, HPA]
    * [OPTFRA-32] - Platform Maturity Requirements for Beijing release
    * [OPTFRA-33] - OOF Support for HPA
    * [OPTFRA-105] - All Documentation Related User Stories and Tasks


**Bug Fixes**

None. Initial release R2 Beijing. No previous versions

**Known Issues**

None.

**Security Notes**

OPTFRA code has been formally scanned during build time using NexusIQ and no Critical vulnerability was found.

Quick Links:
    - `OPTFRA project page <https://wiki.onap.org/display/DW/Optimization+Framework+Project>`_
    - `Passing Badge information for OPTFRA <https://bestpractices.coreinfrastructure.org/en/projects/1720>`_

**Upgrade Notes**

None. Initial release R2 Beijing. No previous versions

**Deprecation Notes**

None. Initial release R2 Beijing. No previous versions

**Other**

None
