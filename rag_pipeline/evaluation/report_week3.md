# Week 3 RAG Evaluation Report

- Queries: **3**
- Citation rate: **0.67**

## Latency
- End-to-end avg: **1430.35 ms**
- End-to-end p95: **1156.40 ms**
- Pipeline avg (reported): **0.00 ms**
- Pipeline p95 (reported): **0.00 ms**

## Checks
- Citation presence is checked heuristically (answer contains `[chunk_id]`).

## Results
| Question | Filters | Top-K | Total (ms) | Pipeline (ms) | Citations? | #Sources | Status |
|---|---|---:|---:|---:|:---:|---:|---|
| What are compliance obligations? | {'department': 'Compliance'} | 5 | 2804.69 | 0.00 |  | 5 | OK |
| What is the notice period for termination? | {'department': 'HR'} | 5 | 329.96 | 0.00 |  | 1 | OK |
| Which documents mention regulatory requirements? | {'department': 'Compliance'} | 5 | 1156.40 | 0.00 | | 5 | OK |

## Answers (preview)

### What are compliance obligations?
- Filters: `{'department': 'Compliance'}` | Top-K: `5`
- Answer: Compliance obligations refer to the requirements that must be met by a Publicly Owned Treatment Works (POTW) and Industrial Users to ensure compliance with Pretreatment Standards and Requirements. A POTW must: * Obtain remedies for noncompliance by Industrial Users with Pretreatment Standards and Requirements [pile_of_law_0000000_chunk_0040] * Comply with the confidentiality requirements set forth
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.5297}, {'chunk_id': 'pile_of_law_0000000_chunk_0047', 'doc_id': 'pile_of_law_0000000', 'score': 0.5201}, {'chunk_id': 'pile_of_law_0000000_chunk_0043', 'doc_id': 'pile_of_law_0000000', 'score': 0.5174}]`

### What is the notice period for termination?
- Filters: `{'department': 'HR'}` | Top-K: `5`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'policyqa_0000000_chunk_0000', 'doc_id': 'policyqa_0000000', 'score': 0.0316}]`

### Which documents mention regulatory requirements?
- Filters: `{'department': 'Compliance'}` | Top-K: `5`
- Answer: Based on the provided documents, the following regulatory requirements are mentioned: 1. The Control Authority may require more detailed reporting of flows [pile_of_law_0000000_chunk_0055]. 2. Industrial Users for which EPA or the authorized state, tribe, or territory is the Control Authority must submit reports electronically by December 21, 2020 [pile_of_law_0000000_chunk_0055]. 3. Prior to Dece
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0055', 'doc_id': 'pile_of_law_0000000', 'score': 0.5444}, {'chunk_id': 'pile_of_law_0000000_chunk_0065', 'doc_id': 'pile_of_law_0000000', 'score': 0.5401}, {'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.5365}]`
