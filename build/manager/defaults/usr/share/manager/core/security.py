import os
import subprocess
import secrets
import time
import logging
import re

from fastapi import HTTPException, Path
from datetime import datetime, timedelta

from core.config import PATH_CERTIFICATES, MAX_TOKEN_AGE_HOURS

logger = logging.getLogger(__name__)


def validate_stack_name(stack: str) -> str:
    """Validates that the stack name does not contain path traversal"""
    if not re.match(r'^[a-zA-Z0-9_-]+$', stack):
        raise HTTPException(
            status_code=400,
            detail="Stack name must contain only alphanumeric characters, hyphens, and underscores"
        )

    if '..' in stack or '/' in stack or '\\' in stack:
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

    def validate(self) -> tuple[str, str]:
        # Validación básica
        if not self.token or len(self.token) != 64:
            logger.warning(f"Invalid token format from stack {self.stack}")
            time.sleep(3)  # Timing attack mitigation
            raise HTTPException(status_code=401, detail="Invalid token")

        # Verificar existencia
        if not self.token_file.exists():
            logger.warning(f"Token not found: {self.token[:8]}... for stack {self.stack}")
            time.sleep(3)
            raise HTTPException(status_code=401, detail="Invalid token")

        # Verificar expiración por timestamp del archivo
        creation_time = datetime.fromtimestamp(self.token_file.stat().st_ctime)
        age = datetime.now() - creation_time

        if age > timedelta(hours=MAX_TOKEN_AGE_HOURS):
            logger.info(f"Expired token removed: {self.token[:8]}...")
            self.token_file.unlink(missing_ok=True)
            time.sleep(3)
            raise HTTPException(status_code=401, detail="Token expired")

        # Leer contenido
        try:
            content = self.token_file.read_text(encoding='utf-8').strip()
            parts = content.split('|')

            if len(parts) != 2:
                logger.error(f"Malformed token content in {self.token_file}")
                time.sleep(3)
                raise HTTPException(status_code=401, detail="Invalid token format")

            common_name, validity_days = parts

            # Validar campos
            int(validity_days)  # debe ser un entero

            return common_name, validity_days

        except (ValueError, OSError) as e:
            logger.error(f"Error reading token file: {e}")
            time.sleep(3)
            raise HTTPException(status_code=401, detail="Invalid token")

    def consume(self):
        """Deletes the token (single use)"""
        self.token_file.unlink(missing_ok=True)


def sanitize_input(value: str, allowed_chars: str = r'[^a-zA-Z0-9@._:-]') -> str:
    """Sanitizes input by removing dangerous characters"""
    return re.sub(allowed_chars, '', value)


def create_admin_cert(
    fqdn: str, host: str, stack: str, common_name: str, password: str,
    days: str, email: str
) -> bool:
    try:
        stack_clean = sanitize_input(stack)
        common_name_clean = sanitize_input(common_name)
        email_clean = sanitize_input(email, r'[^a-zA-Z0-9@._+-]')
        days_clean = sanitize_input(days, r'[^0-9]')

        cmd = [
            '/usr/bin/create_cert_admin.sh',
            fqdn,
            host,
            stack_clean,
            common_name_clean,
            password,
            days_clean,
            email_clean,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"create_cert_admin.sh failed: {result.stderr}")
            return False

        logger.info(f"Certificate created for {email_clean} in stack {stack_clean}")
        return True

    except subprocess.TimeoutExpired:
        logger.error("create_cert_admin.sh execution timeout")
        return False
    except Exception as e:
        logger.error(f"Error executing create_cert_admin.sh: {e}")
        return False


def revoke_admin_cert(common_name: str, stack: str) -> bool:
    """
    Revokes the user certificate identified by common_name in the specified stack.
    Updates the CRL to reflect the revocation.
    """

    cert_dir = PATH_CERTIFICATES / stack / "admin" / "certs"
    cert_file = f"{common_name}.crt"
    cert_path = cert_dir / cert_file

    if not cert_path.is_file():
        return False  # Certificado not exists

    try:
        resource_dir = PATH_CERTIFICATES / stack / "admin"
        # crl_file = resource_dir / "crl" / "crl.pem"

        # Revoke
        subprocess.run([
            "openssl", "ca", "-config", str(resource_dir / "openssl.cnf"),
            "-revoke", str(cert_path),
        ], check=True)

        # Renew CRL
        subprocess.run([
            "/usr/bin/renew_crl"
        ], check=True)

        os.remove(cert_path)

        logger.info(f"Revoked certificate {common_name} at {cert_path} for stack {stack}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"OpenSSL command failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during revocation: {e}")
        return False


def create_computer_cert(
    fqdn: str, host: str, stack: str, common_name: str, password: str,
    days: str, email: str
) -> bool:
    try:
        stack_clean = sanitize_input(stack)
        common_name_clean = sanitize_input(common_name)
        email_clean = sanitize_input(email, r'[^a-zA-Z0-9@._+-]')
        days_clean = sanitize_input(days, r'[^0-9]')

        cmd = [
            '/usr/bin/create_cert_computer.sh',
            fqdn,
            host,
            stack_clean,
            common_name_clean,
            password,
            days_clean,
            email_clean,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"create_cert_computer.sh failed: {result.stderr}")
            return False

        logger.info(f"Certificate created for {email_clean} in stack {stack_clean}")
        return True

    except subprocess.TimeoutExpired:
        logger.error("create_cert_computer.sh execution timeout")
        return False
    except Exception as e:
        logger.error(f"Error executing create_cert_computer.sh: {e}")
        return False


def revoke_computer_cert(common_name: str, stack: str) -> bool:
    cert_dir = PATH_CERTIFICATES / stack / "computer" / "certs"
    cert_file = f"{common_name}.crt"
    cert_path = cert_dir / cert_file

    if not cert_path.is_file():
        return False

    try:
        resource_dir = PATH_CERTIFICATES / stack / "computer"
        # crl_file = resource_dir / "crl" / "crl.pem"

        # Revoke
        subprocess.run([
            "openssl", "ca", "-config", str(resource_dir / "openssl.cnf"),
            "-revoke", str(cert_path),
        ], check=True)

        # Renew CRL
        subprocess.run([
            "/usr/bin/renew_crl"
        ], check=True)

        os.remove(cert_path)

        logger.info(f"Revoked certificate {common_name} at {cert_path} for stack {stack}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"OpenSSL command failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during revocation: {e}")
        return False
