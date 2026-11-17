# AI PPT Generator — Documentation Index

## Project: AI PPT Generator
**Course**: ROSPL (Research Oriented Study Project Laboratory), Semester 7  
**Technology Stack**: Python 3.15 · Streamlit · Groq AI SDK · python-pptx · Pydantic v2  
**Test Status**: ✅ 18/18 pytest tests passing  

---

## Documentation Structure

```
docs/
├── README.md                          ← This file (navigation index)
├── report.md                          ← Consolidated full academic report
│
├── chapters/
│   ├── 01_abstract.md                 ← Abstract & keywords
│   ├── 02_introduction.md             ← Background, problem statement, objectives, scope
│   ├── 03_literature_review.md        ← IEEE-referenced literature survey
│   ├── 04_requirements.md             ← Functional & non-functional requirements
│   ├── 05_system_design.md            ← Architecture, layers, state management
│   ├── 06_implementation.md           ← Module descriptions, algorithms, challenges
│   ├── 07_testing.md                  ← All 18 test cases with results
│   ├── 08_results.md                  ← Outcomes, performance, comparison, limitations
│   ├── 09_conclusion.md               ← Conclusion & 10-point future scope
│   └── 10_references.md               ← IEEE format bibliography [1]–[20]
│
├── diagrams/
│   ├── architecture.md                ← Figures 1–4: System & deployment architecture
│   ├── dfd.md                         ← Figures 5–7: DFD Level 0, 1, and 2
│   ├── uml_class.md                   ← Figure 8: Complete UML class diagram
│   ├── uml_sequence.md                ← Figures 9–10: Sequence & error handling
│   ├── uml_usecase.md                 ← Figures 11–12: Use cases & actor table
│   └── er_diagram.md                  ← Figures 13–14: Logical data model & state
│
└── appendices/
    ├── abbreviations.md               ← Appendix A: Full abbreviation list
    ├── sample_ai_output.md            ← Appendix B: Representative AI JSON output
    └── test_results.md                ← Appendix C: Full pytest terminal output
```

---

## Quick Navigation

| Section | File | Description |
|---|---|---|
| Abstract | [01_abstract.md](chapters/01_abstract.md) | Project summary & keywords |
| Introduction | [02_introduction.md](chapters/02_introduction.md) | Problem, objectives, scope |
| Literature Review | [03_literature_review.md](chapters/03_literature_review.md) | Related work, comparison table |
| Requirements | [04_requirements.md](chapters/04_requirements.md) | 12 FR, 7 NFR, hardware/software |
| System Design | [05_system_design.md](chapters/05_system_design.md) | 8-layer architecture, themes |
| Implementation | [06_implementation.md](chapters/06_implementation.md) | All 9 modules, algorithms |
| Testing | [07_testing.md](chapters/07_testing.md) | 18 test cases with pass/fail |
| Results | [08_results.md](chapters/08_results.md) | Performance, comparison, limitations |
| Conclusion | [09_conclusion.md](chapters/09_conclusion.md) | Conclusion, 10 future enhancements |
| References | [10_references.md](chapters/10_references.md) | IEEE bibliography [1]–[20] |
| Architecture Diagrams | [diagrams/architecture.md](diagrams/architecture.md) | Mermaid: system, pipeline, deployment |
| Data Flow Diagrams | [diagrams/dfd.md](diagrams/dfd.md) | DFD Level 0, 1, 2 |
| Class Diagram | [diagrams/uml_class.md](diagrams/uml_class.md) | All Pydantic models & service classes |
| Sequence Diagrams | [diagrams/uml_sequence.md](diagrams/uml_sequence.md) | End-to-end flow + error handling |
| Use Case Diagram | [diagrams/uml_usecase.md](diagrams/uml_usecase.md) | All system use cases |
| ER Diagram | [diagrams/er_diagram.md](diagrams/er_diagram.md) | Logical data model + state diagram |
| Abbreviations | [appendices/abbreviations.md](appendices/abbreviations.md) | 35 abbreviations |
| Sample AI Output | [appendices/sample_ai_output.md](appendices/sample_ai_output.md) | Representative JSON + schema ref |
| Test Results | [appendices/test_results.md](appendices/test_results.md) | Full pytest terminal output |
| **Full Report** | [**report.md**](report.md) | **Complete consolidated document** |

---

## Figure Index

| Figure | Description | Location |
|---|---|---|
| Figure 1 | High-Level System Architecture | [diagrams/architecture.md](diagrams/architecture.md) |
| Figure 2 | Module Dependency Graph | [diagrams/architecture.md](diagrams/architecture.md) |
| Figure 3 | Presentation Generation Pipeline | [diagrams/architecture.md](diagrams/architecture.md) |
| Figure 4 | Deployment Architecture | [diagrams/architecture.md](diagrams/architecture.md) |
| Figure 5 | DFD Level 0 — Context Diagram | [diagrams/dfd.md](diagrams/dfd.md) |
| Figure 6 | DFD Level 1 — System Decomposition | [diagrams/dfd.md](diagrams/dfd.md) |
| Figure 7 | DFD Level 2 — JSON Parsing Subsystem | [diagrams/dfd.md](diagrams/dfd.md) |
| Figure 8 | UML Class Diagram | [diagrams/uml_class.md](diagrams/uml_class.md) |
| Figure 9 | UML Sequence Diagram (generation) | [diagrams/uml_sequence.md](diagrams/uml_sequence.md) |
| Figure 10 | UML Sequence Diagram (error handling) | [diagrams/uml_sequence.md](diagrams/uml_sequence.md) |
| Figure 11 | Use Case Diagram | [diagrams/uml_usecase.md](diagrams/uml_usecase.md) |
| Figure 12 | Actor Responsibilities Table | [diagrams/uml_usecase.md](diagrams/uml_usecase.md) |
| Figure 13 | ER / Logical Data Model | [diagrams/er_diagram.md](diagrams/er_diagram.md) |
| Figure 14 | Application State Diagram | [diagrams/er_diagram.md](diagrams/er_diagram.md) |

