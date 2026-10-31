#!/usr/bin/env python3
"""Lint an IBM Cloud Databases Gen 2 Terraform file or CLI parameter file.

Exit 0 when the file matches the Gen 2 contract. Exit 1 and print one
reason per line when it does not. With no arguments, run the bundled fixtures.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"


def fail(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def strip_tf_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*?$", "", text, flags=re.M)
    text = re.sub(r"#.*?$", "", text, flags=re.M)
    return text


def is_terraform(path: Path, text: str) -> bool:
    if path.suffix in {".tf", ".tf.json"}:
        return True
    if "dataservices" in text and "ibm_database" not in text and "resource " not in text:
        return False
    return "ibm_database" in text or bool(re.search(r'resource\s+"', text))


def check_common(text: str, errors: list[str]) -> None:
    if re.search(r"ibmcloud\s+cdb\b", text):
        fail(errors, "call ibmcloud resource for this instance")
    if "adminpassword" in text:
        fail(errors, "create a service key instead of adminpassword")
    if re.search(r"\busers\s*\{", text):
        fail(errors, "create a service key instead of a users block")
    if any(token in text for token in ("members_memory_allocation_mb", "members_host_flavor", "multitenant")):
        fail(errors, "set host_flavor on the Gen 2 shape")
    for raw in re.findall(r"max_connections\s*[=:]\s*([0-9]+)", text):
        if int(raw) > 500:
            fail(errors, f"set max_connections to 500 or below (found {raw})")


def check_endpoints(text: str, errors: list[str]) -> None:
    for value in re.findall(r'service_endpoints\s*=\s*"([^"]+)"', text):
        if value != "private":
            fail(errors, f"set service_endpoints to private (found {value})")
    for value in re.findall(r'"service_endpoints"\s*:\s*"([^"]+)"', text):
        if value != "private":
            fail(errors, f"set service_endpoints to private (found {value})")
    for value in re.findall(r"--service-endpoints(?:=|\s+)\"?([A-Za-z]+)\"?", text):
        if value != "private":
            fail(errors, f"set the service endpoint to private (found {value})")


def check_plans(text: str, errors: list[str]) -> None:
    plans = re.findall(r'plan\s*=\s*"([^"]+)"', text)
    plans += re.findall(r'"resource_plan_id"\s*:\s*"([^"]+)"', text)
    for plan in plans:
        if "gen2" not in plan:
            fail(errors, f"use a plan whose name contains gen2 (found {plan})")
    for plan in re.findall(r"service-instance-create\s+\S+\s+\S+\s+(\S+)", text):
        if plan.startswith("<") or plan.startswith("$"):
            continue
        if "gen2" not in plan:
            fail(errors, f"use a CLI plan whose name contains gen2 (found {plan})")


def check_postgres(text: str, errors: list[str]) -> None:
    if "postgresql" not in text and "databases-for-postgresql" not in text:
        return
    members = [int(n) for n in re.findall(r"allocation_count\s*=\s*([0-9]+)", text)]
    members += [int(n) for n in re.findall(r'"members"\s*:\s*"?([0-9]+)"?', text)]
    for count in members:
        if count not in (1, 2, 3):
            fail(errors, f"set postgresql members to 1, 2, or 3 (found {count})")
    sizes = [int(n) for n in re.findall(r'"storage_gb"\s*:\s*"?([0-9]+)"?', text)]
    for size in sizes:
        if size < 10 or size > 9600:
            fail(errors, f"set storage_gb between 10 and 9600 (found {size})")
    if len(sizes) >= 2 and sizes[-1] < sizes[0]:
        fail(errors, "set storage_gb to the current size or larger")


def check_disk(text: str, errors: list[str]) -> None:
    sizes = [int(n) for n in re.findall(r"allocation_mb\s*=\s*([0-9]+)", text)]
    for size in sizes:
        gib = size / 1024
        if size < 10240 or size % 1024 != 0 or gib > 9600:
            fail(errors, f"set disk allocation_mb between 10 and 9600 GB (found {size})")
    if len(sizes) >= 2 and sizes[-1] < sizes[0]:
        fail(errors, "set disk allocation_mb to the current size or larger")


def check_terraform(text: str, errors: list[str]) -> None:
    if "dataservices" in text:
        fail(errors, "keep Terraform on group blocks; put dataservices in the CLI JSON")
    if "ibm_database" in text and "host_flavor" not in text:
        fail(errors, "set group.host_flavor.id")
    if "ibm_database" in text and "ibm_resource_key" not in text:
        fail(errors, "add ibm_resource_key with a role")
    if "ibm_resource_key" in text and not re.search(r"\brole\b", text):
        fail(errors, "set the service key role to Manager or Writer")
    for name, body in re.findall(r'output\s+"([^"]+)"\s*\{([^}]*)\}', text, flags=re.S):
        if re.search(r"credential|password|connection", body, flags=re.I) and not re.search(
            r"sensitive\s*=\s*true", body
        ):
            fail(errors, f'set output "{name}" sensitive = true')


def check_cli(text: str, errors: list[str]) -> None:
    if re.search(r"\bgroup\s*\{", text) or "allocation_mb" in text:
        fail(errors, "keep CLI JSON on dataservices; put group and allocation_mb in Terraform")
    if "dataservices" in text and "host_flavor" not in text and "restore_backup_id" not in text:
        fail(errors, "set dataservices.<engine>.host_flavor")
    if "service-key-create" not in text:
        return
    has_role = re.search(r"service-key-create\s+\S+\s+(Manager|Writer)\b", text) or re.search(
        r"role_crn|serviceRole:", text
    )
    if not has_role:
        fail(errors, "pass a service key role of Manager or Writer")


def lint_text(path: Path, text: str) -> list[str]:
    scanned = strip_tf_comments(text) if path.suffix == ".tf" else text
    errors: list[str] = []
    check_common(scanned, errors)
    check_endpoints(scanned, errors)
    check_plans(scanned, errors)
    check_postgres(scanned, errors)
    check_disk(scanned, errors)
    if is_terraform(path, text):
        check_terraform(scanned, errors)
    else:
        check_cli(scanned, errors)
    return errors


def lint_path(path: Path) -> list[str]:
    return lint_text(path, path.read_text())


def self_test() -> int:
    failures = 0
    fixtures = sorted(FIXTURES.glob("*"))
    if not fixtures:
        print("no fixtures found", file=sys.stderr)
        return 1
    for path in fixtures:
        if not path.is_file():
            continue
        errors = lint_path(path)
        expect_ok = path.name.startswith("valid_")
        if expect_ok and errors:
            failures += 1
            print(f"FAIL {path.name} should pass:")
            for error in errors:
                print(f"  {error}")
        elif not expect_ok and not errors:
            failures += 1
            print(f"FAIL {path.name} should report errors")
        else:
            print(f"ok {path.name}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if len(argv) == 0:
        return self_test()
    status = 0
    for arg in argv:
        path = Path(arg)
        if not path.is_file():
            print(f"{arg}: file not found", file=sys.stderr)
            status = 1
            continue
        errors = lint_path(path)
        if errors:
            status = 1
            print(f"{path}:")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"{path}: ok")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
