import time
from pathlib import Path

# STEP 함수 임포트 (이미 작성한 각 단계 코드를 함수로 만든 상태라고 가정)
from step1_data_filter import run_step1_main
from step2_data_decomposed import run_step2
from step3_1_data_split_chunk import run_step3
from step4_select_max_diffrate_date import run_step4

def main():
    start_time = time.time()
    base_dir = Path.cwd().parents[1] / "data"

    print("🚀 Step 1: Filtering & Convert CSV → Parquet")
    step1_output = run_step1_main(
        input_dir=base_dir / "original",
        output_dir=base_dir / "filtered" / "TORAY"
    )

    print("🚀 Step 2: Decompose & Merge Motors")
    step2_output = run_step2(
        input_dir=step1_output,
        output_dir=base_dir / "decomposed" / "TORAY"
    )

    print("🚀 Step 3: Split into 24h Chunks")
    step3_output = run_step3(
        input_dir=step2_output,
        output_dir=base_dir / "chunked" / "TORAY"
    )

    print("🚀 Step 4: Select Max Diff Rate Dates")
    run_step4(
        input_dir=step3_output,
        output_dir=base_dir / "analysis_results"
    )

    elapsed = time.time() - start_time
    print(f"✅ All steps completed in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
