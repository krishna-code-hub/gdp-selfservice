---
id: TEST-REF-001
title: CDP to GDP compute and storage mapping
summary: CDP equivalents in GDP for YARN, Spark, HDFS and Hive; migration differences.
component: platform
framework: migration
owner: platform-team
status: approved
reviewed: '2026-10-04'
version: Local retrieval test fixture v1; based on supplied CDP/GDP mapping
---
# CDP to GDP equivalents
Applicability: approved for local testing only, not production migration approval.
The mapping below is a subset of the repository owner's supplied CDP/GDP table.
Confirm actual releases and service availability before production use.

## Technology comparison
| CDP capability | GDP counterpart | Difference |
| --- | --- | --- |
| YARN compute | Kubernetes | Container scheduling replaces YARN resource management |
| Spark on YARN | Spark on Kubernetes | Processing engine remains Spark; deployment changes |
| HDFS / PowerScale | S3-compatible MinIO / Ceph | Object storage uses S3/S3A access |
| Hive tables / Parquet | Iceberg / Parquet | Table/catalog behavior changes |
| Hive Metastore | Iceberg REST Catalog | Catalog integration changes |
| Hive / Spark SQL | Trino / Spark SQL | Engine-specific SQL compatibility needs checking |

## Migration checks
Verify resource requests, storage paths, identities, catalog settings and SQL behavior.
Equivalence is not feature parity. Test data reads/writes and access controls before cutover.
