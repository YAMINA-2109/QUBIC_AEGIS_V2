import re

def strict_validator(code: str) -> str:
    """
    Runs static analysis and style validation checks on the given commented C++ smart contract code.
    Returns a markdown-formatted report summarizing findings.
    """
    report = ["# ✅ Strict Validation Report"]

    if not code.strip():
        report.append("- ⚠️ No code provided for validation.")
        return "\n".join(report)

    # Check for forbidden/dangerous functions
    forbidden_functions = ["system", "fork", "exec", "popen"]
    for func in forbidden_functions:
        if re.search(rf"\b{func}\s*\(", code):
            report.append(f"- ❌ Forbidden function detected: `{func}()`")

    # Check for suspicious includes
    includes = re.findall(r'#include\s+[<"].+[>"]', code)
    for inc in includes:
        if any(suspicious in inc for suspicious in ["unistd.h", "sys/"]):
            report.append(f"- ❌ Suspicious include detected: `{inc}`")

    if not includes:
        report.append("- ⚠️ No #include statements found. Did you forget standard libraries?")

    # Check for excessively long lines
    long_lines = [i + 1 for i, line in enumerate(code.splitlines()) if len(line) > 120]
    if long_lines:
        report.append(f"- ⚠️ Lines exceeding 120 characters found at: {long_lines}")

    # Check naming conventions (simple heuristic)
    if not re.search(r'\b[A-Z]', code):
        report.append("- ⚠️ No uppercase identifiers detected. Consider using CamelCase or Uppercase for types.")

    # If no issues found, confirm success
    if len(report) == 1:
        report.append("- ✅ No critical issues found. Code passes strict validation.")

    return "\n".join(report)

