import logging
import httpx
import yaml
from fastapi import APIRouter, HTTPException, status, Response, Request
from core.config import MCI_TEMPLATES_URL, API_VERSION, CORE_TOKEN_URL
from core.database import get_db_connection
from core.core_client import get_project_by_id, get_cached_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_VERSION}/internal/mci",
    tags=["mci"],
)

router_private = APIRouter(
    prefix=f"{API_VERSION}/private/mci",
    tags=["mci"],
)

async def _fetch_text(url: str) -> str:
    logger.debug(f"Fetching text from URL: {url}")
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.text

@router.get("/catalog")
async def get_mci_catalog():
    """Fetch the MCI templates catalog."""
    base_url = MCI_TEMPLATES_URL.rstrip("/")
    url = f"{base_url}/catalog.yml"
    try:
        content = await _fetch_text(url)
        return yaml.safe_load(content)
    except Exception as e:
        logger.error(f"Error fetching MCI catalog: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not fetch catalog: {str(e)}"
        )

@router.get("/templates/{template_id:path}")
async def get_mci_template(
    template_id: str,
):
    """Fetch the full content of a specific MCI template."""
    base_url = MCI_TEMPLATES_URL.rstrip("/")
    catalog_url = f"{base_url}/catalog.yml"
    try:
        catalog_content = await _fetch_text(catalog_url)
        logger.debug(f"Catalog content received: {catalog_content[:200]}...")
        catalog = yaml.safe_load(catalog_content)

        if not isinstance(catalog, dict):
            logger.error(f"Catalog is not a dictionary: {type(catalog)}")
            raise HTTPException(status_code=500, detail="Invalid catalog format")

        template_info = next((t for t in catalog.get("templates", []) if t.get("id") == template_id), None)
        if not template_info:
            raise HTTPException(status_code=404, detail="Template not found")
        
        base_path = f"{base_url}/{template_info['path']}"
        
        dockerfile = await _fetch_text(f"{base_path}/dockerfile.j2")
        partition = await _fetch_text(f"{base_path}/partition.yml")
        
        # deployments.yml is optional
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
            "deployments": deployments
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template {template_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not fetch template details: {str(e)}"
        )

@router_private.get("/projects/{project_id}/export")
async def export_deployments(
    project_id: int,
):
    """
    Export all internal and external deployments of a project in YAML format.
    - Uses distinct schemas for internal and external deployments.
    - Attributes are exported as prefix-value string lists, e.g. ["SET-All Systems"].
    - Resolves store and available packages for internal deployments.
    - Only exports relevant fields.
    """
    # 1. Verify project exists
    try:
        project = await get_project_by_id(project_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found: {str(e)}"
        )

    deployments = []
    
    # 2. Query all deployments of this project
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, enabled, comment, packages_to_install, packages_to_remove,
                           source, base_url, options, suite, components, frozen, expire,
                           default_preincluded_packages, default_included_packages, default_excluded_packages
                    FROM core_deployment
                    WHERE project_id = %s
                    ORDER BY id ASC
                """, (project_id,))
                
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                
                for row in rows:
                    dep = dict(zip(columns, row))
                    dep_id = dep["id"]
                    source = dep["source"]
                    
                    # A. Fetch prefix-value attributes linked to this deployment
                    cur.execute("""
                        SELECT p.prefix, a.value
                        FROM core_deployment_included_attributes dia
                        JOIN core_attribute a ON dia.attribute_id = a.id
                        JOIN core_property p ON a.property_att_id = p.id
                        WHERE dia.deployment_id = %s
                    """, (dep_id,))
                    attrs = cur.fetchall()
                    included_attrs = [f"{r[0]}-{r[1]}" for r in attrs]
                    
                    # B. Build deployment dict according to source type (Internal vs External)
                    d = {
                        "name": dep["name"],
                        "enabled": dep["enabled"]
                    }
                    
                    if source == "E":
                        # External Deployment Schema
                        d.update({
                            "base_url": dep["base_url"],
                            "suite": dep["suite"],
                            "components": dep["components"],
                            "options": dep["options"],
                            "frozen": dep["frozen"],
                            "included_attributes": included_attrs,
                            "source": "E"
                        })
                    else:
                        # Internal Deployment Schema
                        # Check comment and ignore placeholder or template prefix
                        comment = dep["comment"] or ""
                        
                        # Fetch available packagesets associated
                        cur.execute("""
                            SELECT pks.name FROM core_deployment_available_package_sets daps
                            JOIN core_packageset pks ON daps.packageset_id = pks.id
                            WHERE daps.deployment_id = %s
                        """, (dep_id,))
                        pk_sets = cur.fetchall()
                        
                        # Fetch available packages associated
                        cur.execute("""
                            SELECT pk.name FROM core_deployment_available_packages dap
                            JOIN core_package pk ON dap.package_id = pk.id
                            WHERE dap.deployment_id = %s
                        """, (dep_id,))
                        pks = cur.fetchall()
                        
                        if pk_sets:
                            available_packages = pk_sets[0][0]  # Use first packageset name as string
                        elif pks:
                            available_packages = [p[0] for p in pks]  # List of package names
                        else:
                            available_packages = []
                            
                        # Package fields as clean lists of strings
                        packages_to_install = [p.strip() for p in dep["packages_to_install"].split("\n") if p.strip()] if dep["packages_to_install"] else []
                        packages_to_remove = [p.strip() for p in dep["packages_to_remove"].split("\n") if p.strip()] if dep["packages_to_remove"] else []
                        
                        # Resolve store: check store of packageset / package first, fallback to first store in project
                        store_slug = "thirds"
                        cur.execute("""
                            SELECT s.slug FROM core_store s
                            WHERE s.project_id = %s
                            LIMIT 1
                        """, (project_id,))
                        store_row = cur.fetchone()
                        if store_row:
                            store_slug = store_row[0]
                            
                        if pk_sets:
                            cur.execute("""
                                SELECT s.slug FROM core_packageset pks
                                JOIN core_store s ON pks.store_id = s.id
                                WHERE pks.name = %s AND pks.project_id = %s
                            """, (pk_sets[0][0], project_id))
                            pks_store = cur.fetchone()
                            if pks_store:
                                store_slug = pks_store[0]
                        elif pks:
                            cur.execute("""
                                SELECT s.slug FROM core_package pk
                                JOIN core_store s ON pk.store_id = s.id
                                WHERE pk.name = %s AND pk.project_id = %s
                                LIMIT 1
                            """, (pks[0][0], project_id))
                            pk_store = cur.fetchone()
                            if pk_store:
                                store_slug = pk_store[0]
                                
                        d.update({
                            "comment": comment,
                            "available_packages": available_packages,
                            "packages_to_install": packages_to_install,
                            "packages_to_remove": packages_to_remove,
                            "included_attributes": included_attrs,
                            "store": store_slug,
                            "source": "I"
                        })
                        
                    deployments.append(d)
                    
    except Exception as e:
        logger.error(f"Error exporting deployments for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during export: {str(e)}"
        )

    # Wrap the deployments in a standard dict/YAML envelope
    export_data = {"deployments": deployments}
    yaml_content = yaml.safe_dump(export_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Save deployments.yml, stores.yml, and packages.yml to pool/mci-templates
    try:
        from core.config import local_templates_dir, MCI_TEMPLATES_URL
        
        # 1. Query template_id for project_id from mci_config
        template_id = None
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT template_id FROM mci_config WHERE project_id = %s", (project_id,))
                row = cur.fetchone()
                if row:
                    template_id = row[0]
                    
        template_path = None
        if template_id:
            # 2. Load catalog.yml
            catalog = None
            catalog_file = local_templates_dir / "catalog.yml"
            if catalog_file.exists() and catalog_file.is_file():
                catalog = yaml.safe_load(catalog_file.read_text(encoding="utf-8"))
            else:
                try:
                    base_url = MCI_TEMPLATES_URL.rstrip("/")
                    url = f"{base_url}/catalog.yml"
                    content = await _fetch_text(url)
                    catalog = yaml.safe_load(content)
                except Exception as e:
                    logger.error(f"Error fetching catalog from {url}: {e}")
            
            # 3. Locate template by template_id in catalog
            if catalog and isinstance(catalog, dict):
                template_info = next((t for t in catalog.get("templates", []) if t.get("id") == template_id), None)
                if template_info:
                    template_path = template_info.get("path")
                    
        # 4. Determine save directory (resolved template path or project slug as fallback)
        if not template_path:
            template_path = project.get("slug")
            
        if template_path:
            dest_dir = local_templates_dir / template_path
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # A. Save deployments.yml
            dest_file = dest_dir / "deployments.yml"
            dest_file.write_text(yaml_content, encoding="utf-8")
            logger.info(f"Exported deployments saved to {dest_file}")
            
            # B. Export Stores to stores.yml
            stores = []
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, slug FROM core_store WHERE project_id = %s", (project_id,))
                    for s_name, s_slug in cur.fetchall():
                        stores.append({"name": s_name, "slug": s_slug})
            stores_file = dest_dir / "stores.yml"
            stores_file.write_text(
                yaml.safe_dump({"stores": stores}, default_flow_style=False, sort_keys=False, allow_unicode=True),
                encoding="utf-8"
            )
            logger.info(f"Exported stores saved to {stores_file}")
            
            # C. Export Package Metadata to packages.yml
            packages = []
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT pk.fullname, pk.name, pk.version, pk.architecture, s.slug AS store_slug, pr.slug AS project_slug
                        FROM core_package pk
                        JOIN core_store s ON pk.store_id = s.id
                        JOIN core_project pr ON pk.project_id = pr.id
                        WHERE pk.project_id = %s AND pk.store_id IS NOT NULL
                    """, (project_id,))
                    for fullname, name, version, architecture, store_slug, project_slug in cur.fetchall():
                        packages.append({
                            "fullname": fullname,
                            "name": name,
                            "version": version,
                            "architecture": architecture,
                            "store": store_slug,
                            "project_slug": project_slug
                        })
            packages_file = dest_dir / "packages.yml"
            packages_file.write_text(
                yaml.safe_dump({"packages": packages}, default_flow_style=False, sort_keys=False, allow_unicode=True),
                encoding="utf-8"
            )
            logger.info(f"Exported packages metadata saved to {packages_file}")
            
            # D. Download and save physical package files via API
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
                            logger.info(f"Successfully downloaded package {pkg['fullname']}")
                        else:
                            logger.error(f"Failed to download package {pkg['fullname']}: HTTP {response.status_code}")
                except Exception as ex:
                    logger.error(f"Error downloading package {pkg['fullname']}: {ex}")
                    
    except Exception as e:
        logger.error(f"Failed to save deployments, stores, and packages to template directory: {e}")
        
    return Response(content=yaml_content, media_type="text/yaml")

@router_private.post("/projects/{project_id}/import")
async def import_deployments(
    project_id: int,
    request: Request,
):
    """
    Import deployments from a YAML request body into the specified project.
    - Idempotent: Updates existing deployments (by name matching) and creates new ones.
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
                detail=f"Invalid YAML format: {str(e)}"
            )

    # 2. If no payload was provided, try to load deployments.yml from the template directory
    if not payload:
        try:
            from core.config import local_templates_dir, MCI_TEMPLATES_URL
            
            # A. Query template_id for project_id from mci_config
            template_id = None
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT template_id FROM mci_config WHERE project_id = %s", (project_id,))
                    row = cur.fetchone()
                    if row:
                        template_id = row[0]
                        
            template_path = None
            if template_id:
                # B. Load catalog.yml
                catalog = None
                catalog_file = local_templates_dir / "catalog.yml"
                if catalog_file.exists() and catalog_file.is_file():
                    catalog = yaml.safe_load(catalog_file.read_text(encoding="utf-8"))
                else:
                    try:
                        base_url = MCI_TEMPLATES_URL.rstrip("/")
                        url = f"{base_url}/catalog.yml"
                        content = await _fetch_text(url)
                        catalog = yaml.safe_load(content)
                    except Exception as e:
                        logger.error(f"Error fetching catalog from {url}: {e}")
                
                # C. Locate template by template_id in catalog
                if catalog and isinstance(catalog, dict):
                    template_info = next((t for t in catalog.get("templates", []) if t.get("id") == template_id), None)
                    if template_info:
                        template_path = template_info.get("path")
            
            # D. If template path is found, try to read deployments.yml from it
            yaml_content = None
            if template_path:
                local_file = local_templates_dir / template_path / "deployments.yml"
                if local_file.exists() and local_file.is_file():
                    yaml_content = local_file.read_text(encoding="utf-8")
                else:
                    try:
                        base_url = MCI_TEMPLATES_URL.rstrip("/")
                        url = f"{base_url}/{template_path}/deployments.yml"
                        yaml_content = await _fetch_text(url)
                    except Exception as e:
                        logger.error(f"Error fetching deployments.yml from template registry: {e}")
            
            if yaml_content:
                payload = yaml.safe_load(yaml_content)
                logger.info(f"Successfully loaded deployments template for project {project_id} from {template_path or 'registry'}")
            else:
                # E. If no template resolved, check fallback using project's slug
                project = await get_project_by_id(project_id)
                project_slug = project.get("slug")
                local_file = local_templates_dir / project_slug / "deployments.yml"
                if local_file.exists() and local_file.is_file():
                    yaml_content = local_file.read_text(encoding="utf-8")
                    payload = yaml.safe_load(yaml_content)
                    logger.info(f"Successfully loaded deployments from project slug fallback for project {project_id}")
                    
        except Exception as e:
            logger.error(f"Error resolving template deployments for project {project_id}: {e}")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty payload and no template deployments found for this project."
        )

    # Support both wrapped dict and flat list formats
    if isinstance(payload, dict) and "deployments" in payload:
        deployments = payload["deployments"]
    elif isinstance(payload, list):
        deployments = payload
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid structure: expected a list of deployments or a dictionary with a 'deployments' key."
        )

    # 2. Verify project exists
    try:
        await get_project_by_id(project_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found: {str(e)}"
        )

    token = get_cached_token()
    headers = {
        "accept": "application/json",
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }

    created_count = 0
    updated_count = 0
    errors = []

    # 3. Resolve template directory and import Stores and Packages before importing deployments
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
        
        logger.info(f"Import: template_dir={template_dir}, exists={template_dir.exists() if template_dir else False}")
        if template_dir and template_dir.exists():
            # B. Import Stores from stores.yml
            stores_file = template_dir / "stores.yml"
            if stores_file.exists() and stores_file.is_file():
                try:
                    stores_data = yaml.safe_load(stores_file.read_text(encoding="utf-8"))
                    if isinstance(stores_data, dict) and "stores" in stores_data:
                        for store in stores_data["stores"]:
                            s_name = store.get("name")
                            s_slug = store.get("slug")
                            if s_name and s_slug:
                                with get_db_connection() as conn:
                                    with conn.cursor() as cur:
                                        cur.execute("SELECT id FROM core_store WHERE project_id = %s AND LOWER(slug) = LOWER(%s)", (project_id, s_slug))
                                        row = cur.fetchone()
                                        if not row:
                                            logger.info(f"Creating missing store '{s_name}' for project {project_id}")
                                            cur.execute("INSERT INTO core_store (name, slug, project_id) VALUES (%s, %s, %s)", (s_name, s_slug, project_id))
                                            conn.commit()
                except Exception as ex:
                    logger.error(f"Error importing stores from {stores_file}: {ex}")
                    
            # C. Import Packages from packages.yml and copy physical .deb files
            packages_file = template_dir / "packages.yml"
            if packages_file.exists() and packages_file.is_file():
                try:
                    packages_data = yaml.safe_load(packages_file.read_text(encoding="utf-8"))
                    if isinstance(packages_data, dict) and "packages" in packages_data:
                        target_project = await get_project_by_id(project_id)
                        target_slug = target_project.get("slug")
                        
                        for pkg in packages_data["packages"]:
                            fullname = pkg.get("fullname")
                            name = pkg.get("name")
                            version = pkg.get("version")
                            arch = pkg.get("architecture")
                            store_slug = pkg.get("store")
                            
                            if not (fullname and name and version and arch and store_slug):
                                continue
                                
                            # C1. Physical copy of .deb file to destination public store folder
                            src_pkg = template_dir / "stores" / store_slug / fullname
                            if src_pkg.exists() and src_pkg.is_file():
                                dest_pkg_dir = PATH_DATASHARES / STACK / "public" / target_slug / "stores" / store_slug
                                dest_pkg_dir.mkdir(parents=True, exist_ok=True)
                                dest_pkg = dest_pkg_dir / fullname
                                shutil.copy2(src_pkg, dest_pkg)
                                logger.info(f"Copied imported package {fullname} to {dest_pkg}")
                            else:
                                logger.warning(f"Import package file {src_pkg} not found in template")
                                
                            # C2. Register package in core_package database table
                            with get_db_connection() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("SELECT id FROM core_store WHERE project_id = %s AND LOWER(slug) = LOWER(%s)", (project_id, store_slug))
                                    store_row = cur.fetchone()
                                    if store_row:
                                        t_store_id = store_row[0]
                                        cur.execute("SELECT id FROM core_package WHERE project_id = %s AND store_id = %s AND fullname = %s", (project_id, t_store_id, fullname))
                                        pkg_row = cur.fetchone()
                                        if not pkg_row:
                                            logger.info(f"Registering package {fullname} in DB for project {project_id}")
                                            cur.execute(
                                                "INSERT INTO core_package (fullname, name, version, architecture, project_id, store_id) VALUES (%s, %s, %s, %s, %s, %s)",
                                                (fullname, name, version, arch, project_id, t_store_id)
                                            )
                                            conn.commit()
                except Exception as ex:
                    logger.error(f"Error importing packages from {packages_file}: {ex}")
    except Exception as ex:
        logger.error(f"Error during stores and packages resolution: {ex}")

    async with httpx.AsyncClient(verify=False) as client:
        for idx, dep in enumerate(deployments):
            if not isinstance(dep, dict):
                errors.append(f"Deployment at index {idx} is not a valid dictionary.")
                continue

            name = dep.get("name")
            if not name:
                errors.append(f"Deployment at index {idx} is missing the required 'name' field.")
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
                                    cur.execute("""
                                        SELECT a.id FROM core_attribute a
                                        JOIN core_property p ON a.property_att_id = p.id
                                        WHERE LOWER(p.prefix) = LOWER(%s) AND LOWER(a.value) = LOWER(%s)
                                    """, (prefix.strip(), val.strip()))
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
                                cur.execute("""
                                    SELECT id FROM core_packageset
                                    WHERE project_id = %s AND (LOWER(slug) = LOWER(%s) OR LOWER(name) = LOWER(%s))
                                """, (project_id, av_pkgs, av_pkgs))
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
                                    cur.execute("""
                                        SELECT id FROM core_package
                                        WHERE project_id = %s AND LOWER(name) = LOWER(%s)
                                        LIMIT 1
                                    """, (project_id, pkg_name))
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
                "excluded_attributes": excluded_ids
            }

            if source == "E":
                api_payload.update({
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
                    "default_excluded_packages": []
                })
            else:
                api_payload.update({
                    "comment": dep.get("comment", ""),
                    "packages_to_install": parse_packages_list(dep.get("packages_to_install")),
                    "packages_to_remove": parse_packages_list(dep.get("packages_to_remove")),
                    "available_packages": available_packages_ids,
                    "available_package_sets": available_packagesets_ids,
                    "default_preincluded_packages": [],
                    "default_included_packages": [],
                    "default_excluded_packages": []
                })

            # Check if a deployment with the same name already exists in this project (case-insensitive)
            existing_id = None
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT id FROM core_deployment WHERE project_id = %s AND LOWER(name) = LOWER(%s)",
                            (project_id, name)
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
                    logger.info(f"Updating existing deployment '{name}' (ID: {existing_id}) on project {project_id}")
                    response = await client.patch(url, json=api_payload, headers=headers, timeout=15.0)
                    if response.status_code not in (200, 201, 204):
                        logger.error(f"Failed to patch deployment '{name}': {response.status_code} {response.text}")
                        errors.append(f"Failed to update '{name}': {response.text}")
                    else:
                        updated_count += 1
                else:
                    # Create deployment (POST)
                    url = f"{CORE_TOKEN_URL}/deployments/"
                    logger.info(f"Creating new deployment '{name}' on project {project_id}")
                    response = await client.post(url, json=api_payload, headers=headers, timeout=15.0)
                    if response.status_code not in (200, 201, 204):
                        logger.error(f"Failed to post deployment '{name}': {response.status_code} {response.text}")
                        errors.append(f"Failed to create '{name}': {response.text}")
                    else:
                        created_count += 1
            except Exception as e:
                logger.error(f"HTTP communication error for '{name}': {e}")
                errors.append(f"Communication error for '{name}': {str(e)}")

        # 4. Trigger rebuilding metadata for all internal-source deployments of the target project
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, name FROM core_deployment WHERE project_id = %s AND source = 'I'", (project_id,))
                    internal_deps = cur.fetchall()
                    
            for dep_id, dep_name in internal_deps:
                m_url = f"{CORE_TOKEN_URL}/deployments/internal-sources/{dep_id}/metadata/"
                logger.info(f"Triggering metadata rebuild for internal deployment '{dep_name}' (ID: {dep_id})")
                try:
                    m_resp = await client.get(m_url, headers=headers, timeout=120.0)
                    if m_resp.status_code == 200:
                        logger.info(f"Successfully rebuilt metadata for internal deployment '{dep_name}'")
                    else:
                        logger.error(f"Failed to rebuild metadata for '{dep_name}': HTTP {m_resp.status_code}")
                except Exception as ex:
                    logger.error(f"Error triggering metadata rebuild for '{dep_name}': {ex}")
        except Exception as ex:
            logger.error(f"Failed to trigger metadata regeneration for project deployments: {ex}")

    status_code = status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS
    return Response(
        content=yaml.safe_dump({
            "status": "success" if not errors else "partial_success",
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        }, default_flow_style=False, sort_keys=False, allow_unicode=True),
        status_code=status_code,
        media_type="text/yaml"
    )
