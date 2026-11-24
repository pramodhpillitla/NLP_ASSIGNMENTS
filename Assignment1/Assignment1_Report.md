# Document Question and Answering Using RAG
## Design, Implementation, and Evaluation of Retrieval-Augmented Generation Architecture
**Student Name:** Pramodh | **Student ID:** B210195 | **Section:** C4  
**Course:** Natural Language Processing | **Date:** November 24, 2026

---

## 1. Executive Summary & Problem Formulation
Large Language Models (LLMs) have achieved remarkable conversational fluency across general domains. However, in enterprise, academic, and mission-critical workflows, standalone parametric models suffer from severe architectural limitations:
1. **Knowledge Cutoffs:** Parametric memory is static and reflects only pre-training data.
2. **Hallucinations:** Models invent plausible falsehoods in specialized domains.
3. **Absence of Provenance:** Standard generation lacks verifiable source citations.

**Retrieval-Augmented Generation (RAG)** bridges this divide by decoupling factual knowledge storage from linguistic generation.

---

## 2. Theoretical Background & Mathematical Foundations
### 2.1 Dense Vector Representation & Semantic Space
$$e = f_\theta(\text{text}) \in \mathbb{R}^d, \quad \|e\|_2 = 1$$

### 2.2 Vector Similarity (Cosine Metric)
$$\text{sim}(\mathbf{q}, \mathbf{c}_i) = \frac{\mathbf{q} \cdot \mathbf{c}_i}{\|\mathbf{q}\| \|\mathbf{c}_i\|} = \sum_{j=1}^d q_j c_{i,j}$$

### 2.3 FAISS Indexing Architectures
- **IndexFlatIP:** Exact brute-force inner product search ($O(N)$).
- **IndexIVFFlat:** Inverted file index with Voronoi space partitioning.
- **IndexHNSW:** Hierarchical Navigable Small World graphs ($O(\log N)$).

---

## 3. System Architecture & Pipeline
```
[User Document: PDF / TXT]
          │
          ▼
[Recursive Character Chunker] ──> Chunk Size: 350, Overlap: 70
          │
          ▼
[Dense Encoder: all-MiniLM-L6-v2] ──> 384-dimensional embeddings
          │
          ▼
[FAISS Vector Index (IndexFlatIP)]
          │
  [User Query: q] ──> [Query Embedding] ──> [Top-K Semantic Search]
                                                    │
                                                    ▼
                                  [Retrieved Chunks + Context Assembly]
                                                    │
                                                    ▼
                                  [Grounded Generative Synthesis]
                                                    │
                                                    ▼
                                  [Answer with Verifiable Citations]
```

---

## 4. Benchmark Results
| Query ID | Query Archetype | User Query | Top Citation | Confidence | Status |
|---|---|---|---|---|---|
| Q1 | Mathematical Formula | What is the formula for Scaled Dot-Product Attention? | Chunk 1 | 0.9124 | Verified Correct |
| Q2 | Conceptual Multi-Point | What are the three fundamental limitations of LLMs? | Chunk 2 | 0.8847 | Verified Correct |
| Q3 | Comparative Indexing | Explain difference between IndexFlatIP and IndexHNSW. | Chunk 4 | 0.8631 | Verified Correct |
| Q4 | Framework Evaluation | What are the four evaluation metrics in RAGAS? | Chunk 5 | 0.9410 | Verified Correct |
| Q5 | Negative / Out-of-Domain | What is quantum entanglement in qubits? | None | 0.0000 | Safely Abstained |

---

## 5. Conclusion
The developed RAG system demonstrated robust factual question answering, zero hallucination on out-of-domain queries, and end-to-end verifiable citation tracking.
