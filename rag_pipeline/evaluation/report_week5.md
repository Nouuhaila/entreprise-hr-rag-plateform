# Week 5 RAG Evaluation Report

- Total queries: **15**
- Citation rate: **0.13** (2/15)
- Score threshold triggers: **3** (queries answered without LLM)
- Total question tokens: **139** (~9.3 avg/query)

## Latency (pipeline)
- Avg: **10666.27 ms**
- P95: **21602.31 ms**

## Baseline Comparison
| Week | Queries | Citation Rate | Avg Latency |
|------|---------|--------------|-------------|
| Week 3 | 3 | 0.67 | 1430 ms |
| Week 4 | 7 | 0.43 | 3674 ms |
| Week 5 | 15 | 0.13 | 10666 ms |

## Results by Category
| Category | Queries | Citation Rate | Avg Latency (ms) |
|----------|---------|--------------|------------------|
| ambiguous | 3 | 0.33 | 10904 |
| complex_compliance | 3 | 0.33 | 2725 |
| edge_case | 3 | 0.00 | 18669 |
| multi_doc | 3 | 0.00 | 19679 |
| simple_policy | 3 | 0.00 | 1353 |

## Detailed Results
| Question | Category | Filters | Top-K | Pipeline (ms) | Citations? | #Sources | Threshold? |
|---|---|---|---:|---:|:---:|---:|:---:|
| What is the maximum number of vacation days an emp | simple_policy | {} | 5 | 3599 | ❌ | 5 |  |
| What are the rules for remote work? | simple_policy | {'department': 'HR'} | 5 | 274 | ❌ | 0 | ⚡ |
| What documents govern employee leave policy? | simple_policy | {'category': 'Policy'} | 5 | 187 | ❌ | 0 | ⚡ |
| What are all the compliance obligations under EU r | complex_compliance | {'region': 'EU'} | 5 | 498 | ❌ | 5 |  |
| What are compliance obligations? | complex_compliance | {'department': 'Compliance'} | 5 | 947 | ✅ | 5 |  |
| What whistleblower protections are required by law | complex_compliance | {'department': 'Compliance'} | 5 | 6730 | ❌ | 5 |  |
| Which laws and policies together govern employee t | multi_doc | {} | 5 | 18654 | ❌ | 5 |  |
| How do EU regulations and internal HR policies ali | multi_doc | {'region': 'EU'} | 5 | 21697 | ❌ | 5 |  |
| What are the regulatory and internal requirements  | multi_doc | {} | 5 | 18686 | ❌ | 5 |  |
| What are employee rights? | ambiguous | {} | 5 | 17658 | ❌ | 5 |  |
| What should I do? | ambiguous | {} | 5 | 173 | ❌ | 0 | ⚡ |
| Tell me about policies. | ambiguous | {} | 5 | 14883 | ✅ | 5 |  |
| What is the policy for employees hired after Decem | edge_case | {} | 5 | 21602 | ❌ | 5 |  |
| What are the requirements for a company with zero  | edge_case | {} | 5 | 18640 | ❌ | 5 |  |
| Summarize all 10000 compliance documents. | edge_case | {} | 3 | 15766 | ❌ | 3 |  |

## Answers (preview)

### [simple_policy] What is the maximum number of vacation days an employee can take?
- Filters: `{}` | Top-K: `5` | Tokens: `13`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_1192', 'doc_id': 'pile_of_law_0000000', 'score': 0.3656}, {'chunk_id': 'pile_of_law_0000000_chunk_0296', 'doc_id': 'pile_of_law_0000000', 'score': 0.3377}, {'chunk_id': 'pile_of_law_0000000_chunk_0158', 'doc_id': 'pile_of_law_0000000', 'score': 0.3322}]`

### [simple_policy] What are the rules for remote work?
- Filters: `{'department': 'HR'}` | Top-K: `5` | Tokens: `8`
- **Score threshold triggered** — answered without LLM call
- Answer: I don't know based on the provided documents.
- Top sources: `[]`

### [simple_policy] What documents govern employee leave policy?
- Filters: `{'category': 'Policy'}` | Top-K: `5` | Tokens: `7`
- **Score threshold triggered** — answered without LLM call
- Answer: I don't know based on the provided documents.
- Top sources: `[]`

### [complex_compliance] What are all the compliance obligations under EU regulations?
- Filters: `{'region': 'EU'}` | Top-K: `5` | Tokens: `10`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'eurlex_0000002_chunk_0000', 'doc_id': 'eurlex_0000002', 'score': 0.521}, {'chunk_id': 'eurlex_0000000_chunk_0002', 'doc_id': 'eurlex_0000000', 'score': 0.4967}, {'chunk_id': 'eurlex_0000001_chunk_0000', 'doc_id': 'eurlex_0000001', 'score': 0.4376}]`

### [complex_compliance] What are compliance obligations?
- Filters: `{'department': 'Compliance'}` | Top-K: `5` | Tokens: `5`
- Answer: Compliance obligations include: - Obtaining remedies for noncompliance by Industrial Users with Pretreatment Standards and Requirements, including injunctive relief and civil or criminal penalties [pile_of_law_0000000_chunk_0040]. - Complying with confidentiality requirements set forth in § 403.14 [pile_of_law_0000000_chunk_0040]. - Developing and implementing procedures to ensure compliance with 
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.5297}, {'chunk_id': 'pile_of_law_0000000_chunk_0047', 'doc_id': 'pile_of_law_0000000', 'score': 0.5201}, {'chunk_id': 'pile_of_law_0000000_chunk_0043', 'doc_id': 'pile_of_law_0000000', 'score': 0.5174}]`

### [complex_compliance] What whistleblower protections are required by law?
- Filters: `{'department': 'Compliance'}` | Top-K: `5` | Tokens: `8`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.3927}, {'chunk_id': 'pile_of_law_0000000_chunk_0038', 'doc_id': 'pile_of_law_0000000', 'score': 0.3551}, {'chunk_id': 'pile_of_law_0000000_chunk_0043', 'doc_id': 'pile_of_law_0000000', 'score': 0.354}]`

### [multi_doc] Which laws and policies together govern employee termination?
- Filters: `{}` | Top-K: `5` | Tokens: `9`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_1258', 'doc_id': 'pile_of_law_0000000', 'score': 0.4423}, {'chunk_id': 'pile_of_law_0000000_chunk_0019', 'doc_id': 'pile_of_law_0000000', 'score': 0.4112}, {'chunk_id': 'pile_of_law_0000000_chunk_0035', 'doc_id': 'pile_of_law_0000000', 'score': 0.3962}]`

### [multi_doc] How do EU regulations and internal HR policies align on data retention?
- Filters: `{'region': 'EU'}` | Top-K: `5` | Tokens: `13`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'eurlex_0000000_chunk_0000', 'doc_id': 'eurlex_0000000', 'score': 0.3836}, {'chunk_id': 'eurlex_0000002_chunk_0000', 'doc_id': 'eurlex_0000002', 'score': 0.3704}, {'chunk_id': 'eurlex_0000003_chunk_0000', 'doc_id': 'eurlex_0000003', 'score': 0.3403}]`

### [multi_doc] What are the regulatory and internal requirements for anti-discrimination in hiring?
- Filters: `{}` | Top-K: `5` | Tokens: `14`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_1258', 'doc_id': 'pile_of_law_0000000', 'score': 0.4239}, {'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.3568}, {'chunk_id': 'pile_of_law_0000000_chunk_0041', 'doc_id': 'pile_of_law_0000000', 'score': 0.3431}]`

### [ambiguous] What are employee rights?
- Filters: `{}` | Top-K: `5` | Tokens: `5`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0062', 'doc_id': 'pile_of_law_0000000', 'score': 0.4819}, {'chunk_id': 'pile_of_law_0000000_chunk_1258', 'doc_id': 'pile_of_law_0000000', 'score': 0.4366}, {'chunk_id': 'pile_of_law_0000000_chunk_1271', 'doc_id': 'pile_of_law_0000000', 'score': 0.4094}]`

### [ambiguous] What should I do?
- Filters: `{}` | Top-K: `5` | Tokens: `5`
- **Score threshold triggered** — answered without LLM call
- Answer: I don't know based on the provided documents.
- Top sources: `[]`

### [ambiguous] Tell me about policies.
- Filters: `{}` | Top-K: `5` | Tokens: `5`
- Answer: Based on the provided context, I can tell you about policies related to regulations. According to Article 9 of the Directive, Member States shall bring into force the laws, regulations or administrative provisions necessary to comply with this Directive not later than 1 January 1980 [eurlex_0000000_chunk_0002]. POTWs must develop and enforce specific limits to implement the prohibitions listed in 
- Top sources: `[{'chunk_id': 'eurlex_0000000_chunk_0002', 'doc_id': 'eurlex_0000000', 'score': 0.351}, {'chunk_id': 'pile_of_law_0000000_chunk_0019', 'doc_id': 'pile_of_law_0000000', 'score': 0.3469}, {'chunk_id': 'pile_of_law_0000000_chunk_0038', 'doc_id': 'pile_of_law_0000000', 'score': 0.3348}]`

### [edge_case] What is the policy for employees hired after December 31, 2099?
- Filters: `{}` | Top-K: `5` | Tokens: `16`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_0054', 'doc_id': 'pile_of_law_0000000', 'score': 0.4908}, {'chunk_id': 'pile_of_law_0000000_chunk_1271', 'doc_id': 'pile_of_law_0000000', 'score': 0.4573}, {'chunk_id': 'pile_of_law_0000000_chunk_0061', 'doc_id': 'pile_of_law_0000000', 'score': 0.4237}]`

### [edge_case] What are the requirements for a company with zero employees?
- Filters: `{}` | Top-K: `5` | Tokens: `11`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_1263', 'doc_id': 'pile_of_law_0000000', 'score': 0.2901}, {'chunk_id': 'pile_of_law_0000000_chunk_0040', 'doc_id': 'pile_of_law_0000000', 'score': 0.2842}, {'chunk_id': 'pile_of_law_0000000_chunk_0054', 'doc_id': 'pile_of_law_0000000', 'score': 0.2712}]`

### [edge_case] Summarize all 10000 compliance documents.
- Filters: `{}` | Top-K: `3` | Tokens: `10`
- Answer: I don't know based on the provided documents.
- Top sources: `[{'chunk_id': 'pile_of_law_0000000_chunk_1275', 'doc_id': 'pile_of_law_0000000', 'score': 0.4938}, {'chunk_id': 'pile_of_law_0000000_chunk_1261', 'doc_id': 'pile_of_law_0000000', 'score': 0.423}, {'chunk_id': 'pile_of_law_0000000_chunk_1250', 'doc_id': 'pile_of_law_0000000', 'score': 0.3845}]`
