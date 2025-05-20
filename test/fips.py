#!/usr/bin/env python3
# curl https://raw.githubusercontent.com/mshlain/test/refs/heads/main/test/fips.py | python3
import logging
import subprocess

errors_array = []


class ColorFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[34m"
    green = "\x1b[32m"
    red = "\x1b[31m"
    reset = "\x1b[0m"

    def format(self, record):
        if record.levelno == logging.ERROR:
            errors_array.append(record.msg)

        if record.levelno == logging.INFO:
            record.msg = f"{self.blue}{record.msg}{self.reset}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{self.red} ERROR {record.msg}{self.reset}"
        elif record.levelno == logging.SUCCESS:
            record.msg = f"{self.green}{record.msg}{self.reset}"
        return super().format(record)


def setup_logging():
    logging.SUCCESS = 25
    logging.addLevelName(logging.SUCCESS, "SUCCESS")
    logger = logging.getLogger("fips")
    logger.success = lambda msg, *args: logger._log(logging.SUCCESS, msg, args)

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        stderr = result.stderr.strip()
        if stderr and result.returncode != 0:
            return stderr
        stdout = result.stdout.strip()
        return stderr + "\n" + stdout
    except Exception as e:
        return f"Error: {e}"


def log_section(log, title):
    log.info("=" * 50)
    log.info(f"  {title}")
    log.info("=" * 50)
    log.info("")


def check_fips_in_kernel(log):
    log_section(log, "Test fips in kernel")
    cmd = "cat /proc/sys/crypto/fips_enabled"
    log.info(f"Command: {cmd}")
    log.info("Expected: 1")

    result = run_cmd(cmd)
    result = result.strip()
    log.info(f"Result:  {result}")

    if result == "1":
        log.success("FIPS is enabled in kernel")
    else:
        log.error("FIPS is not enabled in kernel")


def check_openssl(log):
    log_section(log, "Print openssl location")
    result = run_cmd("which openssl")
    log.info(f"Result: {result}")

    log_section(log, "Print openssl version")
    result = run_cmd("openssl version -a")
    log.info(f"Result:\n{result}")

    log_section(log, "Print openssl directory")
    result = run_cmd("ls -lah /usr/lib/ssl")
    log.info(f"Result:\n{result}")

    log_section(log, "Print openssl providers directory")
    result = run_cmd("ls -lah /usr/lib/ssl/providers")
    log.info(f"Result:\n{result}")

    log_section(log, "Print fipsmodule.cnf file")
    result = run_cmd("cat /usr/lib/ssl/providers/fipsmodule.cnf")
    log.info(f"Result:\n{result}")


def check_providers(log):
    log_section(log, "Test openssl providers")
    cmd = "openssl list -providers"
    result = run_cmd(cmd)
    log.info(f"Result: {result}")

    if all(x in result for x in ["fips", "OpenSSL FIPS Provider", "status: active"]):
        log.success("FIPS provider is enabled successfully")
    else:
        log.error("FIPS provider is not enabled properly")


def check_ciphers(log):
    log_section(log, "Test openssl ciphers")
    cmd = "openssl ciphers -v"
    log.info(f"Command: {cmd}")
    result = run_cmd(cmd)
    log.info(f"Result:\n{result}")

    if "SSLv3" in result:
        log.error("SSLv3 is not FIPS compliant")
    else:
        log.success("No SSLv3 ciphers found, FIPS compliance is maintained")


def check_microk8s_args(log):
    log_section(log, "Test microk8s args")

    cmd = "cat /var/snap/microk8s/current/args/fips-env"
    log.info(f"Command: {cmd}")
    log.info("Expected: GOFIPS=1")

    result = run_cmd(cmd)
    log.info(f"Result:  {result}")

    if "GOFIPS=1" in result:
        log.success("GOFIPS is enabled in microk8s")
    else:
        log.error("GOFIPS is not enabled in microk8s")


def _build_exec_on_pod_cmd(namespace, pod_name_prefix, cmd):
    # kubectl -n default exec -it $(kubectl -n default get pods | grep "^zkeycloak-db" | head -n 1 | awk '{print $1}') -- openssl list -providers
    return f"/snap/bin/microk8s.kubectl -n {namespace} exec $(/snap/bin/microk8s.kubectl -n {namespace} get pods | grep \"^{pod_name_prefix}\" | head -n 1 | awk '{{print $1}}') -- {cmd}"


def check_infra_pod(log, namespace, pod_name):
    log_section(log, f"Test {pod_name} pod")

    pod_cmd = "openssl list -providers"
    cmd = _build_exec_on_pod_cmd(namespace, pod_name, pod_cmd)
    log.info(f"Command: {cmd}")
    result = run_cmd(cmd)
    log.info(f"Result:\n{result}")

    if all(x in result for x in ["fips", "OpenSSL FIPS Provider", "status: active"]):
        log.success(f"FIPS provider is enabled successfully in {pod_name} pod")
    else:
        log.error(f"FIPS provider is not enabled properly in {pod_name} pod")


def check_chainguard_pod(log, namespace, pod_name):
    log_section(log, f"Test {pod_name} pod")

    pod_cmd = "openssl-fips-test"
    cmd = _build_exec_on_pod_cmd(namespace, pod_name, pod_cmd)
    log.info(f"Command: {cmd}")
    result = run_cmd(cmd)
    log.info(f"Result:\n{result}")

    if "Lifecycle assurance satisfied" in result:
        log.success(
            f"FIPS provider is enabled successfully in {pod_name} pod (chainguard)"
        )
    else:
        log.error(
            f"FIPS provider is not enabled properly in {pod_name} pod (chainguard)"
        )


def _core(log):
    check_fips_in_kernel(log)
    log.info("\n")
    check_openssl(log)
    log.info("\n")
    check_providers(log)
    log.info("\n")
    check_ciphers(log)
    log.info("\n")
    check_microk8s_args(log)
    log.info("\n")


def check_single_pod(log, namespace, short_pod_name):
    if "db-management-utility" in short_pod_name:
        log.error(f"{short_pod_name} is not fips compliant")
        return

    if "scripts-service" in short_pod_name:
        log.error(f"{short_pod_name} is not fips compliant")
        return

    not_testable_pods = ["host-metrics", "pods-metrics-kube-eagle"]
    if short_pod_name in not_testable_pods:
        log.info(f"{short_pod_name} is not testable")
        return

    chainguard_pods = [
        "coredns",
        "zkeycloak-0",
        "prometheus-server",
        "static-file-system",
        "metrics-server-metrics-server-fips",
    ]
    if short_pod_name in chainguard_pods:
        check_chainguard_pod(log, namespace, short_pod_name)
        return

    # all the rest pods are infra pods
    check_infra_pod(
        log,
        namespace,
        short_pod_name,
    )


def check_all_pods(log):
    cmd = "/snap/bin/microk8s.kubectl get pods --all-namespaces"
    result = run_cmd(cmd)
    lines = result.split("\n")
    for line in lines:
        if not line:
            continue
        if "READY" in line:
            continue
        parts = line.split()
        namespace = parts[0]
        pod_name = parts[1]
        # short pod name is pod name without two last parts
        parts = pod_name.split("-")
        if len(parts) < 3:
            short_pod_name = pod_name
        else:
            short_pod_name_parts = parts[:-2]
            short_pod_name = "-".join(short_pod_name_parts)

        if not short_pod_name:
            raise ValueError("short_pod_name is empty")

        check_single_pod(log, namespace, short_pod_name)


def print_summary():
    print("\n")
    print("\n")
    print("\n")
    errors_count = len(errors_array)
    if errors_count > 0:
        print(f"Summary: {errors_count} Errors found:")
        for error in errors_array:
            print(error)
    else:
        print("Summary: No errors found.")


def main():
    log = setup_logging()
    # _core(log)
    check_all_pods(log)
    print_summary()


if __name__ == "__main__":
    main()

# curl https://raw.githubusercontent.com/mshlain/test/refs/heads/main/test/fips.py | python3
