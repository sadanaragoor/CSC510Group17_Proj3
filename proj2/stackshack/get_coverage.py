#!/usr/bin/env python
"""Quick script to get coverage summary."""
import coverage

cov = coverage.Coverage()
cov.load()

print("\n" + "=" * 60)
print("COVERAGE SUMMARY")
print("=" * 60)

# Get overall coverage
total_stmts = 0
total_missing = 0
total_excluded = 0

# Track by module
module_stats = {
    "models": {"stmts": 0, "missing": 0},
    "controllers": {"stmts": 0, "missing": 0},
    "routes": {"stmts": 0, "missing": 0},
    "services": {"stmts": 0, "missing": 0},
}

for file_path in cov.get_data().measured_files():
    try:
        analysis = cov.analysis(file_path)
        stmts, missing, excluded = analysis[1], analysis[2], analysis[3]

        total_stmts += len(stmts)
        total_missing += len(missing)
        total_excluded += len(excluded)

        # Categorize by module
        if "models" in file_path:
            module_stats["models"]["stmts"] += len(stmts)
            module_stats["models"]["missing"] += len(missing)
        elif "controllers" in file_path:
            module_stats["controllers"]["stmts"] += len(stmts)
            module_stats["controllers"]["missing"] += len(missing)
        elif "routes" in file_path:
            module_stats["routes"]["stmts"] += len(stmts)
            module_stats["routes"]["missing"] += len(missing)
        elif "services" in file_path:
            module_stats["services"]["stmts"] += len(stmts)
            module_stats["services"]["missing"] += len(missing)
    except:
        pass

# Calculate percentages
total_covered = total_stmts - total_missing
overall_coverage = (total_covered / total_stmts * 100) if total_stmts > 0 else 0

print(f"\nOVERALL COVERAGE: {overall_coverage:.1f}%")
print(f"Total Statements: {total_stmts}")
print(f"Covered: {total_covered}")
print(f"Missing: {total_missing}")
print(f"Excluded: {total_excluded}")

print("\n" + "-" * 60)
print("COVERAGE BY MODULE:")
print("-" * 60)

for module, stats in module_stats.items():
    if stats["stmts"] > 0:
        covered = stats["stmts"] - stats["missing"]
        pct = (covered / stats["stmts"] * 100) if stats["stmts"] > 0 else 0
        print(f"{module:15} {pct:6.1f}% ({covered:4}/{stats['stmts']:4} statements)")

print("=" * 60 + "\n")
