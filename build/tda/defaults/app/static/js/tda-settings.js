        "use strict";

        const ROOT_PATH = "/tda";

        // State: user-defined lenses
        let lensSpecs = [];               // lens descriptors from /api/v1/lenses/details
        let availableMetrics = [];        // { name:"...", label:"..." }
        let availableDatasetMetrics = []; // { name:"...", label:"..." } (DATASET metric picker)
        let availableColors = [];         // { columns:[...], label:"...", kind:"..." }
        let editingLensName = null;       // lens being edited (null = creating)
        let recalcState = {};             // lens name -> "running" | "done" (per-lens recalculation)

        // State: per-lens form chips
        let formPrefixItems = [];         // { id, prefix, name, selected }
        let formScopeItems = [];          // { id, name, count, selected }
        let formMetricItems = [];         // { id, name, selected }

        const LENS_TYPE_LABELS = {
            identity: "Identity",
            pca: "PCA",
            mds_jaccard: "Jaccard + MDS",
            multi_lens: "Multi-Lens (PCA + Jaccard)",
        };

        /* ── Auth helpers ─────────────────────────────────── */
        async function fetchWithAuth(url, opts = {}) {
            const res = await fetch(url, { credentials: "include", ...opts });
            if (res.status === 401 || res.status === 403) {
                showLoginModal();
                throw new Error("Unauthenticated");
            }
            return res;
        }

        function showLoginModal() {
            const m = document.getElementById("login-modal");
            if (m) {
                m.classList.add("visible");
                m.style.setProperty("display", "flex", "important");
            }
        }
        function hideLoginModal() {
            const m = document.getElementById("login-modal");
            if (m) {
                m.classList.remove("visible");
                m.style.setProperty("display", "none", "important");
            }
        }

        async function submitLogin(e) {
            e.preventDefault();
            const errEl = document.getElementById("loginError");
            const btn = document.getElementById("loginSubmitBtn");
            errEl.style.display = "none";
            btn.disabled = true;
            btn.innerHTML = "<span>Signing in\u2026</span>";
            try {
                const res = await fetch(`${ROOT_PATH}/api/v1/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                    body: JSON.stringify({
                        username: document.getElementById("loginUsername").value,
                        password: document.getElementById("loginPassword").value,
                    }),
                });
                const data = await res.json();
                if (!res.ok) {
                    errEl.textContent = data.detail || "Invalid credentials";
                    errEl.style.display = "block";
                } else {
                    hideLoginModal();
                    await init();
                }
            } catch (err) {
                errEl.textContent = "Network error. Try again.";
                errEl.style.display = "block";
            } finally {
                btn.disabled = false;
                btn.innerHTML = "<span>Sign in</span>";
            }
        }

        async function logout() {
            await fetch(`${ROOT_PATH}/api/v1/auth/logout`, { method: "POST", credentials: "include" });
            showLoginModal();
            document.getElementById("userProfileSection").style.display = "none";
        }

        /* ── User info ────────────────────────────────────── */
        async function loadUserInfo() {
            try {
                const res = await fetchWithAuth(`${ROOT_PATH}/api/v1/auth/me`);
                if (!res.ok) return;
                const user = await res.json();
                const name = user.first_name
                    ? `${user.first_name} ${user.last_name || ""}`.trim()
                    : (user.username || "User");
                document.getElementById("userAvatar").textContent = name.charAt(0).toUpperCase();
                document.getElementById("userName").textContent = name;
                document.getElementById("userRole").textContent = user.is_superuser ? "Superuser" : "Staff";
                document.getElementById("userProfileSection").style.display = "flex";
            } catch (_) { }
        }

        /* ── Map selection and UI synchronization ─────────── */
        function lensTypeLabel(t) {
            return LENS_TYPE_LABELS[t] || t;
        }

        function updateToolbarActions(spec) {
            const btnView = document.getElementById("btnViewDashboard");
            const btnRecalc = document.getElementById("btnRecalcMap");
            const btnDelete = document.getElementById("btnDeleteMap");
            const sideDash = document.getElementById("sidebarDashboardLink");

            if (spec) {
                if (btnView) btnView.style.display = "inline-flex";
                if (btnRecalc) {
                    btnRecalc.style.display = "inline-flex";
                    const state = recalcState[spec.name] || "";
                    if (state === "running") {
                        btnRecalc.disabled = true;
                        btnRecalc.innerHTML = '<span class="spinner-sm"></span>';
                        btnRecalc.title = "Recalculating…";
                    } else if (state === "done") {
                        btnRecalc.disabled = false;
                        btnRecalc.style.color = "#16a34a";
                        btnRecalc.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
                        btnRecalc.title = "Recalculation complete";
                    } else {
                        btnRecalc.disabled = false;
                        btnRecalc.style.color = "";
                        btnRecalc.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>';
                        btnRecalc.title = "Recalculate this map";
                    }
                }
                if (btnDelete) {
                    btnDelete.style.display = "inline-flex";
                }
                if (sideDash) {
                    sideDash.href = `${ROOT_PATH}/#${encodeURIComponent(spec.name)}`;
                }
            } else {
                // Creating a new map
                if (btnView) btnView.style.display = "none";
                if (btnRecalc) btnRecalc.style.display = "none";
                if (btnDelete) btnDelete.style.display = "none";
                if (sideDash) sideDash.href = `${ROOT_PATH}/`;
            }
        }

        function renderMapSelector(selectedName) {
            const sel = document.getElementById("currentMapSelect");
            if (!sel) return;
            sel.innerHTML = "";

            if (!lensSpecs.length) {
                const opt = document.createElement("option");
                opt.value = "";
                opt.textContent = "No maps defined";
                sel.appendChild(opt);
                return;
            }

            lensSpecs.forEach(spec => {
                const opt = document.createElement("option");
                opt.value = spec.name;
                opt.textContent = spec.label || spec.name;
                if (spec.name === selectedName) opt.selected = true;
                sel.appendChild(opt);
            });

            if (editingLensName === null && !lensSpecs.some(s => s.name === selectedName)) {
                const optNew = document.createElement("option");
                optNew.value = "__new__";
                optNew.textContent = "➕ Create New Map";
                optNew.selected = true;
                sel.appendChild(optNew);
            }
        }

        function onMapSelectChange(val) {
            if (val === "__new__") {
                newLens();
            } else if (val) {
                window.location.hash = `#${val}`;
                editLens(val);
            }
        }

        function viewCurrentMapInDashboard() {
            if (editingLensName) {
                window.open(`${ROOT_PATH}/dashboard#${encodeURIComponent(editingLensName)}`, "_blank", "noopener");
            } else {
                window.open(`${ROOT_PATH}/dashboard`, "_blank", "noopener");
            }
        }

        async function recalcCurrentMap() {
            if (!editingLensName) return;
            await recalcLens(editingLensName);
        }

        async function deleteCurrentMap() {
            if (!editingLensName) return;
            await deleteLens(editingLensName);
        }

        /* ── Form chip grids (attribute types, scopes & metrics) ──── */
        function renderChips(gridId, items, hasPrefix) {
            const grid = document.getElementById(gridId);
            if (!grid) return;
            grid.innerHTML = "";
            if (!items.length) {
                grid.innerHTML = '<span class="chip-empty">No data found in database</span>';
                return;
            }
            items.forEach(item => {
                const chip = document.createElement("span");
                chip.className = "chip" + (item.selected ? " selected" : "");
                chip.dataset.id = item.id;
                if (item.title) chip.title = item.title;
                if (hasPrefix) {
                    chip.innerHTML = `<span class="chip-prefix">${escHtml(item.prefix)}</span>${escHtml(item.name)}`;
                } else {
                    chip.textContent = item.name;
                }
                chip.addEventListener("click", () => {
                    item.selected = !item.selected;
                    chip.classList.toggle("selected", item.selected);
                    scheduleMatrixEstimate();
                    if (gridId === "formMetricGrid" || gridId === "formPrefixGrid") {
                        populateColorSelect();
                        autoSelectProjectionBasedOnData();
                    }
                });
                grid.appendChild(chip);
            });
        }

        function autoSelectProjectionBasedOnData() {
            const hasPrefixes = formPrefixItems.some(i => i.selected);
            const hasMetrics = formMetricItems.some(i => i.selected);
            const lensTypeSel = document.getElementById("lensType");
            if (!lensTypeSel) return;

            if (hasPrefixes && hasMetrics) {
                // Mixed continuous and binary dimensions -> recommend/select multi_lens
                lensTypeSel.value = "multi_lens";
            } else if (hasPrefixes && !hasMetrics) {
                // Only binary dimensions -> mds_jaccard
                if (lensTypeSel.value === "multi_lens" || lensTypeSel.value === "identity") {
                    lensTypeSel.value = "mds_jaccard";
                }
            } else if (!hasPrefixes && hasMetrics) {
                // Only continuous metrics -> pca
                if (lensTypeSel.value === "multi_lens" || lensTypeSel.value === "mds_jaccard") {
                    lensTypeSel.value = "pca";
                }
            }
            updateLensFormVisibility();
        }

        const CHIP_GRIDS = {
            prefix: { items: () => formPrefixItems, grid: "formPrefixGrid", hasPrefix: true },
            scope: { items: () => formScopeItems, grid: "formScopeGrid", hasPrefix: false },
            metric: { items: () => formMetricItems, grid: "formMetricGrid", hasPrefix: false },
        };

        function setChipSelection(type, selected) {
            const cfg = CHIP_GRIDS[type];
            if (!cfg) return;
            cfg.items().forEach(i => i.selected = selected);
            renderChips(cfg.grid, cfg.items(), cfg.hasPrefix);
            scheduleMatrixEstimate();
            if (type === "metric" || type === "prefix") {
                populateColorSelect();
                autoSelectProjectionBasedOnData();
            }
        }

        function selectAllChips(type) { setChipSelection(type, true); }
        function selectNoneChips(type) { setChipSelection(type, false); }

        /* ── Tab Switching in Form ────────────────────────── */
        function switchFormTab(tabId, btn) {
            document.querySelectorAll(".form-tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".form-tab-panel").forEach(p => p.classList.remove("active"));
            if (btn) btn.classList.add("active");
            const target = document.getElementById(tabId);
            if (target) target.classList.add("active");
        }

        /* ── Live Chip Filtering ──────────────────────────── */
        function filterChips(gridId, query) {
            const grid = document.getElementById(gridId);
            if (!grid) return;
            const q = (query || "").trim().toLowerCase();
            const chips = grid.querySelectorAll(".chip");
            chips.forEach(c => {
                const text = c.textContent.toLowerCase();
                if (!q || text.includes(q)) {
                    c.classList.remove("hidden");
                } else {
                    c.classList.add("hidden");
                }
            });
        }

        /* ── Lens form ────────────────────────────────────── */
        function updateLensFormVisibility() {
            const type = document.getElementById("lensType").value;
            document.getElementById("lensComponentsField").style.display = type === "pca" ? "flex" : "none";
            document.getElementById("lensMatrixField").style.display = (type === "mds_jaccard" || type === "multi_lens") ? "flex" : "none";
            document.getElementById("lensMetric1Field").style.display = type === "identity" ? "flex" : "none";
            document.getElementById("lensMetric2Field").style.display = type === "identity" ? "flex" : "none";
        }

        function updateClusteringVisibility() {
            const type = document.getElementById("clusteringType").value;
            document.getElementById("clusteringNClustersField").style.display =
                (type === "kmeans" || type === "agglomerative") ? "flex" : "none";
            document.getElementById("clusteringEpsField").style.display = type === "dbscan" ? "flex" : "none";
            document.getElementById("clusteringMinSamplesField").style.display = type === "dbscan" ? "flex" : "none";
        }

        function populateMetricSelects() {
            const sel1 = document.getElementById("lensMetric1");
            const sel2 = document.getElementById("lensMetric2");
            const build = () => {
                const opt = document.createElement("option");
                opt.value = "";
                opt.textContent = "— select metric —";
                return opt;
            };
            sel1.innerHTML = "";
            sel2.innerHTML = "";
            sel1.appendChild(build());
            sel2.appendChild(build());
            availableMetrics.forEach(m => {
                const o1 = document.createElement("option");
                o1.value = m.name;
                o1.textContent = m.label;
                sel1.appendChild(o1);
                const o2 = document.createElement("option");
                o2.value = m.name;
                o2.textContent = m.label;
                sel2.appendChild(o2);
            });
        }

        function defaultColorOption() {
            return availableColors.find(o => o.group === "metric") || availableColors[0] || null;
        }

        function populateColorSelect() {
            const sel = document.getElementById("lensColorSelect");
            const current = sel.value;
            sel.innerHTML = "";
            const groups = {};
            // Metric colors are only offered among the metrics selected in DATASET
            const metricIds = formMetricItems.filter(i => i.selected).map(i => i.id);
            // Prefix colors are only offered among the Attribute types selected in DATASET
            const prefixIds = formPrefixItems.filter(i => i.selected).map(i => i.id);
            availableColors.forEach(opt => {
                const group = opt.group || "metric";
                if (group === "attribute") {
                    const m = /^prefix_(\d+)$/.exec((opt.columns || [])[0] || "");
                    if (!m || !prefixIds.includes(parseInt(m[1], 10))) return;
                } else if (group === "metric") {
                    const cols = opt.columns || [];
                    if (!cols.length || !cols.every(c => metricIds.includes(c))) return;
                }
                if (!groups[group]) {
                    groups[group] = document.createElement("optgroup");
                    groups[group].label = group === "attribute" ? "Attributes" : "Metrics";
                    sel.appendChild(groups[group]);
                }
                const el = document.createElement("option");
                el.value = opt.columns.join("+");
                el.textContent = opt.label;
                groups[group].appendChild(el);
            });
            if (current) sel.value = current;
        }

        function colorKeyFor(columns) { return (columns || []).join("+"); }

        function setColorSelect(columns, label) {
            const sel = document.getElementById("lensColorSelect");
            const key = colorKeyFor(columns);
            if (key === "project_encoded") {
                // Legacy default; pick the first available metric option instead
                const def = defaultColorOption();
                if (def) sel.value = colorKeyFor(def.columns);
                return;
            }
            const exists = Array.from(sel.options).some(o => o.value === key);
            if (!exists && columns && columns.length) {
                const el = document.createElement("option");
                el.value = key;
                el.textContent = label || key;
                sel.appendChild(el);
            }
            sel.value = key;
        }

        function resetFormChips(selectedPrefixIds, selectedScopeIds, selectedMetricNames) {
            formPrefixItems.forEach(i => i.selected = (selectedPrefixIds || []).includes(i.id));
            formScopeItems.forEach(i => i.selected = (selectedScopeIds || []).includes(i.id));
            // null/undefined = all metrics selected (new lens default)
            formMetricItems.forEach(i => i.selected = selectedMetricNames == null ? true : (selectedMetricNames || []).includes(i.id));
            renderChips("formPrefixGrid", formPrefixItems, true);
            renderChips("formScopeGrid", formScopeItems, false);
            renderChips("formMetricGrid", formMetricItems, false);
            populateColorSelect();
            scheduleMatrixEstimate();
        }

        /* ── Matrix size estimate (DATASET section) ──────────── */
        let _estimateTimer = null;
        function scheduleMatrixEstimate() {
            clearTimeout(_estimateTimer);
            _estimateTimer = setTimeout(estimateMatrix, 250);
        }

        async function estimateMatrix() {
            const box = document.getElementById("matrixEstimate");
            if (!box) return;
            const params = new URLSearchParams();
            formPrefixItems.filter(i => i.selected).forEach(i => params.append("formula_prefix_ids", i.id));
            formScopeItems.filter(i => i.selected).forEach(i => params.append("scope_ids", i.id));
            formMetricItems.filter(i => i.selected).forEach(i => params.append("metric_columns", i.id));

            box.innerHTML = '<span class="chip-loading">Estimating matrix size…</span>';
            try {
                const res = await fetchWithAuth(`${ROOT_PATH}/api/v1/config/estimate-matrix?${params.toString()}`);
                if (!res.ok) throw new Error("unavailable");
                const e = await res.json();
                box.innerHTML = `<b>${e.n.toLocaleString()}</b> Computers * <b>${e.d_max.toLocaleString()}</b> dimensions`;
            } catch (_) {
                box.innerHTML = '<span class="chip-empty">Matrix size unavailable (DB not reachable)</span>';
            }
        }

        function newLens() {
            editingLensName = null;
            window.location.hash = "#new";
            renderMapSelector("__new__");
            updateToolbarActions(null);

            const titleEl = document.getElementById("lensFormTitle");
            if (titleEl) titleEl.textContent = "New Map";
            document.getElementById("lensName").value = "";
            document.getElementById("lensName").disabled = false;
            document.getElementById("lensLabel").value = "";
            document.getElementById("lensDesc").value = "";
            document.getElementById("lensScheduled").checked = true;
            document.getElementById("lensType").value = "pca";
            document.getElementById("lensComponents").value = "2";
            document.getElementById("lensMatrixSource").value = "attributes";
            document.getElementById("lensMetric1").value = "";
            document.getElementById("lensMetric2").value = "";
            document.getElementById("coverType").value = "cubical";
            document.getElementById("coverNCubes").value = "";
            document.getElementById("coverOverlap").value = "";
            document.getElementById("clusteringScaling").checked = true;
            document.getElementById("clusteringType").value = "dbscan";
            document.getElementById("clusteringNClusters").value = "";
            document.getElementById("clusteringEps").value = "";
            document.getElementById("clusteringMinSamples").value = "";
            document.getElementById("drawDimensions").value = "3";
            document.getElementById("drawIterations").value = "";
            document.getElementById("drawSeed").value = "";
            document.getElementById("lensMetricsIntervalDays").value = "365";
            resetFormChips([], [], null);
            const def = defaultColorOption();
            if (def) setColorSelect(def.columns, def.label);
            updateLensFormVisibility();
            updateClusteringVisibility();
            const firstTabBtn = document.querySelector(".form-tab-btn");
            if (firstTabBtn) switchFormTab("tab-general", firstTabBtn);
        }

        function editLens(name) {
            const spec = lensSpecs.find(s => s.name === name);
            if (!spec) {
                if (lensSpecs.length > 0) editLens(lensSpecs[0].name);
                return;
            }
            editingLensName = name;
            renderMapSelector(name);
            updateToolbarActions(spec);

            const titleEl = document.getElementById("lensFormTitle");
            if (titleEl) titleEl.textContent = `Configure Map: ${spec.label || spec.name}`;
            document.getElementById("lensName").value = spec.name;
            document.getElementById("lensName").disabled = true; // name is immutable
            document.getElementById("lensLabel").value = spec.label || "";
            document.getElementById("lensDesc").value = spec.description || "";
            document.getElementById("lensScheduled").checked = spec.scheduled !== false;

            const coverCfg = spec.cover || {};
            document.getElementById("coverType").value = coverCfg.type || "cubical";
            document.getElementById("coverNCubes").value = coverCfg.n_cubes == null ? "" : coverCfg.n_cubes;
            document.getElementById("coverOverlap").value = coverCfg.overlap == null ? "" : coverCfg.overlap;

            const clCfg = spec.clustering || {};
            document.getElementById("clusteringScaling").checked = clCfg.scaling !== false;
            document.getElementById("clusteringType").value = clCfg.type || "dbscan";
            document.getElementById("clusteringNClusters").value = clCfg.n_clusters == null ? "" : clCfg.n_clusters;
            document.getElementById("clusteringEps").value = clCfg.eps == null ? "" : clCfg.eps;
            document.getElementById("clusteringMinSamples").value = clCfg.min_samples == null ? "" : clCfg.min_samples;

            const drawCfg = spec.draw || {};
            document.getElementById("drawIterations").value = drawCfg.iterations == null ? "" : drawCfg.iterations;
            document.getElementById("drawSeed").value = drawCfg.seed == null ? "" : drawCfg.seed;
            const ds = spec.dataset || {};
            document.getElementById("lensMetricsIntervalDays").value = ds.metrics_interval_days == null ? "365" : ds.metrics_interval_days;
            resetFormChips(ds.formula_prefix_ids || [], ds.scope_ids || [], ds.metric_columns || []);

            // Set the persisted lens projection after chip reset
            const lensCfg = spec.lens || {};
            document.getElementById("lensType").value = lensCfg.type || "pca";
            document.getElementById("lensComponents").value = String(lensCfg.components == null ? 2 : lensCfg.components);
            document.getElementById("lensMatrixSource").value = lensCfg.matrix_source || "attributes";
            document.getElementById("lensMetric1").value = (lensCfg.metric_columns || [])[0] || "";
            document.getElementById("lensMetric2").value = (lensCfg.metric_columns || [])[1] || "";

            const color = drawCfg.color || null;
            if (color) setColorSelect(color.columns, color.label);
            updateLensFormVisibility();
            updateClusteringVisibility();
        }

        function cancelLensEdit() {
            if (editingLensName) {
                editLens(editingLensName);
            } else if (lensSpecs.length > 0) {
                editLens(lensSpecs[0].name);
            }
        }

        async function saveLens() {
            const name = document.getElementById("lensName").value.trim().toLowerCase();
            const label = document.getElementById("lensLabel").value.trim();
            if (!name || !label) {
                showBanner("error", "Name and Label are required.");
                return;
            }
            const description = document.getElementById("lensDesc").value.trim();
            const lensType = document.getElementById("lensType").value;
            const components = parseInt(document.getElementById("lensComponents").value, 10) || 2;
            const matrix_source = (lensType === "mds_jaccard" || lensType === "multi_lens")
                ? document.getElementById("lensMatrixSource").value
                : null;
            const m1 = document.getElementById("lensMetric1").value;
            const m2 = document.getElementById("lensMetric2").value;
            let metric_columns = [];
            if (lensType === "identity") metric_columns = [m1, m2].filter(Boolean);
            const lens = { type: lensType, components, metric_columns, matrix_source };

            const nCubesRaw = document.getElementById("coverNCubes").value;
            const overlapRaw = document.getElementById("coverOverlap").value;
            const cover = {
                type: document.getElementById("coverType").value,
                n_cubes: nCubesRaw === "" ? null : parseInt(nCubesRaw, 10),
                overlap: overlapRaw === "" ? null : parseFloat(overlapRaw),
                radius: null,
                n_neighbors: null,
            };

            const nClustersRaw = document.getElementById("clusteringNClusters").value;
            const epsRaw = document.getElementById("clusteringEps").value;
            const minSamplesRaw = document.getElementById("clusteringMinSamples").value;
            const clustering = {
                scaling: document.getElementById("clusteringScaling").checked,
                type: document.getElementById("clusteringType").value,
                n_clusters: nClustersRaw === "" ? null : parseInt(nClustersRaw, 10),
                eps: epsRaw === "" ? null : parseFloat(epsRaw),
                min_samples: minSamplesRaw === "" ? null : parseInt(minSamplesRaw, 10),
            };

            const colorOpt = availableColors.find(o => colorKeyFor(o.columns) === document.getElementById("lensColorSelect").value);
            const color = colorOpt
                ? { columns: colorOpt.columns, label: colorOpt.label, kind: colorOpt.kind || "continuous" }
                : null;

            const node_label = "attribute";

            const drawIterationsRaw = document.getElementById("drawIterations").value;
            const drawSeedRaw = document.getElementById("drawSeed").value;
            const draw = {
                dimensions: 3,
                iterations: drawIterationsRaw === "" ? null : parseInt(drawIterationsRaw, 10),
                seed: drawSeedRaw === "" ? null : parseInt(drawSeedRaw, 10),
                color,
                node_label,
            };

            const intervalDaysRaw = document.getElementById("lensMetricsIntervalDays").value;
            const metrics_interval_days = intervalDaysRaw === "" ? 365 : (parseInt(intervalDaysRaw, 10) || 365);
            const dataset = {
                formula_prefix_ids: formPrefixItems.filter(i => i.selected).map(i => i.id),
                scope_ids: formScopeItems.filter(i => i.selected).map(i => i.id),
                metric_columns: formMetricItems.filter(i => i.selected).map(i => i.id),
                metrics_interval_days: metrics_interval_days,
            };

            const scheduled = document.getElementById("lensScheduled").checked;

            const payload = {
                name, label, description, scheduled, lens, cover, clustering,
                draw, dataset,
            };

            const url = editingLensName
                ? `${ROOT_PATH}/api/v1/lenses/${encodeURIComponent(editingLensName)}`
                : `${ROOT_PATH}/api/v1/lenses`;
            const method = editingLensName ? "PUT" : "POST";

            try {
                const res = await fetchWithAuth(url, {
                    method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                const data = await res.json();
                if (!res.ok) {
                    showBanner("error", data.detail || "Failed to save map.");
                    return;
                }
                await loadLensesData();
                window.location.hash = `#${name}`;
                editLens(name);
                showBanner("success", `Map \u201c${data.label || data.name}\u201d saved.`);
            } catch (err) {
                if (err.message !== "Unauthenticated") {
                    showBanner("error", `Network error: ${err.message}`);
                }
            }
        }

        async function deleteLens(name) {
            if (!confirm(`Delete map \u201c${name}\u201d and its generated graphs?`)) return;
            try {
                const res = await fetchWithAuth(`${ROOT_PATH}/api/v1/lenses/${encodeURIComponent(name)}`, {
                    method: "DELETE",
                });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    showBanner("error", data.detail || "Failed to delete map.");
                    return;
                }
                await loadLensesData();
                const nextMap = lensSpecs[0] ? lensSpecs[0].name : null;
                if (nextMap) {
                    window.location.hash = `#${nextMap}`;
                    editLens(nextMap);
                } else {
                    newLens();
                }
                showBanner("success", `Map \u201c${name}\u201d deleted.`);
            } catch (err) {
                if (err.message !== "Unauthenticated") {
                    showBanner("error", `Network error: ${err.message}`);
                }
            }
        }

        async function recalcLens(name) {
            if (recalcState[name] === "running") return;
            recalcState[name] = "running";
            const currentSpec = lensSpecs.find(s => s.name === editingLensName);
            updateToolbarActions(currentSpec);
            try {
                const res = await fetchWithAuth(`${ROOT_PATH}/api/v1/lenses/${encodeURIComponent(name)}/recalculate`, {
                    method: "POST",
                });
                const data = await res.json();
                if (res.status === 409) {
                    showBanner("error", data.message || "Analysis already in progress.");
                    recalcState[name] = "";
                    updateToolbarActions(currentSpec);
                    return;
                }
                if (!res.ok) {
                    showBanner("error", data.detail || "Failed to start recalculation.");
                    recalcState[name] = "";
                    updateToolbarActions(currentSpec);
                    return;
                }
                await pollLensRecalc(name);
            } catch (err) {
                recalcState[name] = "";
                updateToolbarActions(currentSpec);
                if (err.message !== "Unauthenticated") {
                    showBanner("error", `Network error: ${err.message}`);
                }
            }
        }

        async function pollLensRecalc(name) {
            const deadline = Date.now() + 10 * 60 * 1000;  // max wait: 10 minutes
            while (Date.now() < deadline) {
                await new Promise(r => setTimeout(r, 2000));
                let status = null;
                try {
                    const res = await fetchWithAuth(`${ROOT_PATH}/api/v1/status`);
                    if (!res.ok) continue;
                    status = await res.json();
                } catch (err) {
                    if (err.message === "Unauthenticated") {
                        recalcState[name] = "";
                        const currentSpec = lensSpecs.find(s => s.name === editingLensName);
                        updateToolbarActions(currentSpec);
                        return;
                    }
                    continue;
                }
                const lens = status && status.lenses && status.lenses[name];
                if (!lens) continue;  // task may not have started yet; keep polling

                if (lens.status === "done") {
                    recalcState[name] = "done";
                    const currentSpec = lensSpecs.find(s => s.name === editingLensName);
                    updateToolbarActions(currentSpec);
                    await loadLensesData();
                    showBanner("success", `Map \u201c${name}\u201d recalculated (${lens.nodes ?? "?"} nodes, ${lens.edges ?? "?"} edges).`);
                    setTimeout(() => {
                        if (recalcState[name] === "done") {
                            recalcState[name] = "";
                            const cur = lensSpecs.find(s => s.name === editingLensName);
                            updateToolbarActions(cur);
                        }
                    }, 2500);
                    return;
                }
                if (lens.status === "error") {
                    recalcState[name] = "";
                    const currentSpec = lensSpecs.find(s => s.name === editingLensName);
                    updateToolbarActions(currentSpec);
                    await loadLensesData();
                    showBanner("error", `Error recalculating \u201c${name}\u201d: ${lens.error || "unknown error"}`);
                    return;
                }
                if (lens.status === "skipped") {
                    recalcState[name] = "";
                    const currentSpec = lensSpecs.find(s => s.name === editingLensName);
                    updateToolbarActions(currentSpec);
                    await loadLensesData();
                    showBanner("error", `Map \u201c${name}\u201d skipped: ${lens.reason || "no data"}`);
                    return;
                }
                // status === "running": keep waiting
            }
            recalcState[name] = "";
            const currentSpec = lensSpecs.find(s => s.name === editingLensName);
            updateToolbarActions(currentSpec);
            showBanner("error", `Recalculation of \u201c${name}\u201d is taking too long. Check the service logs.`);
        }

        async function loadLensesData() {
            const res = await fetchWithAuth(`${ROOT_PATH}/api/v1/lenses/details`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            lensSpecs = await res.json();
        }

        /* ── Restore running recalculation state after a refresh ── */
        async function resumeRunningLenses() {
            try {
                const res = await fetchWithAuth(`${ROOT_PATH}/api/v1/status`);
                if (!res.ok) return;
                const status = await res.json();
                const lenses = (status && status.lenses) || {};
                lensSpecs.forEach(spec => {
                    const st = lenses[spec.name];
                    if (st && st.status === "running" && recalcState[spec.name] !== "running") {
                        recalcState[spec.name] = "running";
                        pollLensRecalc(spec.name);  // resume polling
                    }
                });
                const currentSpec = lensSpecs.find(s => s.name === editingLensName);
                updateToolbarActions(currentSpec);
            } catch (err) {
                if (err.message !== "Unauthenticated") {
                    console.warn("Could not restore recalculation state:", err.message);
                }
            }
        }

        /* ── Warn before leaving while a lens is recalculating ── */
        window.addEventListener("beforeunload", (e) => {
            if (Object.values(recalcState).includes("running")) {
                e.preventDefault();
                e.returnValue = "";
            }
        });

        /* ── Load DB options (prefixes, scopes, metrics, colors) ── */
        async function loadDbOptions() {
            let availPfx = [], availScope = [], availColors = [], availMetrics = [], availDatasetMetrics = [];
            try {
                const [pfxRes, scopeRes, colorsRes, metricsRes, datasetMetricsRes] = await Promise.all([
                    fetchWithAuth(`${ROOT_PATH}/api/v1/config/available-prefixes`),
                    fetchWithAuth(`${ROOT_PATH}/api/v1/config/available-scopes`),
                    fetchWithAuth(`${ROOT_PATH}/api/v1/config/available-color-columns`),
                    fetchWithAuth(`${ROOT_PATH}/api/v1/config/available-metric-columns`),
                    fetchWithAuth(`${ROOT_PATH}/api/v1/config/available-dataset-metrics`),
                ]);
                if (pfxRes.ok) availPfx = await pfxRes.json();
                if (scopeRes.ok) availScope = await scopeRes.json();
                if (colorsRes.ok) availColors = await colorsRes.json();
                if (metricsRes.ok) availMetrics = await metricsRes.json();
                if (datasetMetricsRes.ok) availDatasetMetrics = await datasetMetricsRes.json();
            } catch (dbErr) {
                if (dbErr.message === "Unauthenticated") throw dbErr;  // re-throw auth errors
                console.warn("Could not load DB options:", dbErr.message);
            }

            formPrefixItems = availPfx.map(p => ({ id: p.id, prefix: p.prefix, name: p.name, selected: false }));
            formScopeItems = availScope.map(s => ({
                id: s.id,
                name: s.name,
                count: s.computer_count || 0,
                title: `${s.computer_count || 0} computers`,
                selected: false,
            }));
            formMetricItems = availDatasetMetrics.map(m => ({ id: m.name, name: m.label, selected: false }));
            availableColors = availColors;
            availableMetrics = availMetrics;
            availableDatasetMetrics = availDatasetMetrics;

            populateMetricSelects();
            populateColorSelect();
        }

        /* ── Banner ───────────────────────────────────────── */
        function showBanner(type, msg) {
            const banner = document.getElementById("statusBanner");
            const icon = document.getElementById("statusIcon");
            document.getElementById("statusText").textContent = msg;
            banner.className = `status-banner ${type} visible`;
            icon.innerHTML = type === "success"
                ? `<polyline points="20 6 9 17 4 12"/>`
                : `<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>`;
            clearTimeout(banner._timeout);
            banner._timeout = setTimeout(() => banner.classList.remove("visible"), 7000);
        }

        function escHtml(s) {
            return String(s)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
        }

        /* ── Init ─────────────────────────────────────────── */
        async function init() {
            try {
                await loadLensesData();
                await loadDbOptions();
                await resumeRunningLenses();
                await loadUserInfo();

                // Check URL hash for target map (e.g. #software or #new)
                const hash = (window.location.hash || "").replace(/^#/, "").trim();
                if (hash === "new") {
                    newLens();
                } else if (hash && lensSpecs.some(s => s.name === hash)) {
                    editLens(hash);
                } else if (lensSpecs.length > 0) {
                    editLens(lensSpecs[0].name);
                } else {
                    newLens();
                }

                // Listen for hash changes in same window
                window.addEventListener("hashchange", () => {
                    const h = (window.location.hash || "").replace(/^#/, "").trim();
                    if (h === "new") {
                        newLens();
                    } else if (h && lensSpecs.some(s => s.name === h) && h !== editingLensName) {
                        editLens(h);
                    }
                });
            } catch (err) {
                if (err.message === "Unauthenticated") {
                    showLoginModal();
                } else {
                    showBanner("error", `Error loading settings: ${err.message}`);
                }
            }
        }

        init();

