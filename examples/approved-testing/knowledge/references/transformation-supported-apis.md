---
id: TEST-REF-002
title: Transformation SQL and PySpark DataFrame support
summary: Test framework accepts SQL and PySpark DataFrame transformations, with submission and output-contract requirements.
component: transformation
framework: capabilities
owner: framework-team
status: approved
reviewed: '2026-10-04'
version: Local retrieval test fixture v1; simulated framework contract
---
# Transformation supported APIs
Applicability: approved local test scenario only. This defines a simulated
framework contract; it does not establish API support in the real GDP deployment.

## Supported behavior in this test scenario
Both SQL transformations and PySpark DataFrame operations are supported.
SQL suits declarative transformations; DataFrames suit programmatic compositions.
Both must follow the framework's input/output, identity and data-quality contracts.

## Usage illustration
The following expressions illustrate the APIs, not GDP submission commands:
```python
sql_result = spark.sql("SELECT customer_id FROM input_view")
dataframe_result = input_df.select("customer_id")
```
Use the test framework's documented submission interface. Direct arbitrary Spark
submission and third-party package installation are not implied by this contract.

## Production answer boundary
Disclose the test-only scope. Obtain the real framework's supported versions,
entry points and dependency restrictions before answering a production support question.
