---
id: REF-003
title: CDP to GDP technology equivalence evidence
summary: CDP equivalent tech stacks in GDP; required verified source-to-target migration mapping.
component: platform
framework: migration
owner: platform-team
status: approved
reviewed: '2026-10-04'
version: "CDP 7.1.9 → GDP platform release 2026.10"
---
# CDP to GDP technology equivalence
Applicability: CDP to GDP pproved migration mapping. 


## Required mapping

# CDP → GDP Technology Stack Mapping

## 1. Technology Stack Comparison

| Capability | CDP – Current State | GDP – Target State | Key Change |
|---|---|---|---|
| **Platform Architecture** | Cloudera Data Platform (CDP 7.x) | Open-source based Data Lakehouse | Vendor platform → Engineering-driven composable platform |
| **Compute Platform** | YARN | Kubernetes | YARN resource management → Container-native compute |
| **Batch Processing** | Apache Spark 3.x on YARN | Apache Spark 3.5+ on Kubernetes | Spark retained; execution platform modernized |
| **Storage** | HDFS / Dell PowerScale | S3-compatible Object Storage (MinIO / Ceph) | File-system storage → Object storage |
| **Storage Access Protocol** | HDFS | S3 / S3A | HDFS APIs → S3 protocol |
| **Table Format** | Hive Tables / Parquet | Apache Iceberg / Parquet | Hive-centric tables → Open lakehouse tables |
| **Metadata Catalog** | Hive Metastore | Iceberg REST Catalog | HMS-dependent → Open REST-based catalog |
| **SQL / Interactive Query** | Hive / Spark SQL | Trino / Spark SQL | Hive-centric SQL → Distributed interactive SQL |
| **High-Performance Analytics** | Primarily Spark/Hive | StarRocks / Dremio / Trino | Specialized engines available based on workload |
| **Streaming Processing** | Spark-based / existing streaming patterns | Apache Flink | Dedicated stream-processing engine |
| **Workflow Orchestration** | Existing schedulers / custom frameworks | Apache Airflow | Custom orchestration → Standardized workflow orchestration |
| **Resource Scheduling** | YARN Scheduler | Kubernetes + YuniKorn | Hadoop scheduling → Kubernetes-native scheduling |
| **Job Submission** | Spark submit / custom frameworks | GDP Gateway → Kubernetes | Direct/custom submission → Standardized compute control plane |
| **Authorization** | Apache Ranger | Apache Ranger | Policy-based authorization retained and integrated with GDP |
| **Authentication** | Kerberos-centric | Enterprise Identity / OIDC / OAuth where applicable | Hadoop identity model → Modern identity integration |
| **Encryption at Rest** | HDFS TDE / storage encryption | Object-store SSE-KMS + Iceberg encryption capabilities | HDFS encryption → Object/lakehouse-native encryption |
| **Key Management** | Enterprise KMS | Enterprise KMS / HSM integration | Centralized key management retained |
| **Metadata & Discovery** | CDP/Hive metadata ecosystem | DataHub + Enterprise Metadata Management | Platform metadata → Enterprise discovery and governance |
| **Data Lineage** | Existing CDP/framework lineage | DataHub + framework-generated lineage | Platform-specific → Framework-driven open lineage |
| **Data Quality** | Application/custom implementation | Standardized metadata-driven DQ framework | Application-specific → Built-in reusable capability |
| **Notebook / Data Science** | CDP tooling / application-specific | JupyterHub on Kubernetes | Vendor tooling → Open-source self-service workbench |
| **Visualization / BI Exploration** | Existing enterprise tools | Apache Superset + enterprise BI | Adds open self-service analytics |
| **Framework Model** | Multiple custom application frameworks | Standardized declarative frameworks | Diverse frameworks → Common engineering standards |
| **Ingestion** | Custom / application-specific ingestion | Metadata-driven standardized ingestion framework | Application-specific → Reusable ingestion pipelines |
| **Transformation** | Spark/Hive custom frameworks | Standardized Spark/Iceberg transformation framework | Custom patterns → Standardized declarative processing |
| **Deployment Model** | Cluster-centric | Kubernetes / containerized | Long-running clusters → Container-native workloads |
| **Multi-tenancy** | Hadoop/YARN queues & platform controls | Domain-isolated K8s + storage + centralized control plane | Shared cluster model → Explicit fault/resource isolation |
| **Observability** | CDP/platform monitoring | Kubernetes + Spark + framework-level observability | Vendor monitoring → Open, end-to-end observability |
| **Infrastructure Provisioning** | Platform/vendor-centric | Infrastructure-as-Code / GitOps automation | Operational provisioning → Engineering automation |
| **Application Onboarding** | Manual/custom onboarding | Automated self-service onboarding | Ticket/process-driven → Automation-first |

## Answer boundary
Do not infer GDP technologies from generic cloud products or error-guide mentions.
