"""Unified Master Test Runner and Reading Order Evaluation for HRO.

Executes everything required to check reading order:
1. Environment & Hardware Diagnostics (CPU, RAM, Tesseract, PaddleOCR, DocLayout-YOLO)
2. Comprehensive Reading-Order Verification Suites across all phases:
   - Phase 5: Geometry & Document Structure Reconstruction
   - Phase 6: Relationships & Multi-Source Evidence Fusion
   - Phase 7: Deterministic Layout-Aware Reading-Order Resolver
   - Phase 8: Multi-Stage Validation & Graph Integrity
   - Phase 9: Benchmark Metrics, Archetypes & Dataset Quality
   - Phase 10: Optimization, Caching & Performance Verification
3. Real Input PDF Processing:
   - Ingests PDF documents from input/ folder (C:\\Users\\LeelaKota\\Desktop\\HRO\\input)
   - Outputs processed artifacts to output/
4. Auto-Incrementing Versioned Excel Reporting:
   - Automatically generates HRO_Reading_Order_Report_v1.xlsx, v2, ..., vn
   - Stored in C:\\Users\\LeelaKota\\Desktop\\HRO and output/

Usage:
    python run_all_tests.py                 # Runs complete reading order verification & generates vN report
    python run_all_tests.py --fast          # Fast verification mode (~8 seconds) + report
    python run_all_tests.py --report-limit 10 # Process 10 files from input/
    python run_all_tests.py --all-input     # Process ALL files in input/ folder
"""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.reporting.batch_reading_order_reporter import BatchReadingOrderReporter


def print_banner():
    print("=" * 80)
    print("   HRO — HYBRID PDF READING ORDER ENGINE: MASTER SUITE & EVALUATION")
    print("=" * 80)
    print(f"Timestamp:       {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Python Version:  {sys.version.split()[0]} ({sys.platform})")
    print(f"Project Path:    {PROJECT_ROOT}")


def print_environment_status():
    from backend.core.runtime import get_runtime_manager
    from backend.ocr.ocr_router import OCRRouter
    from backend.visual_layout.model_manager import VisualModelManager

    runtime = get_runtime_manager().resolve_runtime()
    router = OCRRouter()
    engine_status = {eng.get_name(): eng.is_available()[0] for eng in router.engines}
    v_mgr = VisualModelManager()
    yolo_ready, _ = v_mgr.check_adapter_readiness("doclayout_yolo")
    pp_ready, _ = v_mgr.check_adapter_readiness("pp_doclayout")

    ram_gb = (runtime.hardware.ram_total_bytes / (1024**3)) if runtime.hardware.ram_total_bytes else 0.0

    print("\n[ENVIRONMENT & MODEL DIAGNOSTICS]")
    print(f" - Execution Device:     {runtime.device_selected.upper()} ({runtime.hardware.cpu_count_logical} CPU Threads, {ram_gb:.1f} GB RAM)")
    print(f" - Tesseract OCR 5.4:    {'READY' if engine_status.get('tesseract') else 'UNAVAILABLE'}")
    print(f" - PaddleOCR Engine 3.7: {'READY' if engine_status.get('paddleocr') else 'UNAVAILABLE'}")
    print(f" - DocLayout-YOLO v10:   {'READY' if yolo_ready else 'UNAVAILABLE'}")
    print(f" - PP-DocLayout PicoDet: {'READY' if pp_ready else 'UNAVAILABLE'}")
    print("-" * 80)


def run_reading_order_tests(mode: str = "full", verbose: bool = False, specific_target: str = None) -> int:
    """Run test suites validating reading order algorithms, geometry, fusion, and validation."""
    cmd = [sys.executable, "-m", "pytest"]

    if specific_target:
        print(f"\n[STEP 1: TEST EXECUTION TARGET]: {specific_target}")
        cmd.append(specific_target)
    elif mode == "fast":
        # Fast test suite verifying reading order core, validation, schemas, and benchmark prep
        fast_suites = [
            "tests/test_phase7_reading_order.py",
            "tests/test_phase8_validation.py",
            "tests/test_phase9_benchmarking.py",
            "tests/test_benchmark_dataset_prep.py",
            "tests/test_phase5_geometry_structure.py",
            "tests/test_phase6_relationships_fusion.py",
            "tests/test_phase10_optimization.py",
            "tests/test_api.py",
            "tests/test_config.py",
            "tests/test_coordinates.py",
            "tests/test_metadata.py",
            "tests/test_pdf_loader.py",
            "tests/test_runtime.py",
        ]
        print("\n[STEP 1: READING ORDER TEST VERIFICATION] (Fast Mode)")
        cmd.extend(fast_suites)
        # Exclude slow e2e tests in fast mode
        cmd.extend(["-k", "not (real_pdf_46 or real_two_column or live_pipeline)"])
    else:
        print("\n[STEP 1: READING ORDER TEST VERIFICATION] (Full Comprehensive Mode)")
        cmd.append("tests")

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    print(f"Command: {' '.join(cmd)}")
    print("Executing tests... Please wait...\n")

    t0 = time.perf_counter()
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    duration = time.perf_counter() - t0

    if result.returncode == 0:
        print(f"\n>>> ALL READING ORDER VERIFICATION TESTS PASSED in {duration:.2f}s! <<<\n")
    else:
        print(f"\n>>> WARNING: Tests finished with exit code {result.returncode} in {duration:.2f}s <<<\n")

    return result.returncode


def run_input_batch_evaluation(
    limit: int = 5,
    all_files: bool = False,
    dpi: int = 200,
) -> Tuple[Path, int]:
    """Process files from input/ folder and generate versioned Excel report (v1, v2, ..., vn)."""
    reporter = BatchReadingOrderReporter(root_dir=PROJECT_ROOT)

    input_pdfs = sorted(list(reporter.input_dir.glob("*.pdf")))
    total_in_folder = len(input_pdfs)

    if total_in_folder == 0:
        print(f"[Warning] No PDF documents found in {reporter.input_dir}")
        return None, 0

    target_queue = input_pdfs if all_files else input_pdfs[:limit]

    # Predict next version
    next_ver = reporter.get_next_report_version()

    print("=" * 80)
    print(f"[STEP 2: PROCESSING INPUT FOLDER & GENERATING REPORT v{next_ver}]")
    print("=" * 80)
    print(f"Input Directory:  {reporter.input_dir}")
    print(f"Total in Folder:  {total_in_folder} PDF files")
    print(f"Selected Queue:   {len(target_queue)} PDF files")
    print(f"Output Directory: {reporter.output_dir}")
    print(f"Report Target:    {reporter.root_dir / f'HRO_Reading_Order_Report_v{next_ver}.xlsx'}")
    print("-" * 80)

    # Execute batch reading order pipeline
    records = reporter.process_files(pdf_paths=target_queue, dpi=dpi)

    # Generate versioned report
    report_path, version = reporter.generate_versioned_report(records, version=next_ver)

    return report_path, version


def main():
    parser = argparse.ArgumentParser(
        description="Unified Master Test Runner and Reading Order Evaluation for HRO."
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Fast verification mode for unit tests (~8 seconds)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose pytest output",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Specific test file or directory to run",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Use 4 parallel workers for batch processing (Default: True)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )
    parser.add_argument(
        "--flush-interval",
        type=int,
        default=12,
        help="Flush/write progress to Excel report every N files (default: 12)",
    )
    parser.add_argument(
        "--report-limit",
        type=int,
        default=None,
        help="Optional limit on number of PDF files to process from input/ folder (if omitted, processes ALL files)",
    )
    parser.add_argument(
        "--all-input",
        action="store_true",
        default=True,
        help="Process ALL PDF files present in input/ folder (Default: True)",
    )
    parser.add_argument(
        "--skip-input",
        action="store_true",
        help="Skip input folder batch processing and only run pytest test suites",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip unit/integration tests and run input folder batch processing immediately",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        choices=[150, 200, 300],
        default=200,
        help="Rendering resolution DPI for input processing (default: 200)",
    )
    args = parser.parse_args()

    print_banner()
    try:
        print_environment_status()
    except Exception as exc:
        print(f"[Warning] Could not inspect runtime environment: {exc}")

    # Step 1: Run Reading Order Verification Tests
    test_exit_code = 0
    if not args.skip_tests:
        mode = "fast" if args.fast else "full"
        test_exit_code = run_reading_order_tests(mode=mode, verbose=args.verbose, specific_target=args.target)
    else:
        print("\n[STEP 1: SKIPPED -- Running Input Folder Batch Directly]")

    # Step 2: Process Input Files & Generate Versioned Report (v1, v2, ..., vn)
    report_path = None
    version_num = 0
    if not args.skip_input:
        if args.parallel:
            from scripts.process_parallel_batch import run_parallel_batch
            run_parallel_batch(
                input_dir=PROJECT_ROOT / "input",
                processed_dir=PROJECT_ROOT / "output" / "processed",
                root_dir=PROJECT_ROOT,
                workers=args.workers,
                flush_interval=args.flush_interval,
                limit=args.report_limit,
                dpi=args.dpi,
            )
        else:
            report_path, version_num = run_input_batch_evaluation(
                limit=args.report_limit or 0,
                all_files=(args.report_limit is None),
                dpi=args.dpi,
            )

    print("\n" + "=" * 80)
    print("   >>> HRO MASTER EXECUTION SUMMARY <<<")
    print("=" * 80)
    print(f"Reading Order Tests:    {'PASSED (100%)' if test_exit_code == 0 else 'COMPLETED WITH WARNINGS'}")
    if report_path:
        print(f"Generated Excel Report: v{version_num} -> {report_path}")
        print(f"Mirrored Output Copy:   {PROJECT_ROOT / 'output' / report_path.name}")
    print("=" * 80 + "\n")

    sys.exit(test_exit_code)


if __name__ == "__main__":
    main()
