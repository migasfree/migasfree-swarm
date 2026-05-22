import logging
import os
import httpx
import yaml
from fastapi import APIRouter, HTTPException, status, Response, Request
from core.config import MGI_TEMPLATES_GITHUB_URL, API_VERSION, CORE_TOKEN_URL
from core.database import get_db_connection
from core.core_client import get_project_by_id, get_cached_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_VERSION}/internal/mgi",
    tags=["mgi"],
)


async def _fetch_text(url: str) -> str:
    import time
    if "raw.githubusercontent.com" in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}t={int(time.time())}"
    logger.debug(f"Fetching text from URL: {url}")
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.text


@router.get("/catalog")
async def get_mgi_catalog():
    """Fetch the MGI templates catalog combining local and remote sources."""
    from core.config import local_templates_dir

    templates = []

    # 1. Fetch Local Catalog from filesystem directly
    local_catalog_file = local_templates_dir / "catalog.yml"
    if local_catalog_file.exists() and local_catalog_file.is_file():
        try:
            local_content = local_catalog_file.read_text(encoding="utf-8")
            local_data = yaml.safe_load(local_content)
            if isinstance(local_data, dict) and "templates" in local_data:
                for item in local_data["templates"]:
                    if isinstance(item, dict):
                        item_copy = dict(item)
                        item_copy["origin"] = "local"
                        templates.append(item_copy)
            logger.info(
                f"Loaded {len(templates)} local templates from {local_catalog_file}"
            )
        except Exception as e:
            logger.error(f"Error reading local catalog file: {e}")

    # 2. Fetch Remote Catalog from GitHub
    if MGI_TEMPLATES_GITHUB_URL:
        try:
            remote_url = f"{MGI_TEMPLATES_GITHUB_URL.rstrip('/')}/catalog.yml"
            remote_content = await _fetch_text(remote_url)
            remote_data = yaml.safe_load(remote_content)
            if isinstance(remote_data, dict) and "templates" in remote_data:
                remote_count = 0
                for item in remote_data["templates"]:
                    if isinstance(item, dict):
                        item_copy = dict(item)
                        item_copy["origin"] = "remote"
                        templates.append(item_copy)
                        remote_count += 1
                logger.info(
                    f"Fetched {remote_count} remote templates from {remote_url}"
                )
        except Exception as e:
            logger.error(f"Error fetching remote catalog: {e}")

    return {"templates": templates}


@router.get("/templates/{template_id:path}")
async def get_mgi_template(
    template_id: str,
    origin: str = None,
):
    """Fetch the full content of a specific MGI template.
    Checks local pool first if origin is local or not specified,
    then falls back to GitHub registry if origin is remote or not specified.
    Returns best-effort response (null content) if not found.
    """
    from core.config import local_templates_dir

    # 1. Check local filesystem (pool/project-templates/{template_id}/)
    if origin != "remote":
        local_dir = local_templates_dir / template_id
        if local_dir.exists() and local_dir.is_dir():
            dockerfile = None
            partition = None
            deployments = None
            base_os = None
            try:
                dockerfile = local_dir.joinpath("dockerfile.j2").read_text(
                    encoding="utf-8"
                )
            except Exception:
                pass
            try:
                partition = local_dir.joinpath("partition.yml").read_text(
                    encoding="utf-8"
                )
            except Exception:
                pass
            try:
                deployments = local_dir.joinpath("deployments.yml").read_text(
                    encoding="utf-8"
                )
            except Exception:
                pass
            try:
                catalog_file = local_templates_dir / "catalog.yml"
                if catalog_file.exists() and catalog_file.is_file():
                    catalog_data = yaml.safe_load(
                        catalog_file.read_text(encoding="utf-8")
                    )
                    if isinstance(catalog_data, dict):
                        for t in catalog_data.get("templates", []):
                            if t.get("id") == template_id:
                                base_os = t.get("base_os")
                                break
            except Exception:
                pass
            return {
                "id": template_id,
                "base_os": base_os,
                "dockerfile": dockerfile,
                "partition": partition,
                "deployments": deployments,
            }

    # 2. Fallback: try GitHub registry (skip proxy — only local filesystem or canonical source)
    if origin != "local" and MGI_TEMPLATES_GITHUB_URL:
        try:
            base_url = MGI_TEMPLATES_GITHUB_URL.rstrip("/")
            catalog_content = await _fetch_text(f"{base_url}/catalog.yml")
            catalog = yaml.safe_load(catalog_content)
            if isinstance(catalog, dict):
                template_info = next(
                    (
                        t
                        for t in catalog.get("templates", [])
                        if t.get("id") == template_id
                    ),
                    None,
                )
                if template_info:
                    base_path = f"{base_url}/{template_id}"
                    dockerfile = await _fetch_text(f"{base_path}/dockerfile.j2")
                    partition = await _fetch_text(f"{base_path}/partition.yml")
                    deployments = None
                    try:
                        deployments = await _fetch_text(f"{base_path}/deployments.yml")
                    except Exception:
                        pass
                    return {
                        "id": template_id,
                        "base_os": template_info.get("base_os"),
                        "dockerfile": dockerfile,
                        "partition": partition,
                        "deployments": deployments,
                    }
        except Exception as e:
            logger.exception(f"Failed to fetch remote template '{template_id}' from GitHub: {e}")

    # 3. Not found anywhere — return minimal response so Core can continue
    return {
        "id": template_id,
        "base_os": None,
        "dockerfile": None,
        "partition": None,
        "deployments": None,
    }


@router.get("/projects/{project_id}/export")
async def export_deployments(
    project_id: int,
    request: Request,
):
    """
    Export all internal and external deployments of a project in YAML/JSON format.
    - Uses distinct schemas for internal and external deployments.
    - Attributes are exported as prefix-value string lists, e.g. ["SET-All Systems"].
    - Resolves store and available packages for internal deployments.
    - Only exports relevant fields.
    - Also exports applications associated with the project.
    """
    # 1. Verify project exists
    try:
        project = await get_project_by_id(project_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found: {str(e)}",
        )

    deployments = []

    # 2. Query all deployments of this project
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, enabled, comment, packages_to_install, packages_to_remove,
                           source, base_url, options, suite, components, frozen, expire,
                           default_preincluded_packages, default_included_packages, default_excluded_packages
                    FROM core_deployment
                    WHERE project_id = %s
                    ORDER BY id ASC
                """,
                    (project_id,),
                )

                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

                for row in rows:
                    dep = dict(zip(columns, row))
                    dep_id = dep["id"]
                    source = dep["source"]

                    # A. Fetch prefix-value attributes linked to this deployment
                    cur.execute(
                        """
                        SELECT p.prefix, a.value
                        FROM core_deployment_included_attributes dia
                        JOIN core_attribute a ON dia.attribute_id = a.id
                        JOIN core_property p ON a.property_att_id = p.id
                        WHERE dia.deployment_id = %s
                    """,
                        (dep_id,),
                    )
                    attrs = cur.fetchall()
                    included_attrs = [f"{r[0]}-{r[1]}" for r in attrs]

                    # B. Build deployment dict according to source type (Internal vs External)
                    d = {"name": dep["name"], "enabled": dep["enabled"]}

                    if source == "E":
                        # External Deployment Schema
                        d.update(
                            {
                                "base_url": dep["base_url"],
                                "suite": dep["suite"],
                                "components": dep["components"],
                                "options": dep["options"],
                                "frozen": dep["frozen"],
                                "included_attributes": included_attrs,
                                "source": "E",
                            }
                        )
                    else:
                        # Internal Deployment Schema
                        # Check comment and ignore placeholder or template prefix
                        comment = dep["comment"] or ""

                        # Fetch available packagesets associated
                        cur.execute(
                            """
                            SELECT pks.name FROM core_deployment_available_package_sets daps
                            JOIN core_packageset pks ON daps.packageset_id = pks.id
                            WHERE daps.deployment_id = %s
                        """,
                            (dep_id,),
                        )
                        pk_sets = cur.fetchall()

                        # Fetch available packages associated
                        cur.execute(
                            """
                            SELECT pk.name FROM core_deployment_available_packages dap
                            JOIN core_package pk ON dap.package_id = pk.id
                            WHERE dap.deployment_id = %s
                        """,
                            (dep_id,),
                        )
                        pks = cur.fetchall()

                        if pk_sets:
                            available_packages = pk_sets[0][
                                0
                            ]  # Use first packageset name as string
                        elif pks:
                            available_packages = [
                                p[0] for p in pks
                            ]  # List of package names
                        else:
                            available_packages = []

                        # Package fields as clean lists of strings
                        packages_to_install = (
                            [
                                p.strip()
                                for p in dep["packages_to_install"].split("\n")
                                if p.strip()
                            ]
                            if dep["packages_to_install"]
                            else []
                        )
                        packages_to_remove = (
                            [
                                p.strip()
                                for p in dep["packages_to_remove"].split("\n")
                                if p.strip()
                            ]
                            if dep["packages_to_remove"]
                            else []
                        )

                        # Resolve store: check store of packageset / package first, fallback to first store in project
                        store_slug = "thirds"
                        cur.execute(
                            """
                            SELECT s.slug FROM core_store s
                            WHERE s.project_id = %s
                            LIMIT 1
                        """,
                            (project_id,),
                        )
                        store_row = cur.fetchone()
                        if store_row:
                            store_slug = store_row[0]

                        if pk_sets:
                            cur.execute(
                                """
                                SELECT s.slug FROM core_packageset pks
                                JOIN core_store s ON pks.store_id = s.id
                                WHERE pks.name = %s AND pks.project_id = %s
                            """,
                                (pk_sets[0][0], project_id),
                            )
                            pks_store = cur.fetchone()
                            if pks_store:
                                store_slug = pks_store[0]
                        elif pks:
                            cur.execute(
                                """
                                SELECT s.slug FROM core_package pk
                                JOIN core_store s ON pk.store_id = s.id
                                WHERE pk.name = %s AND pk.project_id = %s
                                LIMIT 1
                            """,
                                (pks[0][0], project_id),
                            )
                            pk_store = cur.fetchone()
                            if pk_store:
                                store_slug = pk_store[0]

                        d.update(
                            {
                                "comment": comment,
                                "available_packages": available_packages,
                                "packages_to_install": packages_to_install,
                                "packages_to_remove": packages_to_remove,
                                "included_attributes": included_attrs,
                                "store": store_slug,
                                "source": "I",
                            }
                        )

                    deployments.append(d)

    except Exception as e:
        logger.error(f"Error exporting deployments for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during deployments export: {str(e)}",
        )

    # 3. Query all applications of this project
    applications = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT a.id, a.name, a.description, a.score, a.icon, a.level, c.name AS category_name, pbp.packages_to_install
                    FROM app_catalog_packagesbyproject pbp
                    JOIN app_catalog_application a ON pbp.application_id = a.id
                    JOIN app_catalog_category c ON a.category_id = c.id
                    WHERE pbp.project_id = %s
                    ORDER BY a.id ASC
                """,
                    (project_id,),
                )

                app_rows = cur.fetchall()
                for app_row in app_rows:
                    (
                        app_id,
                        app_name,
                        app_desc,
                        app_score,
                        app_icon,
                        app_level,
                        category_name,
                        packages_to_install,
                    ) = app_row

                    # Fetch attributes linked to this application
                    cur.execute(
                        """
                        SELECT p.prefix, att.value
                        FROM app_catalog_application_available_for_attributes aaa
                        JOIN core_attribute att ON aaa.attribute_id = att.id
                        JOIN core_property p ON att.property_att_id = p.id
                        WHERE aaa.application_id = %s
                    """,
                        (app_id,),
                    )
                    attrs = cur.fetchall()
                    available_attrs = [f"{r[0]}-{r[1]}" for r in attrs]

                    # Package fields as clean lists of strings
                    packages_list = (
                        [
                            p.strip()
                            for p in packages_to_install.split("\n")
                            if p.strip()
                        ]
                        if packages_to_install
                        else []
                    )

                    applications.append(
                        {
                            "name": app_name,
                            "description": app_desc,
                            "score": app_score,
                            "icon": app_icon,
                            "level": app_level,
                            "category": category_name,
                            "packages_to_install": packages_list,
                            "available_for_attributes": available_attrs,
                        }
                    )
    except Exception as e:
        logger.error(f"Error exporting applications for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during applications export: {str(e)}",
        )

    # Wrap deployments and applications in a standard dict/YAML envelope (for HTTP response)
    export_data = {"deployments": deployments, "applications": applications}
    yaml_content = yaml.safe_dump(
        export_data, default_flow_style=False, sort_keys=False, allow_unicode=True
    )

    # Build separate YAML content for the deployments.yml file (without applications)
    deployments_yaml = yaml.safe_dump(
        {"deployments": deployments},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    # Save deployments.yml, stores.yml, packages.yml, and applications.yml to pool/project-templates
    try:
        from core.config import local_templates_dir

        # 1. Query template_id, config, partition, base_os, build_type, provision_script, image_format for project_id from mgi_config
        template_id = None
        dockerfile_content = None
        partition_content = None
        base_os = None
        build_type = "docker"
        provision_script = ""
        image_format = "raw"
        config_data = {}

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT template_id, config, partition, base_os, build_type, provision_script, image_format FROM mgi_config WHERE project_id = %s",
                    (project_id,),
                )
                row = cur.fetchone()
                if row:
                    (
                        template_id,
                        config_val,
                        partition_content,
                        base_os,
                        build_type,
                        provision_script,
                        image_format,
                    ) = row

                    import json

                    if config_val:
                        if isinstance(config_val, str):
                            config_data = json.loads(config_val)
                        elif isinstance(config_val, dict):
                            config_data = config_val

                    if build_type == "docker":
                        dockerfile_content = config_data.get("dockerfile")

        # 2. Use template_id as directory name directly (no catalog lookup needed)
        template_path = template_id or project.get("slug")

        if template_path:
            dest_dir = local_templates_dir / template_path
            dest_dir.mkdir(parents=True, exist_ok=True)

            # A. Save deployments.yml (deployments only, preserving original structure)
            dest_file = dest_dir / "deployments.yml"
            dest_file.write_text(deployments_yaml, encoding="utf-8")
            logger.info(f"Exported deployments saved to {dest_file}")

            if build_type == "docker" and dockerfile_content:
                dockerfile_file = dest_dir / "dockerfile.j2"
                dockerfile_file.write_text(dockerfile_content, encoding="utf-8")
                logger.info(f"Exported dockerfile.j2 saved to {dockerfile_file}")
            elif build_type == "qemu_win":
                autounattend_content = config_data.get("autounattend_template")
                setupcomplete_content = config_data.get("setupcomplete_template")
                if autounattend_content:
                    autounattend_file = dest_dir / "autounattend.xml.j2"
                    autounattend_file.write_text(autounattend_content, encoding="utf-8")
                    logger.info(
                        f"Exported autounattend.xml.j2 saved to {autounattend_file}"
                    )
                if setupcomplete_content:
                    setupcomplete_file = dest_dir / "setupcomplete.cmd.j2"
                    setupcomplete_file.write_text(
                        setupcomplete_content, encoding="utf-8"
                    )
                    logger.info(
                        f"Exported setupcomplete.cmd.j2 saved to {setupcomplete_file}"
                    )
                if provision_script:
                    provision_file = dest_dir / "provision-migasfree.ps1.j2"
                    provision_file.write_text(provision_script, encoding="utf-8")
                    logger.info(
                        f"Exported provision-migasfree.ps1.j2 saved to {provision_file}"
                    )

            if partition_content:
                partition_file = dest_dir / "partition.yml"
                partition_file.write_text(partition_content, encoding="utf-8")
                logger.info(f"Exported partition.yml saved to {partition_file}")

            # B. Export Stores to stores.yml
            stores = []
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name, slug FROM core_store WHERE project_id = %s",
                        (project_id,),
                    )
                    for s_name, s_slug in cur.fetchall():
                        stores.append({"name": s_name, "slug": s_slug})
            stores_file = dest_dir / "stores.yml"
            stores_file.write_text(
                yaml.safe_dump(
                    {"stores": stores},
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )
            logger.info(f"Exported stores saved to {stores_file}")

            # C. Export Package Metadata to packages.yml
            packages = []
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT pk.fullname, pk.name, pk.version, pk.architecture, s.slug AS store_slug, pr.slug AS project_slug
                        FROM core_package pk
                        JOIN core_store s ON pk.store_id = s.id
                        JOIN core_project pr ON pk.project_id = pr.id
                        WHERE pk.project_id = %s AND pk.store_id IS NOT NULL
                    """,
                        (project_id,),
                    )
                    for (
                        fullname,
                        name,
                        version,
                        architecture,
                        store_slug,
                        project_slug,
                    ) in cur.fetchall():
                        packages.append(
                            {
                                "fullname": fullname,
                                "name": name,
                                "version": version,
                                "architecture": architecture,
                                "store": store_slug,
                                "project_slug": project_slug,
                            }
                        )
            packages_file = dest_dir / "packages.yml"
            packages_file.write_text(
                yaml.safe_dump(
                    {"packages": packages},
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )
            logger.info(f"Exported packages metadata saved to {packages_file}")

            # D. Export Applications to applications.yml
            apps_file = dest_dir / "applications.yml"
            apps_file.write_text(
                yaml.safe_dump(
                    {"applications": applications},
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )
            logger.info(f"Exported applications metadata saved to {apps_file}")

            # E. Download and save physical package files via API
            for pkg in packages:
                # Construct backend API download URL
                pkg_url = f"http://public/public/{pkg['project_slug']}/stores/{pkg['store']}/{pkg['fullname']}"
                pkg_dest = dest_dir / "stores" / pkg["store"] / pkg["fullname"]
                pkg_dest.parent.mkdir(parents=True, exist_ok=True)

                try:
                    logger.info(f"Downloading package from {pkg_url} to {pkg_dest}")
                    async with httpx.AsyncClient(verify=False) as client:
                        response = await client.get(pkg_url, timeout=60.0)
                        if response.status_code == 200:
                            pkg_dest.write_bytes(response.content)
                            logger.info(
                                f"Successfully downloaded package {pkg['fullname']}"
                            )
                        else:
                            logger.error(
                                f"Failed to download package {pkg['fullname']}: HTTP {response.status_code}"
                            )
                except Exception as ex:
                    logger.error(f"Error downloading package {pkg['fullname']}: {ex}")

            # F. Download and save application icon files
            for app in applications:
                icon_path = app.get("icon")
                if not icon_path:
                    continue
                # icon_path is like "catalog_icons/app_2.png"
                icon_url = f"http://public/public/{icon_path}"
                icon_dest = dest_dir / "icons" / os.path.basename(icon_path)
                icon_dest.parent.mkdir(parents=True, exist_ok=True)

                try:
                    logger.info(f"Downloading icon from {icon_url} to {icon_dest}")
                    async with httpx.AsyncClient(verify=False) as client:
                        response = await client.get(icon_url, timeout=30.0)
                        if response.status_code == 200:
                            icon_dest.write_bytes(response.content)
                            logger.info(f"Successfully downloaded icon {icon_path}")
                        else:
                            logger.error(
                                f"Failed to download icon {icon_path}: HTTP {response.status_code}"
                            )
                except Exception as ex:
                    logger.error(f"Error downloading icon {icon_path}: {ex}")

            # G. Set ownership for the entire project-templates tree
            try:
                import subprocess

                subprocess.run(
                    ["chown", "-R", "890:890", str(local_templates_dir)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logger.info(f"Ownership set to 890:890 on {local_templates_dir}")
            except Exception as own_err:
                logger.error(
                    f"Failed to set ownership on {local_templates_dir}: {own_err}"
                )

            # H. Update local catalog.yml with this template entry
            try:
                catalog_file = local_templates_dir / "catalog.yml"
                if catalog_file.exists() and catalog_file.is_file():
                    local_catalog = (
                        yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
                    )
                else:
                    local_catalog = {}
                if not isinstance(local_catalog, dict):
                    local_catalog = {}
                templates = local_catalog.get("templates", [])
                # Upsert: add or update entry for this template_id
                existing = next(
                    (t for t in templates if t.get("id") == template_id), None
                )
                entry = {"id": template_id}
                if base_os:
                    entry["base_os"] = base_os
                if existing:
                    templates[templates.index(existing)] = entry
                else:
                    templates.append(entry)
                local_catalog["templates"] = templates
                local_templates_dir.mkdir(parents=True, exist_ok=True)
                catalog_file.write_text(
                    yaml.safe_dump(
                        local_catalog,
                        default_flow_style=False,
                        sort_keys=False,
                        allow_unicode=True,
                    ),
                    encoding="utf-8",
                )
                logger.info(f"Updated local catalog.yml with template '{template_id}'")
            except Exception as catalog_err:
                logger.error(f"Failed to update local catalog.yml: {catalog_err}")

    except Exception as e:
        logger.error(
            f"Failed to save deployments, stores, packages, and applications to template directory: {e}"
        )

    accept = request.headers.get("accept", "")
    if "text/yaml" in accept or "application/x-yaml" in accept:
        return Response(content=yaml_content, media_type="text/yaml")
    import json

    return Response(
        content=json.dumps(export_data, ensure_ascii=False),
        media_type="application/json",
    )


@router.post("/projects/{project_id}/import")
async def import_deployments(
    project_id: int,
    request: Request,
    template_id: str = None,
    origin: str = None,
):
    """
    Import deployments and applications from a YAML request body into the specified project.
    - Idempotent: Updates existing deployments/applications and creates new ones.
    - Resolves prefix-value attributes dynamically.
    - Resolves store and available packages for internal deployments.
    """
    template_path = None

    # Helper to format package fields as list of strings (since Django core serializer does join on them)
    def parse_packages_list(val):
        if not val:
            return []
        if isinstance(val, list):
            return val
        return [p.strip() for p in val.split("\n") if p.strip()]

    # 1. Parse and validate YAML payload
    body = await request.body()
    payload = None
    if body and body.strip():
        try:
            payload = yaml.safe_load(body)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid YAML format: {str(e)}",
            )

    # 2. If no payload was provided, try to load deployments.yml from the template directory
    if not payload:
        try:
            from core.config import (
                local_templates_dir,
                MGI_TEMPLATES_URL,
                MGI_TEMPLATES_GITHUB_URL,
            )

            # A. Query template_id for project_id from mgi_config if not provided
            if not template_id:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT template_id FROM mgi_config WHERE project_id = %s",
                            (project_id,),
                        )
                        row = cur.fetchone()
                        if row:
                            template_id = row[0]

            # B. Use template_id as directory name directly (no catalog lookup needed)
            template_path = template_id

            # C. If template path is found, try to read deployments.yml from it
            yaml_content = None
            if template_path:
                if origin != "remote":
                    local_file = local_templates_dir / template_path / "deployments.yml"
                    if local_file.exists() and local_file.is_file():
                        yaml_content = local_file.read_text(encoding="utf-8")

                if not yaml_content and origin != "local":
                    for fallback_url in [MGI_TEMPLATES_URL, MGI_TEMPLATES_GITHUB_URL]:
                        if not fallback_url:
                            continue
                        if (
                            origin == "remote"
                            and fallback_url == MGI_TEMPLATES_URL
                            and MGI_TEMPLATES_URL != MGI_TEMPLATES_GITHUB_URL
                        ):
                            continue
                        try:
                            base_url = fallback_url.rstrip("/")
                            url = f"{base_url}/{template_path}/deployments.yml"
                            yaml_content = await _fetch_text(url)
                            if yaml_content:
                                logger.info(f"Loaded deployments.yml from {url}")
                                break
                        except Exception:
                            continue

            if yaml_content:
                payload = yaml.safe_load(yaml_content)
                logger.info(
                    f"Successfully loaded deployments template for project {project_id} from {template_path or 'registry'}"
                )
            else:
                # D. If no template resolved, check fallback using project's slug
                project = await get_project_by_id(project_id)
                project_slug = project.get("slug")
                local_file = local_templates_dir / project_slug / "deployments.yml"
                if local_file.exists() and local_file.is_file():
                    yaml_content = local_file.read_text(encoding="utf-8")
                    payload = yaml.safe_load(yaml_content)
                    logger.info(
                        f"Successfully loaded deployments from project slug fallback for project {project_id}"
                    )

            # E. Load applications.yml from the same template directory and merge into payload
            apps_file = None
            if template_path and origin != "remote":
                apps_file = local_templates_dir / template_path / "applications.yml"
            if (not apps_file or not apps_file.exists()) and origin != "remote":
                try:
                    proj = await get_project_by_id(project_id)
                    apps_file = (
                        local_templates_dir / proj.get("slug", "") / "applications.yml"
                    )
                except Exception:
                    pass
            if apps_file and apps_file.exists() and apps_file.is_file():
                try:
                    apps_data = yaml.safe_load(apps_file.read_text(encoding="utf-8"))
                    if isinstance(apps_data, dict) and "applications" in apps_data:
                        if payload is None:
                            payload = {}
                        payload.setdefault("applications", apps_data["applications"])
                        logger.info(f"Loaded applications from {apps_file}")
                except Exception as e:
                    logger.error(f"Error loading applications from {apps_file}: {e}")

        except Exception as e:
            logger.error(
                f"Error resolving template deployments for project {project_id}: {e}"
            )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty payload and no template deployments found for this project.",
        )

    # Support both wrapped dict and flat list formats
    deployments = []
    applications = []
    if isinstance(payload, dict):
        if "deployments" in payload:
            deployments = payload["deployments"]
        if "applications" in payload:
            applications = payload["applications"]
    elif isinstance(payload, list):
        deployments = payload
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid structure: expected a list of deployments or a dictionary with a 'deployments' key.",
        )

    # 2b. Verify project exists
    try:
        await get_project_by_id(project_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found: {str(e)}",
        )

    token = get_cached_token()
    headers = {
        "accept": "application/json",
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    created_count = 0
    updated_count = 0
    app_created_count = 0
    app_updated_count = 0
    stores_created = 0
    packages_created = 0
    errors = []

    # 3. Resolve template directory and import Stores, Packages and Applications before importing deployments
    try:
        from core.config import local_templates_dir, PATH_DATASHARES, STACK
        import shutil

        # A. Determine template directory path
        template_dir = None
        if template_path:
            template_dir = local_templates_dir / template_path
        else:
            project_obj = await get_project_by_id(project_id)
            project_slug = project_obj.get("slug")
            template_dir = local_templates_dir / project_slug

        logger.info(
            f"Import: template_dir={template_dir}, exists={template_dir.exists() if template_dir else False}"
        )
        if template_dir and template_dir.exists():
            # B. Import Stores from stores.yml
            stores_file = template_dir / "stores.yml"
            if stores_file.exists() and stores_file.is_file():
                try:
                    stores_data = yaml.safe_load(
                        stores_file.read_text(encoding="utf-8")
                    )
                    if isinstance(stores_data, dict) and "stores" in stores_data:
                        for store in stores_data["stores"]:
                            s_name = store.get("name")
                            s_slug = store.get("slug")
                            if s_name and s_slug:
                                with get_db_connection() as conn:
                                    with conn.cursor() as cur:
                                        cur.execute(
                                            "SELECT id FROM core_store WHERE project_id = %s AND LOWER(slug) = LOWER(%s)",
                                            (project_id, s_slug),
                                        )
                                        row = cur.fetchone()
                                        if not row:
                                            logger.info(
                                                f"Creating missing store '{s_name}' for project {project_id}"
                                            )
                                            cur.execute(
                                                "INSERT INTO core_store (name, slug, project_id) VALUES (%s, %s, %s)",
                                                (s_name, s_slug, project_id),
                                            )
                                            conn.commit()
                                            stores_created += 1
                except Exception as ex:
                    logger.error(f"Error importing stores from {stores_file}: {ex}")

            # C. Import Packages from packages.yml and copy physical .deb files
            packages_file = template_dir / "packages.yml"
            if packages_file.exists() and packages_file.is_file():
                try:
                    packages_data = yaml.safe_load(
                        packages_file.read_text(encoding="utf-8")
                    )
                    if isinstance(packages_data, dict) and "packages" in packages_data:
                        target_project = await get_project_by_id(project_id)
                        target_slug = target_project.get("slug")

                        for pkg in packages_data["packages"]:
                            fullname = pkg.get("fullname")
                            name = pkg.get("name")
                            version = pkg.get("version")
                            arch = pkg.get("architecture")
                            store_slug = pkg.get("store")

                            if not (
                                fullname and name and version and arch and store_slug
                            ):
                                continue

                            # C1. Physical copy of .deb file to destination public store folder
                            src_pkg = template_dir / "stores" / store_slug / fullname
                            if src_pkg.exists() and src_pkg.is_file():
                                dest_pkg_dir = (
                                    PATH_DATASHARES
                                    / STACK
                                    / "public"
                                    / target_slug
                                    / "stores"
                                    / store_slug
                                )
                                dest_pkg_dir.mkdir(parents=True, exist_ok=True)
                                dest_pkg = dest_pkg_dir / fullname
                                shutil.copy2(src_pkg, dest_pkg)
                                logger.info(
                                    f"Copied imported package {fullname} to {dest_pkg}"
                                )
                            else:
                                logger.warning(
                                    f"Import package file {src_pkg} not found in template"
                                )

                            # C2. Register package in core_package database table
                            with get_db_connection() as conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "SELECT id FROM core_store WHERE project_id = %s AND LOWER(slug) = LOWER(%s)",
                                        (project_id, store_slug),
                                    )
                                    store_row = cur.fetchone()
                                    if store_row:
                                        t_store_id = store_row[0]
                                        cur.execute(
                                            "SELECT id FROM core_package WHERE project_id = %s AND store_id = %s AND fullname = %s",
                                            (project_id, t_store_id, fullname),
                                        )
                                        pkg_row = cur.fetchone()
                                        if not pkg_row:
                                            logger.info(
                                                f"Registering package {fullname} in DB for project {project_id}"
                                            )
                                            cur.execute(
                                                "INSERT INTO core_package (fullname, name, version, architecture, project_id, store_id) VALUES (%s, %s, %s, %s, %s, %s)",
                                                (
                                                    fullname,
                                                    name,
                                                    version,
                                                    arch,
                                                    project_id,
                                                    t_store_id,
                                                ),
                                            )
                                            conn.commit()
                                            packages_created += 1
                except Exception as ex:
                    logger.error(f"Error importing packages from {packages_file}: {ex}")

            # D. Import Applications from applications.yml if not already provided in the payload
            if not applications:
                apps_file = template_dir / "applications.yml"
                if apps_file.exists() and apps_file.is_file():
                    try:
                        apps_data = yaml.safe_load(
                            apps_file.read_text(encoding="utf-8")
                        )
                        if isinstance(apps_data, dict) and "applications" in apps_data:
                            applications = apps_data["applications"]
                            logger.info(
                                f"Loaded applications from template {apps_file}"
                            )
                    except Exception as ex:
                        logger.error(
                            f"Error importing applications from {apps_file}: {ex}"
                        )
    except Exception as ex:
        logger.error(
            f"Error during stores, packages, and applications resolution: {ex}"
        )

    # 3b. Update mgi_config with template metadata (dockerfile, partition, base_os)
    try:
        from core.config import local_templates_dir

        dockerfile_content = None
        partition_content = None
        base_os_value = None
        resolved_template_id = template_id or template_path

        # Try to get from payload first
        if payload and isinstance(payload, dict):
            if not dockerfile_content:
                dockerfile_content = payload.get("dockerfile")
            if not partition_content:
                partition_content = payload.get("partition")
            if not base_os_value:
                base_os_value = payload.get("base_os")
            if not resolved_template_id:
                resolved_template_id = payload.get("template_id")

        # If not in payload, try template directory files
        if template_path:
            template_dir_mgi = local_templates_dir / template_path
        else:
            try:
                project_obj = await get_project_by_id(project_id)
                project_slug = project_obj.get("slug")
                template_dir_mgi = local_templates_dir / project_slug
            except Exception:
                template_dir_mgi = None

        autounattend_content = None
        setupcomplete_content = None
        provision_content = None
        build_type = "docker"
        image_format = "raw"

        if origin != "remote" and template_dir_mgi and template_dir_mgi.exists():
            autounattend_file = template_dir_mgi / "autounattend.xml.j2"
            setupcomplete_file = template_dir_mgi / "setupcomplete.cmd.j2"
            provision_file = template_dir_mgi / "provision-migasfree.ps1.j2"

            if (
                autounattend_file.exists()
                or setupcomplete_file.exists()
                or provision_file.exists()
            ):
                build_type = "qemu_win"
                image_format = "wim"
                if autounattend_file.exists():
                    autounattend_content = autounattend_file.read_text(encoding="utf-8")
                if setupcomplete_file.exists():
                    setupcomplete_content = setupcomplete_file.read_text(
                        encoding="utf-8"
                    )
                if provision_file.exists():
                    provision_content = provision_file.read_text(encoding="utf-8")

            if not dockerfile_content and build_type == "docker":
                dfile = template_dir_mgi / "dockerfile.j2"
                if dfile.exists() and dfile.is_file():
                    dockerfile_content = dfile.read_text(encoding="utf-8")
            if not partition_content:
                pfile = template_dir_mgi / "partition.yml"
                if pfile.exists() and pfile.is_file():
                    partition_content = pfile.read_text(encoding="utf-8")
            if not base_os_value and resolved_template_id:
                catalog_file = local_templates_dir / "catalog.yml"
                if catalog_file.exists() and catalog_file.is_file():
                    try:
                        catalog_data = yaml.safe_load(
                            catalog_file.read_text(encoding="utf-8")
                        )
                        if isinstance(catalog_data, dict):
                            for t in catalog_data.get("templates", []):
                                if t.get("id") == resolved_template_id:
                                    base_os_value = t.get("base_os")
                                    break
                    except Exception:
                        pass

        # If origin is remote or fallback is needed, fetch template metadata from remote URLs
        if origin != "local" and resolved_template_id:
            from core.config import MGI_TEMPLATES_GITHUB_URL, MGI_TEMPLATES_URL
            urls_to_try = []
            for curl in [MGI_TEMPLATES_GITHUB_URL, MGI_TEMPLATES_URL]:
                if curl:
                    urls_to_try.append(curl.rstrip("/"))

            # Fetch dockerfile from remote
            if not dockerfile_content and build_type == "docker":
                for base_url in urls_to_try:
                    try:
                        url = f"{base_url}/{resolved_template_id}/dockerfile.j2"
                        dockerfile_content = await _fetch_text(url)
                        if dockerfile_content:
                            break
                    except Exception:
                        continue

            # Fetch partition from remote
            if not partition_content:
                for base_url in urls_to_try:
                    try:
                        url = f"{base_url}/{resolved_template_id}/partition.yml"
                        partition_content = await _fetch_text(url)
                        if partition_content:
                            break
                    except Exception:
                        continue

            # Fetch base_os from remote catalog
            if not base_os_value:
                for base_url in urls_to_try:
                    try:
                        catalog_content = await _fetch_text(f"{base_url}/catalog.yml")
                        catalog_data = yaml.safe_load(catalog_content)
                        if isinstance(catalog_data, dict):
                            for t in catalog_data.get("templates", []):
                                if t.get("id") == resolved_template_id:
                                    base_os_value = t.get("base_os")
                                    break
                        if base_os_value:
                            break
                    except Exception:
                        continue

        # Upsert mgi_config
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, config FROM mgi_config WHERE project_id = %s",
                    (project_id,),
                )
                existing = cur.fetchone()

                if build_type == "docker":
                    target_cfg = {"dockerfile": dockerfile_content or ""}
                else:
                    target_cfg = {
                        "autounattend_template": autounattend_content or "",
                        "setupcomplete_template": setupcomplete_content or "",
                        "disk_size_gb": 40,
                        "vm_ram_mb": 4096,
                        "vm_cpus": 4,
                    }

                import json

                if existing:
                    existing_id, existing_cfg_raw = existing
                    existing_cfg = {}
                    if existing_cfg_raw:
                        if isinstance(existing_cfg_raw, str):
                            existing_cfg = json.loads(existing_cfg_raw)
                        elif isinstance(existing_cfg_raw, dict):
                            existing_cfg = existing_cfg_raw
                    existing_cfg.update(target_cfg)

                    updates = []
                    params = []
                    updates.append("config = %s")
                    params.append(json.dumps(existing_cfg))
                    updates.append("build_type = %s")
                    params.append(build_type)
                    updates.append("image_format = %s")
                    params.append(image_format)
                    if provision_content is not None:
                        updates.append("provision_script = %s")
                        params.append(provision_content)
                    if partition_content is not None:
                        updates.append("partition = %s")
                        params.append(partition_content)
                    if base_os_value is not None:
                        updates.append("base_os = %s")
                        params.append(base_os_value)
                    if resolved_template_id is not None:
                        updates.append("template_id = %s")
                        params.append(resolved_template_id)

                    if updates:
                        params.append(project_id)
                        cur.execute(
                            f"UPDATE mgi_config SET {', '.join(updates)} WHERE project_id = %s",
                            params,
                        )
                        conn.commit()
                        logger.info(f"Updated mgi_config for project {project_id}")
                else:
                    cur.execute(
                        "INSERT INTO mgi_config (project_id, template_id, config, partition, base_os, build_type, image_format, provision_script) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            project_id,
                            resolved_template_id,
                            json.dumps(target_cfg),
                            partition_content or "",
                            base_os_value or "",
                            build_type,
                            image_format,
                            provision_content or "",
                        ),
                    )
                    conn.commit()
                    logger.info(f"Created mgi_config for project {project_id}")
    except Exception as ex:
        logger.error(f"Error updating mgi_config for project {project_id}: {ex}")

    # 4. Process Applications Import
    for idx, app in enumerate(applications):
        if not isinstance(app, dict):
            errors.append(f"Application at index {idx} is not a valid dictionary.")
            continue

        name = app.get("name")
        if not name:
            errors.append(
                f"Application at index {idx} is missing the required 'name' field."
            )
            continue

        try:
            # A. Resolve Category
            category_name = app.get("category", "Accessories")
            category_id = None
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM app_catalog_category WHERE LOWER(name) = LOWER(%s)",
                        (category_name,),
                    )
                    row = cur.fetchone()
                    if row:
                        category_id = row[0]
                    else:
                        logger.info(
                            f"Creating missing application category '{category_name}'"
                        )
                        cur.execute(
                            "INSERT INTO app_catalog_category (name) VALUES (%s) RETURNING id",
                            (category_name,),
                        )
                        category_id = cur.fetchone()[0]
                        conn.commit()

            # B. Resolve Attributes
            attr_ids = []
            available_attrs = app.get("available_for_attributes", [])
            if isinstance(available_attrs, list):
                for attr in available_attrs:
                    if isinstance(attr, str) and "-" in attr:
                        prefix, val = attr.split("-", 1)
                        try:
                            with get_db_connection() as conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        """
                                        SELECT a.id FROM core_attribute a
                                        JOIN core_property p ON a.property_att_id = p.id
                                        WHERE LOWER(p.prefix) = LOWER(%s) AND LOWER(a.value) = LOWER(%s)
                                    """,
                                        (prefix.strip(), val.strip()),
                                    )
                                    row = cur.fetchone()
                                    if row:
                                        attr_ids.append(row[0])
                        except Exception as e:
                            logger.error(
                                f"Error resolving attribute {attr} for application: {e}"
                            )

            # C. Create or Update Application
            description = app.get("description", "")
            score = app.get("score", 3)
            icon = app.get("icon", None)
            level = app.get("level", "U")

            app_id = None
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM app_catalog_application WHERE LOWER(name) = LOWER(%s)",
                        (name,),
                    )
                    row = cur.fetchone()
                    if row:
                        app_id = row[0]
                        logger.info(f"Updating application '{name}' (ID: {app_id})")
                        cur.execute(
                            """
                            UPDATE app_catalog_application
                            SET description = %s, score = %s, icon = %s, level = %s, category_id = %s
                            WHERE id = %s
                        """,
                            (description, score, icon, level, category_id, app_id),
                        )
                        app_updated_count += 1
                    else:
                        logger.info(f"Creating application '{name}'")
                        cur.execute(
                            """
                            INSERT INTO app_catalog_application (name, description, score, icon, level, category_id, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW())
                            RETURNING id
                        """,
                            (name, description, score, icon, level, category_id),
                        )
                        app_id = cur.fetchone()[0]
                        app_created_count += 1
                    conn.commit()

            # C2. Restore icon file from template and update DB
            original_icon = app.get("icon")
            if original_icon and app_id:
                try:
                    import os as _os
                    from core.config import local_templates_dir, PATH_DATASHARES, STACK

                    # Look for the icon in the template's icons/ directory
                    icon_filename = _os.path.basename(original_icon)
                    icon_src = None
                    if template_path:
                        icon_src = (
                            local_templates_dir
                            / template_path
                            / "icons"
                            / icon_filename
                        )
                    if not icon_src or not icon_src.exists():
                        # Try project slug fallback
                        try:
                            proj = await get_project_by_id(project_id)
                            icon_src = (
                                local_templates_dir
                                / proj.get("slug", "")
                                / "icons"
                                / icon_filename
                            )
                        except Exception:
                            pass

                    if icon_src and icon_src.exists():
                        # Determine new icon path: catalog_icons/app_{app_id}{ext}
                        _, ext = _os.path.splitext(icon_filename)
                        new_icon_relpath = f"catalog_icons/app_{app_id}{ext}"

                        # Copy to public directory
                        icon_dest_dir = (
                            PATH_DATASHARES / STACK / "public" / "catalog_icons"
                        )
                        icon_dest_dir.mkdir(parents=True, exist_ok=True)
                        icon_dest = icon_dest_dir / f"app_{app_id}{ext}"

                        import shutil as _shutil

                        _shutil.copy2(icon_src, icon_dest)
                        logger.info(
                            f"Restored icon for application '{name}' to {icon_dest}"
                        )

                        # Update icon field in DB
                        with get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute(
                                    "UPDATE app_catalog_application SET icon = %s WHERE id = %s",
                                    (new_icon_relpath, app_id),
                                )
                                conn.commit()
                    else:
                        logger.warning(
                            f"Icon file not found in template for application '{name}': {icon_src}"
                        )
                except Exception as icon_ex:
                    logger.error(
                        f"Error restoring icon for application '{name}': {icon_ex}"
                    )

            # D. Associate Application with Project (Packages by Project)
            packages_to_install = app.get("packages_to_install", "")
            if isinstance(packages_to_install, list):
                packages_to_install = "\n".join(packages_to_install)

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id FROM app_catalog_packagesbyproject
                        WHERE application_id = %s AND project_id = %s
                    """,
                        (app_id, project_id),
                    )
                    row = cur.fetchone()
                    if row:
                        pbp_id = row[0]
                        cur.execute(
                            """
                            UPDATE app_catalog_packagesbyproject
                            SET packages_to_install = %s
                            WHERE id = %s
                        """,
                            (packages_to_install, pbp_id),
                        )
                    else:
                        cur.execute(
                            """
                            INSERT INTO app_catalog_packagesbyproject (packages_to_install, application_id, project_id)
                            VALUES (%s, %s, %s)
                        """,
                            (packages_to_install, app_id, project_id),
                        )
                    conn.commit()

            # E. Save/Associate available attributes
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM app_catalog_application_available_for_attributes WHERE application_id = %s",
                        (app_id,),
                    )
                    for attr_id in attr_ids:
                        cur.execute(
                            """
                            INSERT INTO app_catalog_application_available_for_attributes (application_id, attribute_id)
                            VALUES (%s, %s)
                        """,
                            (app_id, attr_id),
                        )
                    conn.commit()

        except Exception as e:
            errors.append(f"Failed to import application '{name}': {str(e)}")

    # 5. Process Deployments Import
    async with httpx.AsyncClient(verify=False) as client:
        for idx, dep in enumerate(deployments):
            if not isinstance(dep, dict):
                errors.append(f"Deployment at index {idx} is not a valid dictionary.")
                continue

            name = dep.get("name")
            if not name:
                errors.append(
                    f"Deployment at index {idx} is missing the required 'name' field."
                )
                continue

            # Skip ignored example deployments
            if dep.get("ignored", False):
                logger.info(f"Skipping ignored deployment '{name}'")
                continue

            source = dep.get("source", "I")

            # A. Resolve prefix-value attributes (e.g. SET-All Systems)
            included_ids = []
            included_attrs = dep.get("included_attributes", [])
            if isinstance(included_attrs, list):
                for attr in included_attrs:
                    if isinstance(attr, str) and "-" in attr:
                        prefix, val = attr.split("-", 1)
                        try:
                            with get_db_connection() as conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        """
                                        SELECT a.id FROM core_attribute a
                                        JOIN core_property p ON a.property_att_id = p.id
                                        WHERE LOWER(p.prefix) = LOWER(%s) AND LOWER(a.value) = LOWER(%s)
                                    """,
                                        (prefix.strip(), val.strip()),
                                    )
                                    row = cur.fetchone()
                                    if row:
                                        included_ids.append(row[0])
                        except Exception as e:
                            logger.error(f"Error resolving attribute {attr}: {e}")

            excluded_ids = []

            # B. Resolve available packages & package sets (for internal deployments)
            available_packages_ids = []
            available_packagesets_ids = []

            if source == "I":
                av_pkgs = dep.get("available_packages")
                if isinstance(av_pkgs, str) and av_pkgs:
                    # Resolve packageset ID
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute(
                                    """
                                    SELECT id FROM core_packageset
                                    WHERE project_id = %s AND (LOWER(slug) = LOWER(%s) OR LOWER(name) = LOWER(%s))
                                    """,
                                    (project_id, av_pkgs, av_pkgs),
                                )
                                row = cur.fetchone()
                                if row:
                                    available_packagesets_ids.append(row[0])
                    except Exception as e:
                        logger.error(f"Error resolving packageset {av_pkgs}: {e}")
                elif isinstance(av_pkgs, list):
                    # Resolve package IDs
                    for pkg_name in av_pkgs:
                        try:
                            with get_db_connection() as conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        """
                                        SELECT id FROM core_package
                                        WHERE project_id = %s AND LOWER(name) = LOWER(%s)
                                        LIMIT 1
                                    """,
                                        (project_id, pkg_name),
                                    )
                                    row = cur.fetchone()
                                    if row:
                                        available_packages_ids.append(row[0])
                        except Exception as e:
                            logger.error(f"Error resolving package {pkg_name}: {e}")

            # D. Prepare the REST API body
            api_payload = {
                "name": name,
                "enabled": dep.get("enabled", True),
                "source": source,
                "project": project_id,
                "included_attributes": included_ids,
                "excluded_attributes": excluded_ids,
            }

            if source == "E":
                api_payload.update(
                    {
                        "base_url": dep.get("base_url"),
                        "options": dep.get("options"),
                        "suite": dep.get("suite"),
                        "components": dep.get("components"),
                        "frozen": dep.get("frozen", True),
                        "expire": dep.get("expire", 1440),
                        # Set empty lists for internal fields
                        "packages_to_install": [],
                        "packages_to_remove": [],
                        "default_preincluded_packages": [],
                        "default_included_packages": [],
                        "default_excluded_packages": [],
                    }
                )
            else:
                api_payload.update(
                    {
                        "comment": dep.get("comment", ""),
                        "packages_to_install": parse_packages_list(
                            dep.get("packages_to_install")
                        ),
                        "packages_to_remove": parse_packages_list(
                            dep.get("packages_to_remove")
                        ),
                        "available_packages": available_packages_ids,
                        "available_package_sets": available_packagesets_ids,
                        "default_preincluded_packages": [],
                        "default_included_packages": [],
                        "default_excluded_packages": [],
                    }
                )

            # Check if a deployment with the same name already exists in this project (case-insensitive)
            existing_id = None
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT id FROM core_deployment WHERE project_id = %s AND LOWER(name) = LOWER(%s)",
                            (project_id, name),
                        )
                        row = cur.fetchone()
                        if row:
                            existing_id = row[0]
            except Exception as e:
                logger.error(f"Error checking existing deployment '{name}': {e}")
                errors.append(f"Database error checking '{name}': {str(e)}")
                continue

            try:
                if existing_id:
                    # Update deployment (PATCH)
                    url = f"{CORE_TOKEN_URL}/deployments/{existing_id}/"
                    logger.info(
                        f"Updating existing deployment '{name}' (ID: {existing_id}) on project {project_id}"
                    )
                    response = await client.patch(
                        url, json=api_payload, headers=headers, timeout=15.0
                    )
                    if response.status_code not in (200, 201, 204):
                        logger.error(
                            f"Failed to patch deployment '{name}': {response.status_code} {response.text}"
                        )
                        errors.append(f"Failed to update '{name}': {response.text}")
                    else:
                        updated_count += 1
                else:
                    # Create deployment (POST)
                    url = f"{CORE_TOKEN_URL}/deployments/"
                    logger.info(
                        f"Creating new deployment '{name}' on project {project_id}"
                    )
                    response = await client.post(
                        url, json=api_payload, headers=headers, timeout=15.0
                    )
                    if response.status_code not in (200, 201, 204):
                        logger.error(
                            f"Failed to post deployment '{name}': {response.status_code} {response.text}"
                        )
                        errors.append(f"Failed to create '{name}': {response.text}")
                    else:
                        created_count += 1
            except Exception as e:
                logger.error(f"HTTP communication error for '{name}': {e}")
                errors.append(f"Communication error for '{name}': {str(e)}")

        # 6. Trigger rebuilding metadata for all internal-source deployments of the target project
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, name FROM core_deployment WHERE project_id = %s AND source = 'I'",
                        (project_id,),
                    )
                    internal_deps = cur.fetchall()

            for dep_id, dep_name in internal_deps:
                m_url = (
                    f"{CORE_TOKEN_URL}/deployments/internal-sources/{dep_id}/metadata/"
                )
                logger.info(
                    f"Triggering metadata rebuild for internal deployment '{dep_name}' (ID: {dep_id})"
                )
                try:
                    m_resp = await client.get(m_url, headers=headers, timeout=120.0)
                    if m_resp.status_code == 200:
                        logger.info(
                            f"Successfully rebuilt metadata for internal deployment '{dep_name}'"
                        )
                    else:
                        logger.error(
                            f"Failed to rebuild metadata for '{dep_name}': HTTP {m_resp.status_code}"
                        )
                except Exception as ex:
                    logger.error(
                        f"Error triggering metadata rebuild for '{dep_name}': {ex}"
                    )
        except Exception as ex:
            logger.error(
                f"Failed to trigger metadata regeneration for project deployments: {ex}"
            )

    import json

    response_data = {
        "status": "success" if not errors else "partial_success",
        "deployments_created": created_count,
        "deployments_updated": updated_count,
        "stores_created": stores_created,
        "packages_created": packages_created,
        "applications_created": app_created_count,
        "applications_updated": app_updated_count,
        "errors": errors,
    }
    http_status = status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS

    accept = request.headers.get("accept", "")
    if "text/yaml" in accept or "application/x-yaml" in accept:
        return Response(
            content=yaml.safe_dump(
                response_data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            ),
            status_code=http_status,
            media_type="text/yaml",
        )
    return Response(
        content=json.dumps(response_data, ensure_ascii=False),
        status_code=http_status,
        media_type="application/json",
    )
