import os
import asyncio
import secrets
import logging
import re

from fastapi import HTTPException, Path
from datetime import datetime, timedelta

from core.config import PATH_CERTIFICATES, MAX_TOKEN_AGE_HOURS

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_stack_name(stack: str) -> str:
    """Validates that the stack name does not contain path traversal"""
    if not re.match(r"^[a-zA-Z0-9_-]+$", stack):
        raise HTTPException(
            status_code=400,
            detail="Stack name must contain only alphanumeric characters, hyphens, and underscores",
        )

    if ".." in stack or "/" in stack or "\\" in stack:
        raise HTTPException(status_code=400, detail="Invalid stack name")

    return stack


def get_stack_dependency(stack: str = Path(..., description="Stack identifier")) -> str:
    """Dependency to validate stack across all routes"""
    return validate_stack_name(stack)


def timing_safe_compare(a: str, b: str) -> bool:
    """Timing attack resistant comparison"""
    return secrets.compare_digest(a.encode(), b.encode())


class TokenValidator:
    """Token validator with secure file handling"""

    def __init__(self, stack: str, token: str, resource: str):
        self.stack = stack
        self.token = token
        self.resource = resource  # "admin" or "computer"
        self.token_file = PATH_CERTIFICATES / stack / resource / "tokens" / token

    async def validate(self) -> tuple[str, str]:
        # Basic validation
        if not self.token or len(self.token) != 64:
            logger.warning(f"Invalid token format from stack {self.stack}")
            await asyncio.sleep(3)  # Timing attack mitigation
            raise HTTPException(status_code=401, detail="Invalid token")

        # Verify existence
        if not self.token_file.exists():
            logger.warning(
                f"Token not found: {self.token[:8]}... for stack {self.stack}"
            )
            await asyncio.sleep(3)
            raise HTTPException(status_code=401, detail="Invalid token")

        # Verify expiration by timestamp of the file
        creation_time = datetime.fromtimestamp(self.token_file.stat().st_ctime)
        age = datetime.now() - creation_time

        if age > timedelta(hours=MAX_TOKEN_AGE_HOURS):
            logger.info(f"Expired token removed: {self.token[:8]}...")
            self.token_file.unlink(missing_ok=True)
            await asyncio.sleep(3)
            raise HTTPException(status_code=401, detail="Token expired")

        # Read content
        try:
            content = self.token_file.read_text(encoding="utf-8").strip()
            parts = content.split("|")

            if len(parts) != 2:
                logger.error(f"Malformed token content in {self.token_file}")
                await asyncio.sleep(3)
                raise HTTPException(status_code=401, detail="Invalid token format")

            common_name, validity_days = parts

            # Validate fields
            int(validity_days)  # must be an integer

            return common_name, validity_days

        except (ValueError, OSError) as e:
            logger.error(f"Error reading token file: {e}")
            await asyncio.sleep(3)
            raise HTTPException(status_code=401, detail="Invalid token")

    def consume(self):
        """Deletes the token (single use)"""
        self.token_file.unlink(missing_ok=True)


def sanitize_input(value: str, allowed_chars: str = r"[^a-zA-Z0-9@._:-]") -> str:
    """Sanitizes input by removing dangerous characters"""
    return re.sub(allowed_chars, "", value)


async def create_admin_cert(
    fqdn: str,
    host: str,
    stack: str,
    common_name: str,
    password: str,
    days: str,
    email: str,
) -> bool:
    try:
        stack_clean = sanitize_input(stack)
        common_name_clean = sanitize_input(common_name)
        email_clean = sanitize_input(email, r"[^a-zA-Z0-9@._+-]")
        days_clean = sanitize_input(days, r"[^0-9]")

        cmd = [
            "/usr/bin/create_cert_admin.sh",
            fqdn,
            host,
            stack_clean,
            common_name_clean,
            password,
            days_clean,
            email_clean,
        ]
        logger.debug(f"Running command: {cmd}")

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            logger.error("create_cert_admin.sh execution timeout")
            return False

        if process.returncode != 0:
            logger.error(f"create_cert_admin.sh failed: {stderr.decode()}")
            return False

        logger.info(
            f"Certificate {common_name_clean} created. Stack {stack_clean}. {email_clean}"
        )
        return True

    except Exception as e:
        logger.error(f"Error executing create_cert_admin.sh: {e}")
        return False


async def revoke_admin_cert(common_name: str, stack: str) -> bool:
    """
    Revokes the user certificate identified by common_name in the specified stack.
    Updates the CRL to reflect the revocation.
    """

    cert_dir = PATH_CERTIFICATES / stack / "admin" / "certs"
    cert_file = f"{common_name}.crt"
    cert_path = cert_dir / cert_file

    if not cert_path.is_file():
        return False  # Certificate not exists

    try:
        resource_dir = PATH_CERTIFICATES / stack / "admin"

        # Revoke
        cmd_revoke = [
            "openssl",
            "ca",
            "-config",
            str(resource_dir / "openssl.cnf"),
            "-revoke",
            str(cert_path),
        ]
        process_revoke = await asyncio.create_subprocess_exec(
            *cmd_revoke, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process_revoke.communicate()

        if process_revoke.returncode != 0:
            logger.error("OpenSSL revoke command failed")
            return False

        # Renew CRL
        process_renew = await asyncio.create_subprocess_exec(
            "/usr/bin/renew_crl",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process_renew.communicate()

        if process_renew.returncode != 0:
            logger.error("renew_crl command failed")
            return False

        os.remove(cert_path)

        logger.info(
            f"Revoked certificate {common_name} at {cert_path} for stack {stack}"
        )
        return True

    except Exception as e:
        logger.error(f"Unexpected error during revocation: {e}")
        return False


async def create_computer_cert(
    fqdn: str,
    host: str,
    stack: str,
    common_name: str,
    password: str,
    days: str,
    email: str,
) -> bool:
    try:
        stack_clean = sanitize_input(stack)
        common_name_clean = sanitize_input(common_name)
        email_clean = sanitize_input(email or "", r"[^a-zA-Z0-9@._+-]")
        days_clean = sanitize_input(days, r"[^0-9]")
        password_safe = password or ""

        cmd = [
            "/usr/bin/create_cert_computer.sh",
            fqdn,
            host,
            stack_clean,
            common_name_clean,
            password_safe,
            days_clean,
            email_clean,
        ]
        logger.debug(f"Running command: {cmd}")

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            logger.error("create_cert_computer.sh execution timeout")
            return False

        if process.returncode != 0:
            logger.error(f"create_cert_computer.sh failed: {stderr.decode()}")
            return False

        logger.info(
            f"Certificate {common_name_clean} created. Stack {stack_clean}. {email_clean}"
        )
        return True

    except Exception as e:
        logger.error(f"Error executing create_cert_computer.sh: {e}")
        return False


async def revoke_computer_cert(common_name: str, stack: str) -> bool:
    cert_dir = PATH_CERTIFICATES / stack / "computer" / "certs"
    cert_file = f"{common_name}.crt"
    cert_path = cert_dir / cert_file

    if not cert_path.is_file():
        return False

    try:
        resource_dir = PATH_CERTIFICATES / stack / "computer"

        # Revoke
        cmd_revoke = [
            "openssl",
            "ca",
            "-config",
            str(resource_dir / "openssl.cnf"),
            "-revoke",
            str(cert_path),
        ]
        process_revoke = await asyncio.create_subprocess_exec(
            *cmd_revoke, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process_revoke.communicate()

        if process_revoke.returncode != 0:
            logger.error("OpenSSL revoke command failed")
            return False

        # Renew CRL
        process_renew = await asyncio.create_subprocess_exec(
            "/usr/bin/renew_crl",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process_renew.communicate()

        if process_renew.returncode != 0:
            logger.error("renew_crl command failed")
            return False

        os.remove(cert_path)

        logger.info(
            f"Revoked certificate {common_name} at {cert_path} for stack {stack}"
        )
        return True

    except Exception as e:
        logger.error(f"Unexpected error during revocation: {e}")
        return False
