# Hybrid_PDF_Reading_Order Engine

A modular, extensible PDF reading-order engine engineered to resolve deterministic reading order in complex documents by fusing page geometry, document structure, textual relationships, visual layout detection, and independent validation.

---

## 1. Project Objective

Standard PDF text extraction often produces jumbled reading orders on multi-column layouts, sidebars, tables, footnotes, and figures. `Hybrid_PDF_Reading_Order` solves this by decoupling and systematically combining:

1. **Page Geometry**: Bounding box spatial analysis, column margins, gutters, and reading zones.
2. **Document Structure**: Hierarchical outline detection (headers, titles, sections, footnotes).
3. **Text Relationships**: Spatial-linguistic continuity across columns and pages.
4. **Visual Layout Models**: Multi-class visual layout segmentation (comparing DocLayout-YOLO and PP-DocLayout).
5. **Evidence Fusion**: Multi-modal fusion weighting geometry, structure, and visual cues.
6. **Deterministic Reading Order Resolution**: Topological ordering with explicit tie-breaking (Phase 7).
7. **Independent Validation**: Rule-based and syntactic verification of reading flow integrity (Phase 7).

> **Current Status**: **Phases 1, 2, 3, 4, 5, and 6 are complete**.
> - **Phase 1**: Foundation & Architecture.
> - **Phase 2**: PDF Ingestion & Multi-Resolution Page Rendering.
> - **Phase 3**: Native Text Extraction, OCR Routing & Extraction Reconciliation.
> - **Phase 4**: Visual-Layout Model Evaluation & Coordinate Normalization.
> - **Phase 5**: Advanced Page Geometry, Column Detection & Hierarchical Structure Reconstruction.
> - **Phase 6**: Text Relationships & Multi-Source Evidence Fusion (`UnifiedStructuralGraph`).

---

## 2. Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                               FastAPI REST Layer                                  |
|   /health   |   /system/info   |   /models/available   |   /documents/ingest      |
|   /documents/{id}/graph   |   /documents/{id}/structure   |   /relationships      |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
|                           Ingestion & Rendering Engine                            |
|    PDFLoader         Metadata Extractor       PageMetadata       PageRenderer     |
|   (PyMuPDF / Auth)   (SHA-256 / Tags)     (Media/CropBox/Rot)   (150/200/300 DPI) |
+-----------------------------------------------------------------------------------+
                     |                                         |
                     v                                         v
+---------------------------------------+   +---------------------------------------+
|        Phase 3: Text & OCR Layer      |   |       Phase 4: Visual Layout Layer    |
|   NativeTextExtractor (spans/fonts)   |   |   VisualInferenceService              |
|   ExtractionQualityAssessor           |   |   DocLayout-YOLO / PP-DocLayout       |
|   OCRRouter (Tesseract / Paddle)      |   |   Morphological Fallback Segmenter    |
|   ExtractionReconciler (IoU / Sim)    |   |   ModelComparator (Benchmark Metrics) |
+---------------------------------------+   +---------------------------------------+
                     \                                         /
                      \-------------------+-------------------/
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        Phase 5: Geometry & Document Structure                     |
|   BoundingBoxAnalyzer   |   WhitespaceAnalyzer   |   ColumnDetector (1/2/3 cols)  |
|   RegionSegmenter       |   ElementClassifier    |   HeadingDetector / Lists      |
|   HierarchyBuilder (Document -> Page -> Region -> Section -> Element tree)        |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                 Phase 6: Text Relationships & Multi-Source Evidence Fusion        |
|   HeadingRelationshipDetector (INTRODUCES)   | CaptionDetector (CAPTION_OF)       |
|   ContinuationDetector (CONTINUES)           | ReferenceDetector (REFERENCES)     |
|   ConflictResolver (Preserves Disagreements) | StructuralGraphBuilder             |
|   UnifiedStructuralGraph (Nodes, Typed Edges, Regions, Conflicts, Provenance)     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               Phase 7: Layout-Aware Reading Order Resolver (Next Step)            |
+-----------------------------------------------------------------------------------+
```

---

## 3. Directory Structure

```text
Hybrid_PDF_Reading_Order/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── documents.py         # Ingestion, graph, structure, & relationship endpoints
│   │   │   ├── health.py            # Health check endpoint (/health)
│   │   │   ├── models.py            # Model availability endpoint (/models/available)
│   │   │   ├── system.py            # System & hardware info endpoint (/system/info)
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py                # Centralized Pydantic settings & path resolution
│   │   ├── logging.py               # JSON structured & console logging
│   │   ├── runtime.py               # Hardware detection & CPU/GPU device selection
│   │   └── __init__.py
│   ├── ingestion/
│   │   ├── metadata.py              # Document-level metadata & SHA-256 calculation
│   │   ├── page_metadata.py         # Per-page boundary, CropBox & orientation metadata
│   │   ├── page_registry.py         # Artifact directory manager & manifest persistence
│   │   ├── page_renderer.py         # PyMuPDF rendering & coordinate transformations
│   │   ├── pdf_loader.py            # Secure PDF opening, validation & boundary enforcement
│   │   └── __init__.py
│   ├── extraction/
│   │   ├── element_registry.py      # Stable ContentElement indexing & page queries
│   │   ├── extraction_quality.py    # Native extraction quality scoring & OCR routing triggers
│   │   ├── extraction_reconciler.py # Spatial IoU & text similarity reconciliation
│   │   ├── native_extractor.py      # Granular block, line, span, and font extraction
│   │   ├── text_normalizer.py       # Conservative Unicode & hyphenation normalizer
│   │   └── __init__.py
│   ├── ocr/
│   │   ├── base.py                  # BaseOCREngine abstract adapter
│   │   ├── ocr_preprocessing.py     # CLAHE, denoising, grayscale, and Otsu binarization
│   │   ├── ocr_router.py            # Dynamic dispatch between native, OCR, and fallback
│   │   ├── ocr_schemas.py           # OCRWord and OCRResult contracts
│   │   ├── paddle_engine.py         # PaddleOCR engine adapter
│   │   ├── tesseract_engine.py      # Tesseract OCR engine adapter
│   │   └── __init__.py
│   ├── visual_layout/
│   │   ├── adapters/
│   │   │   ├── base.py              # BaseLayoutModelAdapter abstract contract
│   │   │   ├── doclayout_yolo.py    # DocLayout-YOLO model adapter
│   │   │   ├── pp_doclayout.py      # PP-DocLayout model adapter
│   │   │   └── __init__.py
│   │   ├── class_mapping.py         # Semantic class taxonomy normalization
│   │   ├── inference_service.py     # Multi-resolution inference & CV fallback segmenter
│   │   ├── model_comparator.py      # Speed, coverage, and detection comparison
│   │   ├── model_manager.py         # Model lifecycle & weight checkpoint discovery
│   │   ├── registry.py              # LayoutModelRegistry factory
│   │   ├── schemas.py               # BoundingBox, Detections, Predictions schemas
│   │   └── __init__.py
│   ├── geometry/
│   │   ├── alignment_analysis.py    # Left, right, center, and indent alignment
│   │   ├── bbox_analysis.py         # Spatial containment, overlap, and relative distance
│   │   ├── column_detection.py      # Single, two, three column & sidebar detection
│   │   ├── geometry_features.py     # Normalized spatial feature extraction
│   │   ├── region_segmentation.py   # Page partitioning (header, footer, columns, sidebars)
│   │   ├── rotation_analysis.py     # Direction vector and orientation classification
│   │   ├── whitespace_analysis.py   # Vertical gutter and projection analysis
│   │   └── __init__.py
│   ├── document_structure/
│   │   ├── element_classifier.py    # Title, Heading, Paragraph, Caption classification
│   │   ├── heading_detector.py      # Multi-level heading hierarchy (L1/L2/L3)
│   │   ├── hierarchy_builder.py     # Non-cyclic PageStructure tree assembly
│   │   ├── list_detector.py         # Bullet and numbered list item grouping
│   │   ├── paragraph_grouper.py     # Continuous paragraph clustering
│   │   ├── structure_schemas.py     # RegionType, StructuralRegion, HierarchyNode, PageStructure
│   │   ├── table_figure_association.py # Caption-to-target proximity associator
│   │   └── __init__.py
│   ├── relationships/
│   │   ├── caption_relationships.py # CAPTION_OF and TITLE_OF relationship detection
│   │   ├── continuation_detection.py# CONTINUES paragraph continuation across soft breaks
│   │   ├── heading_relationships.py # INTRODUCES heading-to-content relationship detection
│   │   ├── reference_detection.py   # REFERENCES citation detection (e.g. Figure 1, Table 2)
│   │   ├── relationship_graph.py    # Directed RelationshipGraph assembly & deduplication
│   │   ├── relationship_schemas.py  # RelationshipEdge, RelationshipGraph, RelationshipType
│   │   └── __init__.py
│   ├── fusion/
│   │   ├── conflict_resolver.py     # Preserves semantic clashes without silent data loss
│   │   ├── evidence_normalizer.py   # Calibrates heterogeneous confidence metrics
│   │   ├── evidence_sources.py      # Granular multimodal observation collector
│   │   ├── fusion_schemas.py        # EvidenceObservation, ConflictRecord, UnifiedStructuralGraph
│   │   ├── structural_graph.py      # Fuses nodes, edges, regions, and conflicts into graph
│   │   └── __init__.py
│   ├── reporting/
│   │   ├── report_generator.py      # OpenPyXL generator for all 4 required Excel reports
│   │   └── __init__.py
│   ├── pipeline.py                  # Master DocumentIntelligencePipeline orchestrator
│   ├── schemas/                     # Shared cross-stage data models
│   ├── main.py                      # FastAPI application entrypoint
│   └── __init__.py
├── tests/                           # Complete test suite (98 tests passing)
│   ├── conftest.py                  # Pytest fixtures and synthetic PDF generators
│   ├── test_api.py                  # Root, health, system, and models API tests
│   ├── test_config.py               # Settings and configuration tests
│   ├── test_coordinates.py          # Coordinate transformation round-trip tests
│   ├── test_documents_api.py        # Ingestion API and manifest retrieval tests
│   ├── test_metadata.py             # Document & page metadata tests
│   ├── test_page_renderer.py        # Rendering engine at 150/200/300 DPI tests
│   ├── test_pdf_loader.py           # Loader, encryption & limit validation tests
│   ├── test_phase3_extraction_ocr.py# Native extraction, OCR routing & reconciliation tests
│   ├── test_phase4_visual_layout.py # Class mapping, model manager & comparator tests
│   ├── test_phase5_geometry_structure.py # Bounding box, column, region & hierarchy tests
│   ├── test_phase6_relationships_fusion.py # Introduces, captions, continuations & fusion tests
│   ├── test_pipeline_e2e.py         # End-to-end pipeline execution & graph endpoint tests
│   ├── test_runtime.py              # Hardware detection & device fallback tests
│   ├── test_visual_layout.py        # Schema, adapter, and registry tests
│   └── __init__.py
├── output/
│   ├── logs/                        # Structured JSON application logs (app.log)
│   ├── reports/                     # Excel reports (PHASE_3, PHASE_4, PHASE_5, PHASE_6)
│   └── processed/                   # Page PNGs, structural_graph.json, manifests
├── scripts/
│   ├── generate_all_reports.py      # Automated report runner on representative PDFs
│   ├── ingest_pdf.py                # Command-line PDF ingestion and rendering tool
│   └── __init__.py
├── requirements/
│   ├── base.txt                     # Core production dependencies
│   ├── cpu.txt                      # CPU-optimized dependencies
│   ├── gpu.txt                      # NVIDIA CUDA / GPU dependencies
│   ├── ocr.txt                      # OCR engine dependencies
│   ├── models.txt                   # Visual layout model dependencies
│   └── dev.txt                      # Testing and development dependencies
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Reports Generated

The pipeline generates 4 comprehensive Excel reports in `output/reports/`:

1. **`PHASE_3_EXTRACTION_OCR_REPORT.xlsx`**:
   - `Document Summary`: Native blocks, OCR routing status, reconciled elements, disagreements, performance.
   - `Page Quality & Decisions`: Character counts, coverage percentage, image dominance, routing decisions with explicit reasons.
   - `Reconciliation Decisions`: Spatial IoU, text similarity, disagreement flags, and resolution explanations.
2. **`PHASE_4_VISUAL_MODEL_COMPARISON.xlsx`**:
   - `Model Inventory`: DocLayout-YOLO vs. PP-DocLayout status, framework versions, supported devices, and checkpoint paths.
   - `Layout Detection Summary`: Detection counts, inference timing, detected classes, and verified coordinate systems.
3. **`PHASE_5_GEOMETRY_STRUCTURE_REPORT.xlsx`**:
   - `Page Geometry & Columns`: Dimensions, rotation, column counts, total regions, hierarchy depth.
   - `Structural Regions`: Header, footer, column, and sidebar regions with bounding boxes and reading priority.
   - `Element Classification`: Title, heading, paragraph, list item, and caption classification with typography metadata.
4. **`PHASE_6_EVIDENCE_FUSION_REPORT.xlsx`**:
   - `Structural Graph Summary`: Total nodes, edges, regions, conflicts, completeness score, and timestamps.
   - `Relationship Edges`: Directed edges (`INTRODUCES`, `CAPTION_OF`, `CONTINUES`, `REFERENCES`) with confidence scores.
   - `Conflict Register`: Preserved disagreements between visual models and text extraction.

---

## 5. Running the Pipeline & Generating Reports

### Run Automated Report Generation Script
```powershell
python scripts/generate_all_reports.py
```

### CLI Document Ingestion
```powershell
python scripts/ingest_pdf.py datasets/sample_pdfs/single_column_digital.pdf --dpi 200
```

---

## 6. Running Tests & Compilation Checks

### Compilation Check
```powershell
python -m compileall -q backend scripts tests
```

### Run Full Test Suite (98 Tests Passing)
```powershell
python -m pytest tests -v
```

### Run Quiet Mode
```powershell
python -m pytest tests -q
```
*Actual output:*
```text
98 passed, 1 warning in 21.19s
```
