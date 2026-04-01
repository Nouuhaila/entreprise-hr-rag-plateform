# Week 4 RAG Evaluation Report

- Queries: **7**
- Citation rate: **0.43**

## Latency
- End-to-end avg: **3674.21 ms**
- End-to-end p95: **4322.93 ms**
- Pipeline avg (reported): **0.00 ms**
- Pipeline p95 (reported): **0.00 ms**

## Checks
- Citation presence is checked heuristically (answer contains `[chunk_id]`).

## Results
| Question | Filters | Top-K | Total (ms) | Pipeline (ms) | Citations? | #Sources | Status |
|---|---|---:|---:|---:|:---:|---:|---|
| What are the GDPR data retention requirements for employee records? | {'region': 'EU'} | 5 | 1719.78 | 0.00 | ❌ | 5 | OK |
| What disciplinary procedures apply before termination? | {'department': 'HR'} | 5 | 261.79 | 0.00 | ❌ | 1 | OK |
| What are the anti-discrimination policies for hiring? | {'category': 'Policy'} | 5 | 351.18 | 0.00 | ❌ | 1 | OK |
| What are the whistleblower protection obligations? | {'department': 'Compliance'} | 5 | 455.99 | 0.00 | ✅ | 5 | OK |
| What are compliance obligations? | {'department': 'Compliance'} | 5 | 693.23 | 0.00 | ✅ | 5 | OK |
| What is the notice period for termination? | {'department': 'HR'} | 3 | 4322.93 | 0.00 | ❌ | 1 | OK |
| What are compliance obligations? | {'department': 'Compliance'} | 5 | 17914.60 | 0.00 | ✅ | 5 | OK |

## Answers (preview)

### What are the GDPR data retention requirements for employee records?
- Filters: `{'region': 'EU'}` | Top-K: `5`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'eurlex_0000003_chunk_0001', 'doc_id': 'eurlex_0000003', 'score': 0.2756}, {'chunk_id': 'eurlex_0000004_chunk_0002', 'doc_id': 'eurlex_0000004', 'score': 0.2261}, {'chunk_id': 'eurlex_0000000_chunk_0000', 'doc_id': 'eurlex_0000000', 'score': 0.226}]`

### What disciplinary procedures apply before termination?
- Filters: `{'department': 'HR'}` | Top-K: `5`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'policyqa_0000000_chunk_0000', 'doc_id': 'policyqa_0000000', 'score': 0.0637}]`

### What are the anti-discrimination policies for hiring?
- Filters: `{'category': 'Policy'}` | Top-K: `5`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'policyqa_0000000_chunk_0000', 'doc_id': 'policyqa_0000000', 'score': 0.0515}]`

### What are the whistleblower protection obligations?
- Filters: `{'department': 'Compliance'}` | Top-K: `5`
- Answer: Based on the provided context, I found the following information related to whistleblower protection obligations: The context does not explicitly mention whistleblower protection obligations. However, it does mention confidentiality requirements set forth in § 403.14 [pile_of_law_0000000_chunk_0043]. This suggests that the POTW (Publicly Owned Treatment Works) has some obligations related to prote
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.4296}, {'chunk_id': 'pile_of_law_0000000_chunk_0043', 'doc_id': 'pile_of_law_0000000', 'score': 0.4131}, {'chunk_id': 'pile_of_law_0000000_chunk_0071', 'doc_id': 'pile_of_law_0000000', 'score': 0.4007}]`

### What are compliance obligations?
- Filters: `{'department': 'Compliance'}` | Top-K: `5`
- Answer: Based on the provided context, compliance obligations include: * Obtaining remedies for noncompliance by Industrial Users with Pretreatment Standards and Requirements, including injunctive relief and civil or criminal penalties [pile_of_law_0000000_chunk_0040]. * Complying with confidentiality requirements set forth in § 403.14 [pile_of_law_0000000_chunk_0040]. * Developing and implementing proced
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.5297}, {'chunk_id': 'pile_of_law_0000000_chunk_0047', 'doc_id': 'pile_of_law_0000000', 'score': 0.5201}, {'chunk_id': 'pile_of_law_0000000_chunk_0043', 'doc_id': 'pile_of_law_0000000', 'score': 0.5174}]`

### What is the notice period for termination?
- Filters: `{'department': 'HR'}` | Top-K: `3`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'policyqa_0000000_chunk_0000', 'doc_id': 'policyqa_0000000', 'score': 0.0316}]`

### What are compliance obligations?
- Filters: `{'department': 'Compliance'}` | Top-K: `5`
- Answer: Based on the provided context, compliance obligations include: * Obtaining remedies for noncompliance by Industrial Users with Pretreatment Standards and Requirements [pile_of_law_0000000_chunk_0040] * Enforcing Pretreatment requirements through remedies, including inspections, entry, or monitoring activities, and reporting requirements [pile_of_law_0000000_chunk_0040] * Complying with confidentia
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.5297}, {'chunk_id': 'pile_of_law_0000000_chunk_0047', 'doc_id': 'pile_of_law_0000000', 'score': 0.5201}, {'chunk_id': 'pile_of_law_0000000_chunk_0043', 'doc_id': 'pile_of_law_0000000', 'score': 0.5174}]`
