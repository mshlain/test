#!/usr/bin/env python3
import logging
import subprocess


class ColorFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[34m"
    green = "\x1b[32m"
    red = "\x1b[31m"
    reset = "\x1b[0m"

    def format(self, record):
        if record.levelno == logging.INFO:
            record.msg = f"{self.blue}{record.msg}{self.reset}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{self.red}{record.msg}{self.reset}"
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
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def log_section(log, title):
    log.info("=" * 50)
    log.info(f"  {title}")
    log.info("=" * 50)
    log.info("")


def check_fips(log):
    log_section(log, "Test fips in kernel")
    cmd = "cat /proc/sys/crypto/fips_enabled"
    log.info(f"Command: {cmd}")
    log.info("Expected: 1")

    result = run_cmd(cmd)
    log.info(f"Result:  {result}")

    if result == "1":
        log.success("FIPS is enabled")
    else:
        log.error(f"Expected 1 got {result}")


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


def main():
    log = setup_logging()
    check_fips(log)
    log.info("\n")
    check_openssl(log)
    log.info("\n")
    check_providers(log)
    log.info("\n")
    check_ciphers(log)


if __name__ == "__main__":
    main()

# curl https://raw.githubusercontent.com/mshlain/test/refs/heads/main/fips.py | python3
