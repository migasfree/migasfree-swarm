        "use strict";

        /* ── Configuration ──────────────────────────────────────────────── */
        const ROOT_PATH = "/tda";
        const FQDN = window.location.hostname;
        const MAX_LISTED = 50;           // computers listed before "show more"
        const DEFAULT_LENSES = ["health", "obsolescence", "software", "migration", "sync", "diversity"];

        /* ── State ──────────────────────────────────────────────────────── */
        let activeLens = null;
        let currentLensMeta = null;   // metadata of the lens currently displayed
        let currentData = null;       // raw JSON of the lens currently displayed
        let is3D = true;              // pure 3D rendering mode
        let graph3d = null;           // ForceGraph3D instance
        let nodeScale = 2.5;          // node size multiplier (slider 0..5, default 2.5)
        let currentColorMode = null;  // active color metric mode

        /* ── Metric metadata for live coloring (mapped to dataset columns) ─ */
        const COLOR_METRICS = {
            error_count: { label: "Errors (avg)", unit: "", kind: "continuous", field: "avg_errors" },
            fault_count: { label: "Faults (avg)", unit: "", kind: "continuous", field: "avg_faults" },
            avg_sync_duration_secs: { label: "Sync Duration (avg)", unit: " s", kind: "continuous", field: "avg_sync" },
            sync_count: { label: "Sync Count (avg)", unit: "", kind: "continuous", field: "avg_sync_count" },
            pms_failures: { label: "PMS Failures (avg)", unit: "", kind: "continuous", field: "avg_pms_failures" },
            ram_gb: { label: "RAM (avg)", unit: " GB", kind: "continuous", field: "avg_ram_gb" },
            disk_gb: { label: "Disk (avg)", unit: " GB", kind: "continuous", field: "avg_disk_gb" },
            machine_type: { label: "Machine Type (avg)", unit: "", kind: "continuous", field: "avg_machine_type" },
            computer_age_days: { label: "Computer Age (avg)", unit: " d", kind: "continuous", field: "avg_computer_age_days" },
            days_since_last_sync: { label: "Days Since Sync (avg)", unit: " d", kind: "continuous", field: "avg_days_since_last_sync" },
            total_packages: { label: "Packages (avg)", unit: "", kind: "continuous", field: "avg_packages" },
            migration_count: { label: "Migrations (avg)", unit: "", kind: "continuous", field: "avg_migrations" },
            days_since_last_migration: { label: "Days Since Migration (avg)", unit: " d", kind: "continuous", field: "avg_days_since_migration" },
            jaccard_outlier_score: { label: "Config Outlier Score", unit: "", kind: "continuous", field: "color_value" },
            software_drift_score: { label: "Software Drift Score", unit: "", kind: "continuous", field: "color_value" },
        };

        /* ── Lens label/description map (built-in lenses only) ────────────── */
        const LENS_META = {
            health: { label: "Health", color: "#ef4444", desc: "Error & fault rate" },
            obsolescence: { label: "Obsolescence", color: "#f59e0b", desc: "Hardware capacity & profiles" },
            software: { label: "Software", color: "#10b981", desc: "Package drift & archetypes" },
            migration: { label: "Migration", color: "#6366f1", desc: "Trajectories & bottlenecks" },
            sync: { label: "Sync", color: "#3b82f6", desc: "Sync speed & PMS failures" },
            diversity: { label: "Diversity", color: "#8b5cf6", desc: "Config divergence (Jaccard)" },
        };

        /* ── Stable color for user-defined lenses ────────────────────────── */
        const LENS_PALETTE = ["#ec4899", "#14b8a6", "#f97316", "#84cc16", "#06b6d4", "#a855f7", "#f43f5e", "#64748b"];
        function paletteFor(name) {
            if (LENS_META[name]) return LENS_META[name].color;
            let h = 0;
            for (const ch of String(name)) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
            return LENS_PALETTE[h % LENS_PALETTE.length];
        }

        /* ── Color interpolation (green → amber → red) ───────────────────── */
        function scoreColor(norm) {
            // norm ∈ [0,1]
            if (norm <= 0.5) {
                // green → amber
                const t = norm * 2;
                const r = Math.round(34 + t * (245 - 34));
                const g = Math.round(197 + t * (158 - 197));
                const b = Math.round(94 + t * (11 - 94));
                return `rgb(${r},${g},${b})`;
            } else {
                // amber → red
                const t = (norm - 0.5) * 2;
                const r = Math.round(245 + t * (239 - 245));
                const g = Math.round(158 + t * (68 - 158));
                const b = Math.round(11 + t * (68 - 11));
                return `rgb(${r},${g},${b})`;
            }
        }

        /* ── Node score per lens (fallback for legacy JSON) ──────────────── */
        function nodeScore(node, lens) {
            const d = node.data || node;
            switch (lens) {
                case "health":
                    return (d.avg_errors || 0) + (d.avg_faults || 0);
                case "sync":
                    return (d.avg_sync_duration || 0) / 60 + (d.pms_failures || 0);
                default:
                    return 0;
            }
        }

        /* ── Categorical palette (per project / category) ─────────────────── */
        // Perceptually distinct categorical palette (d3 schemeTableau10). The
        // assignment is deterministic per graph: categories sorted alphabetically
        // map in order, so every distinct value gets a different, well-separated
        // color (a plain name-hash would map similar names to adjacent hues).
        const CATEGORY_COLORS = [
            "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
            "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
        ];
        function buildCategoryMap(nodes, mode) {
            const keys = new Set();
            const prefixFilter = mode && mode.startsWith("prefix:") ? mode.slice(7) : null;

            (nodes || []).forEach(n => {
                const d = n.data || n;
                if (mode === "projects") {
                    const projects = d.projects || [];
                    if (projects && projects.length) {
                        const dom = projects[0];
                        keys.add(String(dom.name != null ? dom.name : (dom.id != null ? dom.id : "?")));
                    }
                } else if (prefixFilter) {
                    const cats = d.color_categories;
                    if (cats) {
                        Object.keys(cats).forEach(k => {
                            const strK = String(k);
                            if (strK.startsWith(prefixFilter + "-") || strK.startsWith(prefixFilter + ":") || strK === prefixFilter) {
                                keys.add(strK);
                            }
                        });
                    }
                    const topList = d.top_attributes || [];
                    topList.forEach(a => {
                        if (a && a.name && (a.name.startsWith(prefixFilter + "-") || a.name.startsWith(prefixFilter + ":") || a.name === prefixFilter)) {
                            keys.add(String(a.name));
                        }
                    });
                } else if (mode === "attributes") {
                    const cats = d.color_categories;
                    if (cats && Object.keys(cats).length) {
                        Object.keys(cats).forEach(k => keys.add(String(k)));
                    } else {
                        const topList = d.top_attributes || [];
                        const distAttr = topList.find(a => a.lift >= 1.2) || topList[0];
                        if (distAttr && distAttr.name) keys.add(String(distAttr.name));
                    }
                } else {
                    const cats = d.color_categories;
                    if (cats) Object.keys(cats).forEach(k => keys.add(String(k)));
                }
            });
            const map = new Map();
            Array.from(keys).sort().forEach((k, i) => {
                map.set(k, CATEGORY_COLORS[i % CATEGORY_COLORS.length]);
            });
            return map;
        }
        function categoryColor(key, map) {
            if (map && map.has(String(key))) return map.get(String(key));
            let h = 0;
            for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) >>> 0;
            return CATEGORY_COLORS[h % CATEGORY_COLORS.length];
        }
        function projectCategoryColor(node, map) {
            const d = node.data || node;
            const projects = d.projects || [];
            if (!projects || !projects.length) return "#94a3b8";
            const dom = projects[0];
            const key = String(dom.name != null ? dom.name : (dom.id != null ? dom.id : "?"));
            return categoryColor(key, map);
        }
        function attributeCategoryColor(node, map, prefixFilter) {
            const d = node.data || node;
            const categories = d.color_categories;
            if (prefixFilter) {
                if (categories) {
                    const matches = Object.entries(categories).filter(([k]) =>
                        k.startsWith(prefixFilter + "-") || k.startsWith(prefixFilter + ":") || k === prefixFilter
                    ).sort((a, b) => b[1] - a[1]);
                    if (matches.length) {
                        return categoryColor(String(matches[0][0]), map);
                    }
                }
                const topList = d.top_attributes || [];
                const matchAttr = topList.find(a =>
                    a && a.name && (a.name.startsWith(prefixFilter + "-") || a.name.startsWith(prefixFilter + ":") || a.name === prefixFilter)
                );
                if (matchAttr) {
                    return categoryColor(String(matchAttr.name), map);
                }
                return "#e2e8f0"; // Neutral background if node doesn't match this prefix
            }

            if (categories && Object.keys(categories).length) {
                const dominant = Object.entries(categories).sort((a, b) => b[1] - a[1])[0];
                return categoryColor(String(dominant[0]), map);
            }
            const topList = d.top_attributes || [];
            const distAttr = topList.find(a => a.lift >= 1.2) || topList[0];
            if (distAttr && distAttr.name) {
                return categoryColor(String(distAttr.name), map);
            }
            return "#94a3b8";
        }

        // Categorical coloring driven by the engine's color_categories
        // (dominant category per node), used e.g. for boolean attribute colors.
        function categoricalNodeColor(node, map) {
            const d = node.data || node;
            const categories = d.color_categories;
            if (categories && Object.keys(categories).length) {
                const dominant = Object.entries(categories).sort((a, b) => b[1] - a[1])[0];
                return categoryColor(String(dominant[0]), map);
            }
            return projectCategoryColor(node, map);
        }

        /* ── Node label: distinctive attribute vs lens metric ───────────── */
        const METRIC_UNITS = {
            error_count: "", fault_count: "", sync_count: "",
            avg_sync_duration_secs: " s", pms_failures: "",
            ram_gb: " GB", disk_gb: " GB", machine_type: "",
            computer_age_days: " d", days_since_last_sync: " d",
            total_packages: "", migration_count: "",
            days_since_last_migration: " d", jaccard_outlier_score: "",
            software_drift_score: "",
        };

        function formatMetricValue(value, colorColumns) {
            const num = Number(value);
            if (value === undefined || value === null || !isFinite(num)) return "";
            const formatted = (Math.round(num * 100) / 100).toLocaleString("en-US", {
                maximumFractionDigits: 2,
            });
            const col = (colorColumns && colorColumns.length) ? colorColumns[0] : "";
            const unit = METRIC_UNITS[col] !== undefined ? METRIC_UNITS[col] : "";
            return formatted + unit;
        }

        /* ── Compute color and norm for a node based on current color mode ─ */
        function getNodeColorInfo(node, mode, data, lens, catMap, minScore, maxScore) {
            const d = node.data || node;
            if (mode && mode.startsWith("prefix:")) {
                const prefixName = mode.slice(7);
                return { color: attributeCategoryColor(node, catMap, prefixName), norm: -1 };
            }

            const metricCfg = mode ? COLOR_METRICS[mode] : null;
            if (metricCfg) {
                if (metricCfg.kind === "categorical") {
                    return { color: categoricalNodeColor(node, catMap), norm: -1 };
                }
                const field = metricCfg.field;
                let val = d[field] !== undefined ? Number(d[field]) : (d.color_value !== undefined ? d.color_value : 0);
                if (!isFinite(val)) val = 0;
                const range = (maxScore - minScore) || 1;
                const norm = Math.max(0, Math.min(1, (val - minScore) / range));
                return { color: scoreColor(norm), norm: norm };
            }

            // Fallback to lens metadata
            const colorMeta = (data.metadata && data.metadata.color) || null;
            const colorKind = colorMeta ? colorMeta.kind : "continuous";
            if (colorKind === "categorical") {
                return { color: categoricalNodeColor(node, catMap), norm: -1 };
            } else {
                const val = d.color_value !== undefined ? d.color_value : nodeScore(d, lens);
                const range = (maxScore - minScore) || 1;
                const norm = Math.max(0, Math.min(1, (val - minScore) / range));
                return { color: scoreColor(norm), norm: norm };
            }
        }

        /* ── 3D node label overlay (DOM layer, projected from 3D world) ─── */
        let labelsVisible = true;
        let label3DRAF = null;

        function toggleLabels(visible) {
            labelsVisible = visible;
            applyLabelMode();
        }

        function applyLabelMode() {
            if (graph3d && is3D) render3DLabelOverlay();
        }

        function buildViewMatrix(camera) {
            const q = camera.quaternion;
            const x = q.x, y = q.y, z = q.z, w = q.w;
            const x2 = x + x, y2 = y + y, z2 = z + z;
            const xx = x * x2, xy = x * y2, xz = x * z2;
            const yy = y * y2, yz = y * z2, zz = z * z2;
            const wx = w * x2, wy = w * y2, wz = w * z2;
            const m00 = 1 - (yy + zz), m01 = xy + wz, m02 = xz - wy;
            const m10 = xy - wz, m11 = 1 - (xx + zz), m12 = yz + wx;
            const m20 = xz + wy, m21 = yz - wx, m22 = 1 - (xx + yy);
            const px = camera.position.x, py = camera.position.y, pz = camera.position.z;
            return [
                m00, m10, m20, 0,
                m01, m11, m21, 0,
                m02, m12, m22, 0,
                -(m00 * px + m01 * py + m02 * pz),
                -(m10 * px + m11 * py + m12 * pz),
                -(m20 * px + m21 * py + m22 * pz),
                1,
            ];
        }

        function project3DPoint(proj, view, x, y, z, width, height) {
            const vx = view[0] * x + view[4] * y + view[8] * z + view[12];
            const vy = view[1] * x + view[5] * y + view[9] * z + view[13];
            const vz = view[2] * x + view[6] * y + view[10] * z + view[14];
            const vw = view[3] * x + view[7] * y + view[11] * z + view[15];
            const cx = proj[0] * vx + proj[4] * vy + proj[8] * vz + proj[12] * vw;
            const cy = proj[1] * vx + proj[5] * vy + proj[9] * vz + proj[13] * vw;
            const cw = proj[3] * vx + proj[7] * vy + proj[11] * vz + proj[15] * vw;
            if (cw <= 0.0001) return null;
            return {
                x: (cx / cw + 1) * 0.5 * width,
                y: (1 - cy / cw) * 0.5 * height,
                depth: Math.sqrt(vx * vx + vy * vy + vz * vz),
            };
        }

        function render3DLabelOverlay() {
            const overlay = document.getElementById("cy-labels");
            if (!overlay) return;
            overlay.innerHTML = "";
            if (!labelsVisible || !graph3d || !is3D) return;

            const renderer = graph3d.renderer();
            const camera = graph3d.camera();
            if (!renderer || !camera) return;
            const canvas = renderer.domElement;
            const width = (canvas.clientWidth || canvas.width) || 0;
            const height = (canvas.clientHeight || canvas.height) || 0;
            if (!width || !height) return;

            const proj = camera.projectionMatrix.elements;
            const view = buildViewMatrix(camera);
            if (!proj) return;

            const nodes = (graph3d.graphData() || {}).nodes || [];

            // Group by distinctive attribute, keep the largest node per group
            const groups = new Map();
            nodes.forEach(n => {
                const dist = n.distLabel;
                if (!dist) return;
                const cur = groups.get(dist);
                if (!cur || (n.size || 0) > (cur.size || 0)) groups.set(dist, n);
            });

            let refDepth = 1;
            const positioned = nodes.filter(n => n.x != null && isFinite(n.x));
            if (positioned.length) {
                let cx = 0, cy = 0, cz = 0;
                positioned.forEach(n => { cx += n.x; cy += n.y; cz += n.z; });
                cx /= positioned.length; cy /= positioned.length; cz /= positioned.length;
                const cvx = view[0] * cx + view[4] * cy + view[8] * cz + view[12];
                const cvy = view[1] * cx + view[5] * cy + view[9] * cz + view[13];
                const cvz = view[2] * cx + view[6] * cy + view[10] * cz + view[14];
                refDepth = Math.max(1, Math.sqrt(cvx * cvx + cvy * cvy + cvz * cvz));
            }

            const sorted3DNodes = Array.from(groups.values()).sort((a, b) => (b.size || 0) - (a.size || 0));
            const rendered3DBoxes = [];

            sorted3DNodes.forEach(n => {
                let wx, wy, wz;
                const obj = n.__threeObj;
                if (obj && obj.position) {
                    wx = obj.position.x; wy = obj.position.y; wz = obj.position.z;
                } else {
                    wx = n.x; wy = n.y; wz = n.z;
                }
                if (wx == null || !isFinite(wx) || wy == null || !isFinite(wy) || wz == null || !isFinite(wz)) return;
                const p = project3DPoint(proj, view, wx, wy, wz, width, height);
                if (!p || !isFinite(p.x) || !isFinite(p.y) || !isFinite(p.depth)) return;
                if (p.x < -60 || p.y < -60 || p.x > width + 60 || p.y > height + 60) return;

                const fSize = Math.max(8, Math.min(22, Math.round(15 * refDepth / p.depth)));
                if (!isFinite(fSize)) return;

                const labelText = n.distLabel;
                const estWidth = labelText.length * (fSize * 0.55) + 16;
                const estHeight = fSize + 10;
                const curBox = {
                    x1: p.x - estWidth / 2,
                    y1: p.y - estHeight / 2,
                    x2: p.x + estWidth / 2,
                    y2: p.y + estHeight / 2,
                };

                const collides = rendered3DBoxes.some(b => {
                    return !(curBox.x2 + 8 < b.x1 || curBox.x1 - 8 > b.x2 || curBox.y2 + 4 < b.y1 || curBox.y1 - 4 > b.y2);
                });

                if (!collides) {
                    rendered3DBoxes.push(curBox);
                    const el = document.createElement("div");
                    el.className = "cy-label";
                    el.style.fontSize = fSize + "px";
                    el.style.left = p.x + "px";
                    el.style.top = p.y + "px";
                    el.textContent = labelText;
                    overlay.appendChild(el);
                }
            });
        }

        function start3DLabelLoop() {
            if (label3DRAF != null) return;
            const tick = () => {
                label3DRAF = null;
                try {
                    if (graph3d && is3D) render3DLabelOverlay();
                } catch (err) {
                    console.error("3D label overlay error:", err);
                }
                label3DRAF = requestAnimationFrame(tick);
            };
            label3DRAF = requestAnimationFrame(tick);
        }

        function stop3DLabelLoop() {
            if (label3DRAF != null) {
                cancelAnimationFrame(label3DRAF);
                label3DRAF = null;
            }
        }

        /* ── 3D force-graph rendering (3d-force-graph) ────────────────────── */
        function init3DGraph(data, lens, drawCfg) {
            if (graph3d) { try { graph3d._destructor(); } catch (_) { } graph3d = null; }
            is3D = true;

            const container = document.getElementById("cy");
            container.innerHTML = "";
            const labelOverlay = document.getElementById("cy-labels");
            if (labelOverlay) labelOverlay.innerHTML = "";

            const colorMeta = (data.metadata && data.metadata.color) || null;
            const nodeLabelMode = (data.metadata && data.metadata.node_label) || "attribute";
            const colorColumns = (colorMeta && colorMeta.columns) || [];
            const nodes = data.nodes || [];

            // Compute score range / categories for active color mode
            let minScore = 0, maxScore = 1, catMap = null;
            if (currentColorMode && currentColorMode.startsWith("prefix:")) {
                catMap = buildCategoryMap(nodes, currentColorMode);
            } else {
                const metricCfg = currentColorMode ? COLOR_METRICS[currentColorMode] : null;
                if (metricCfg) {
                    if (metricCfg.kind === "continuous") {
                        const scores = nodes.map(n => {
                            const val = Number(n[metricCfg.field]);
                            return isFinite(val) ? val : 0;
                        });
                        minScore = scores.length ? Math.min(...scores) : 0;
                        maxScore = scores.length ? Math.max(...scores, minScore + 0.001) : 1;
                    } else {
                        catMap = buildCategoryMap(nodes, metricCfg.mode || "categories");
                    }
                } else {
                    const colorKind = colorMeta ? colorMeta.kind : "continuous";
                    if (colorKind === "continuous") {
                        const scores = nodes.map(n => (n.color_value !== undefined ? n.color_value : nodeScore(n, lens)));
                        minScore = scores.length ? Math.min(...scores) : 0;
                        maxScore = scores.length ? Math.max(...scores, minScore + 0.001) : 1;
                    } else {
                        catMap = buildCategoryMap(nodes, "categories");
                    }
                }
            }

            const graphNodes = nodes.map((n) => {
                const colorInfo = getNodeColorInfo(n, currentColorMode, data, lens, catMap, minScore, maxScore);
                const color = colorInfo.color;
                const radius = Math.max(18, Math.min(60, 18 + Math.sqrt(n.size) * 2.8));
                let distLabel = "";
                if (nodeLabelMode === "metric") {
                    distLabel = formatMetricValue(n.color_value, colorColumns);
                } else {
                    const topList = n.top_attributes || [];
                    const distAttr = topList.find(a => a.lift >= 1.2) || topList[0];
                    distLabel = distAttr ? distAttr.name : "";
                }
                return {
                    id: String(n.id),
                    size: n.size,
                    radius: radius,
                    color: color,
                    color_value: n.color_value !== undefined ? n.color_value : 0,
                    color_categories: n.color_categories || null,
                    distLabel: distLabel,
                    computer_ids: n.computer_ids || [],
                    computer_names: n.computer_names || [],
                    projects: n.projects || {},
                    statuses: n.statuses || {},
                    avg_errors: n.avg_errors || 0,
                    avg_faults: n.avg_faults || 0,
                    avg_sync: n.avg_sync_duration || 0,
                    avg_sync_count: n.avg_sync_count || 0,
                    avg_pms_failures: n.avg_pms_failures || 0,
                    avg_ram_gb: n.avg_ram_gb,
                    avg_disk_gb: n.avg_disk_gb,
                    avg_machine_type: n.avg_machine_type !== undefined ? n.avg_machine_type : 0,
                    machine_types: n.machine_types || {},
                    avg_computer_age_days: n.avg_computer_age_days || 0,
                    avg_days_since_last_sync: n.avg_days_since_last_sync || 0,
                    avg_days_since_migration: n.avg_days_since_migration || 0,
                    avg_packages: n.avg_packages || 0,
                    avg_migrations: n.avg_migrations || 0,
                    migrated_count: n.migrated_count || 0,
                    cpu_models: n.cpu_models || [],
                    gpus: n.gpus || [],
                    top_attributes: n.top_attributes || [],
                    keplerId: n.kepler_id || "",
                };
            });

            const graphLinks = (data.edges || []).map((e, i) => ({
                id: `e${i}`,
                source: String(e.source),
                target: String(e.target),
            }));

            const graph = ForceGraph3D()(container)
                .width(container.clientWidth || window.innerWidth)
                .height(container.clientHeight || window.innerHeight)
                .graphData({ nodes: graphNodes, links: graphLinks })
                .backgroundColor("#ffffff")
                .nodeColor(n => n.color)
                .nodeVal(n => (n.radius || 20) / 8)
                .nodeRelSize(4 * nodeScale)
                .nodeLabel(n => n.distLabel ? `${n.distLabel}\n${n.size} computers` : `${n.size} computers`)
                .linkColor(() => "rgba(148,163,184,0.45)")
                .linkWidth(1.5)
                .linkOpacity(0.7)
                .onNodeClick(n => { showDetail({ data: () => n }); })
                .onNodeHover(n => { container.style.cursor = n ? "pointer" : "default"; });

            graph.numDimensions(3);
            graph.d3Force("charge").strength(-300);
            graph.d3Force("link").distance(70);
            graph3d = graph;
            resizeGraph3D();
            start3DLabelLoop();

            // Automatically frame the whole 3D graph into view with padding
            setTimeout(() => {
                if (is3D && graph3d) {
                    graph3d.zoomToFit(600, 40);
                }
            }, 300);
        }

        /* ── Keep the 3D graph sized to the canvas container ────────────── */
        function resizeGraph3D() {
            if (!graph3d || !is3D) return;
            const container = document.getElementById("cy");
            if (!container) return;
            graph3d.width(container.clientWidth || window.innerWidth)
                .height(container.clientHeight || window.innerHeight);
        }

        window.addEventListener("resize", () => {
            if (is3D && graph3d) resizeGraph3D();
        });

        /* ── Load a lens ────────────────────────────────────────────────── */
        async function selectLens(lens, btn) {
            if (lens === activeLens) return;
            activeLens = lens;

            // Update button styles
            document.querySelectorAll(".lens-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // Update settings link with active map hash
            const settingsLink = document.getElementById("settingsNavLink");
            if (settingsLink) {
                settingsLink.href = `${ROOT_PATH}/settings#${encodeURIComponent(lens)}`;
            }

            // Show loading
            const loading = document.getElementById("cy-loading");
            const placeholder = document.getElementById("cy-placeholder");
            placeholder.style.display = "none";
            loading.classList.add("visible");
            document.getElementById("statsSection").style.display = "none";
            document.getElementById("colorLegend").classList.remove("visible");
            closeDetail();
            currentColorMode = null;
            const searchIn = document.getElementById("computerSearchInput");
            if (searchIn) searchIn.value = "";
            const searchDrop = document.getElementById("searchDropdown");
            if (searchDrop) searchDrop.style.display = "none";
            const clearBtn = document.getElementById("searchClearBtn");
            if (clearBtn) clearBtn.style.display = "none";

            try {
                // Load the graph JSON and the live lens descriptor in parallel.
                // The descriptor carries draw.dimensions so a 2D/3D change takes
                // effect immediately, without recalculating the Mapper.
                const [resp, specResp] = await Promise.all([
                    fetch(`${ROOT_PATH}/api/v1/lens/${lens}/json`),
                    fetch(`${ROOT_PATH}/api/v1/lenses/${lens}`),
                ]);
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                const data = await resp.json();
                const spec = specResp.ok ? await specResp.json() : null;
                currentData = data;
                currentLensMeta = data.metadata || {};

                document.getElementById("relayoutBtn").disabled = false;

                // Update stats & legend immediately
                updateStats(data);
                updateLegend(data);

                renderCurrent(data, lens);
            } catch (err) {
                loading.classList.remove("visible");
                console.error("Error loading map JSON:", err);
                placeholder.style.display = "flex";
                placeholder.querySelector("h3").textContent = "Error loading map";
                placeholder.querySelector("p").textContent = err.message;
            }
        }

        /* ── Render the current data in 3D ──────────────────────────────── */
        function renderCurrent(data, lens) {
            init3DGraph(data, lens, {});
            hideLoading();
        }

        function hideLoading() {
            const loading = document.getElementById("cy-loading");
            if (loading) loading.classList.remove("visible");
        }

        /* ── Update sidebar stats ────────────────────────────────────────── */
        function updateStats(data) {
            const m = data.metadata || {};
            document.getElementById("statComputers").textContent = m.total_computers ?? "—";
            document.getElementById("statNodes").textContent = m.total_nodes ?? "—";
            document.getElementById("statEdges").textContent = m.total_edges ?? "—";
            document.getElementById("statLens").textContent = (m.lens || "—").charAt(0).toUpperCase() + (m.lens || "").slice(1);

            if (m.generated_at) {
                const d = new Date(m.generated_at + (m.generated_at.endsWith("Z") ? "" : "Z"));
                document.getElementById("generatedAt").textContent =
                    "Generated: " + d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
            } else {
                document.getElementById("generatedAt").textContent = "";
            }
            document.getElementById("statsSection").style.display = "block";
        }

        /* ── Populate color mode dropdown with available computed data ───── */
        function populateColorModeSelect(data) {
            const selectEl = document.getElementById("colorModeSelect");
            if (!selectEl || !data) return;

            const m = data.metadata || {};
            const datasetCols = m.dataset_metric_columns || (currentLensMeta && currentLensMeta.dataset_metric_columns) || [];
            const lensColorCols = (m.color && m.color.columns) || [];

            // 1. Gather continuous metric columns from computed dataset
            const availableCols = [];
            datasetCols.forEach(c => {
                if (COLOR_METRICS[c] && !availableCols.includes(c)) availableCols.push(c);
            });
            // Include lens coloring columns if defined (e.g. outlier/drift scores)
            lensColorCols.forEach(c => {
                if (COLOR_METRICS[c] && !availableCols.includes(c)) availableCols.push(c);
            });

            // 2. Discover distinct prefixes from computed nodes
            const discoveredPrefixes = new Set();

            (data.nodes || []).forEach(n => {
                if (n.color_categories) {
                    Object.keys(n.color_categories).forEach(k => {
                        const strK = String(k);
                        const idx = strK.indexOf("-");
                        if (idx > 0) {
                            discoveredPrefixes.add(strK.slice(0, idx));
                        } else {
                            const idxColon = strK.indexOf(":");
                            if (idxColon > 0) discoveredPrefixes.add(strK.slice(0, idxColon));
                        }
                    });
                }
                if (n.top_attributes) {
                    n.top_attributes.forEach(a => {
                        if (a && a.name) {
                            const strA = String(a.name);
                            const idx = strA.indexOf("-");
                            if (idx > 0) {
                                discoveredPrefixes.add(strA.slice(0, idx));
                            } else {
                                const idxColon = strA.indexOf(":");
                                if (idxColon > 0) discoveredPrefixes.add(strA.slice(0, idxColon));
                            }
                        }
                    });
                }
            });

            // Build options (no synthetic 'default' option; configured metric/prefix is directly selected)
            selectEl.innerHTML = "";

            if (availableCols.length) {
                const grpMetrics = document.createElement("optgroup");
                grpMetrics.label = "Dataset Metrics";
                availableCols.forEach(col => {
                    const cfg = COLOR_METRICS[col];
                    if (cfg && cfg.kind === "continuous") {
                        const opt = document.createElement("option");
                        opt.value = col;
                        opt.textContent = cfg.label;
                        grpMetrics.appendChild(opt);
                    }
                });
                if (grpMetrics.children.length) {
                    selectEl.appendChild(grpMetrics);
                }
            }

            const prefixNames = Object.assign(
                {},
                window.tdaPrefixCatalog || {},
                (m && m.prefix_names) || {}
            );
            const prefixList = Array.from(discoveredPrefixes).sort();
            if (prefixList.length) {
                const grpCats = document.createElement("optgroup");
                grpCats.label = "Attributes";
                prefixList.forEach(prefix => {
                    const opt = document.createElement("option");
                    opt.value = `prefix:${prefix}`;
                    const displayName = prefixNames[prefix] || prefixNames[prefix.toUpperCase()] || prefix;
                    opt.textContent = displayName;
                    grpCats.appendChild(opt);
                });
                if (grpCats.children.length) {
                    selectEl.appendChild(grpCats);
                }
            }

            // Determine active/default key from lens metadata if not explicitly set
            const validValues = Array.from(selectEl.options).map(o => o.value);
            let configuredMode = null;
            if (m.color && m.color.columns && m.color.columns.length) {
                const firstCol = m.color.columns[0];
                if (m.color.kind === "categorical" && firstCol.startsWith("prefix_")) {
                    const pMatch = /^prefix_(\d+)$/.exec(firstCol);
                    if (pMatch && prefixList.length) {
                        configuredMode = `prefix:${prefixList[0]}`;
                    }
                } else if (validValues.includes(firstCol)) {
                    configuredMode = firstCol;
                }
            }
            if (!currentColorMode || currentColorMode === "default" || !validValues.includes(currentColorMode)) {
                currentColorMode = configuredMode || (validValues.length ? validValues[0] : "");
            }
            if (currentColorMode) {
                selectEl.value = currentColorMode;
            }
        }

        /* ── Update color legend ─────────────────────────────────────────── */
        function updateLegend(data) {
            const legendEl = document.getElementById("colorLegend");
            const catsBox = document.getElementById("legendCategories");
            const scaleBox = document.getElementById("legendScale");
            const lowLabel = document.getElementById("legendLowLabel");
            const highLabel = document.getElementById("legendHighLabel");
            const selectEl = document.getElementById("colorModeSelect");

            if (!data || !data.nodes || !data.nodes.length) {
                legendEl.classList.remove("visible");
                return;
            }

            populateColorModeSelect(data);

            const m = data.metadata || {};
            const colorMeta = m.color || null;
            const nodes = data.nodes || [];

            let isCategorical = false;
            let catMap = null;
            let minScore = 0, maxScore = 1;
            let unit = "";

            if (currentColorMode && currentColorMode.startsWith("prefix:")) {
                isCategorical = true;
                catMap = buildCategoryMap(nodes, currentColorMode);
            } else {
                const metricCfg = currentColorMode ? COLOR_METRICS[currentColorMode] : null;
                if (metricCfg) {
                    isCategorical = metricCfg.kind === "categorical";
                    unit = metricCfg.unit || "";
                    if (isCategorical) {
                        catMap = buildCategoryMap(nodes, metricCfg.mode || "categories");
                    } else {
                        const scores = nodes.map(n => {
                            const val = Number(n[metricCfg.field]);
                            return isFinite(val) ? val : 0;
                        });
                        minScore = scores.length ? Math.min(...scores) : 0;
                        maxScore = scores.length ? Math.max(...scores, minScore + 0.001) : 1;
                    }
                } else {
                    const colorKind = colorMeta ? colorMeta.kind : "continuous";
                    isCategorical = colorKind === "categorical";
                    if (isCategorical) {
                        catMap = buildCategoryMap(nodes, "categories");
                    } else {
                        const scores = nodes.map(n => (n.color_value !== undefined ? n.color_value : nodeScore(n, activeLens)));
                        minScore = scores.length ? Math.min(...scores) : 0;
                        maxScore = scores.length ? Math.max(...scores, minScore + 0.001) : 1;
                    }
                }
            }

            legendEl.classList.add("visible");

            if (isCategorical) {
                if (scaleBox) scaleBox.style.display = "none";
                catsBox.innerHTML = "";

                if (catMap && catMap.size) {
                    Array.from(catMap.keys()).sort().forEach(k => {
                        const chip = document.createElement("span");
                        chip.className = "legend-cat";
                        const swatch = document.createElement("span");
                        swatch.className = "legend-cat-swatch";
                        swatch.style.background = catMap.get(k);
                        chip.appendChild(swatch);
                        chip.appendChild(document.createTextNode(k));
                        catsBox.appendChild(chip);
                    });
                    catsBox.style.display = "flex";
                } else {
                    catsBox.style.display = "none";
                }
            } else {
                if (catsBox) { catsBox.style.display = "none"; catsBox.innerHTML = ""; }
                if (scaleBox) scaleBox.style.display = "flex";
                const fmtMin = (Math.round(minScore * 100) / 100).toLocaleString("en-US", { maximumFractionDigits: 2 });
                const fmtMax = (Math.round(maxScore * 100) / 100).toLocaleString("en-US", { maximumFractionDigits: 2 });
                if (lowLabel) lowLabel.textContent = `${fmtMin}${unit}`;
                if (highLabel) highLabel.textContent = `${fmtMax}${unit}`;
            }
        }

        /* ── Live change of coloring mode without full recalculation ────── */
        function onColorModeChange(mode) {
            currentColorMode = mode;
            if (!currentData || !currentData.nodes) return;

            const nodes = currentData.nodes || [];
            const data = currentData;
            const lens = activeLens;

            // Recompute min/max or categories
            let minScore = 0, maxScore = 1, catMap = null;
            if (currentColorMode && currentColorMode.startsWith("prefix:")) {
                catMap = buildCategoryMap(nodes, currentColorMode);
            } else {
                const metricCfg = currentColorMode ? COLOR_METRICS[currentColorMode] : null;
                if (metricCfg) {
                    if (metricCfg.kind === "continuous") {
                        const scores = nodes.map(n => {
                            const val = Number(n[metricCfg.field]);
                            return isFinite(val) ? val : 0;
                        });
                        minScore = scores.length ? Math.min(...scores) : 0;
                        maxScore = scores.length ? Math.max(...scores, minScore + 0.001) : 1;
                    } else {
                        catMap = buildCategoryMap(nodes, metricCfg.mode || "categories");
                    }
                } else {
                    const colorMeta = (data.metadata && data.metadata.color) || null;
                    const colorKind = colorMeta ? colorMeta.kind : "continuous";
                    if (colorKind === "continuous") {
                        const scores = nodes.map(n => (n.color_value !== undefined ? n.color_value : nodeScore(n, lens)));
                        minScore = scores.length ? Math.min(...scores) : 0;
                        maxScore = scores.length ? Math.max(...scores, minScore + 0.001) : 1;
                    } else {
                        catMap = buildCategoryMap(nodes, "categories");
                    }
                }
            }

            // Update 3D ForceGraph
            if (graph3d) {
                const graphData = graph3d.graphData();
                if (graphData && graphData.nodes) {
                    graphData.nodes.forEach(n => {
                        const colorInfo = getNodeColorInfo(n, currentColorMode, data, lens, catMap, minScore, maxScore);
                        n.color = colorInfo.color;
                    });
                    graph3d.nodeColor(n => n.color);
                }
            }

            updateLegend(currentData);
        }

        /* ── Graph controls ─────────────────────────────────────────────── */
        function fitGraph() {
            if (graph3d) {
                graph3d.zoomToFit(500, 40);
            }
        }
        function zoomIn() {
            if (graph3d) {
                const pos = graph3d.cameraPosition();
                graph3d.cameraPosition({ x: pos.x * 0.75, y: pos.y * 0.75, z: pos.z * 0.75 }, pos.lookAt, 300);
            }
        }
        function zoomOut() {
            if (graph3d) {
                const pos = graph3d.cameraPosition();
                graph3d.cameraPosition({ x: pos.x * 1.33, y: pos.y * 1.33, z: pos.z * 1.33 }, pos.lookAt, 300);
            }
        }
        function relayout() {
            if (graph3d) {
                graph3d.d3ReheatSimulation();
                setTimeout(() => { if (graph3d) graph3d.zoomToFit(400, 40); }, 200);
            }
        }

        /* ── Node size slider (0..5) ─────────────────────────────────────── */
        function setNodeScale(v) {
            nodeScale = parseFloat(v);
            if (!isFinite(nodeScale) || nodeScale < 0) nodeScale = 0;
            if (nodeScale > 5) nodeScale = 5;

            if (graph3d) {
                graph3d.nodeRelSize(4 * nodeScale);
            }
        }

        /* ── Detail panel ────────────────────────────────────────────────── */
        function escHtml(s) {
            return String(s)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
        }

        /* ── Lens metric cards in the detail panel ──────────────────────── */
        const METRIC_DETAILS = {
            error_count:               { field: "avg_errors",               label: "Avg Errors",        unit: "",    decimals: 2, cls: "red" },
            fault_count:               { field: "avg_faults",               label: "Avg Faults",        unit: "",    decimals: 2, cls: "amber" },
            sync_count:                { field: "avg_sync_count",           label: "Avg Syncs",         unit: "",    decimals: 1, cls: "blue" },
            avg_sync_duration_secs:    { field: "avg_sync",                 label: "Avg Sync",          unit: "m",   decimals: 1, cls: "blue", divBy: 60 },
            pms_failures:              { field: "avg_pms_failures",         label: "PMS Failures",      unit: "",    decimals: 1, cls: "red" },
            ram_gb:                    { field: "avg_ram_gb",               label: "Avg RAM",           unit: "GB",  decimals: 1, cls: "blue" },
            disk_gb:                   { field: "avg_disk_gb",              label: "Avg Disk",          unit: "GB",  decimals: 0, cls: "amber" },
            machine_type:              { field: "avg_machine_type",         label: "Virtual Ratio",     unit: "",    decimals: 2, cls: "violet" },
            computer_age_days:         { field: "avg_computer_age_days",    label: "Avg Age",           unit: "d",   decimals: 0, cls: "blue" },
            days_since_last_sync:      { field: "avg_days_since_last_sync", label: "Days Since Sync",   unit: "d",   decimals: 0, cls: "amber" },
            total_packages:            { field: "avg_packages",             label: "Avg Packages",      unit: "",    decimals: 0, cls: "green" },
            migration_count:           { field: "avg_migrations",           label: "Avg Migrations",    unit: "",    decimals: 1, cls: "indigo" },
            days_since_last_migration: { field: "avg_days_since_migration", label: "Days Since Migration", unit: "d", decimals: 0, cls: "amber" },
            jaccard_outlier_score:     { field: "color_value",              label: "Config Divergence", unit: "",    decimals: 3, cls: "violet" },
            software_drift_score:      { field: "color_value",              label: "Software Drift",    unit: "",    decimals: 3, cls: "green" },
        };
        const METRIC_CARD_COLORS = {
            red: "#ef4444", amber: "#f59e0b", blue: "#3b82f6",
            green: "#10b981", indigo: "#6366f1", violet: "#8b5cf6",
        };

        function renderLensMetricCard(col, d) {
            const spec = METRIC_DETAILS[col];
            if (!spec) return "";
            // color_value only reflects this column when the lens colors by it
            if (spec.field === "color_value") {
                const colorCols = (currentLensMeta && currentLensMeta.color && currentLensMeta.color.columns) || [];
                if (!colorCols.includes(col)) return "";
            }
            const color = METRIC_CARD_COLORS[spec.cls] || "#3b82f6";
            const label = escHtml(spec.label);
            let raw = d[spec.field];
            if (raw === undefined || raw === null || !isFinite(Number(raw))) {
                return `<div class="metric-card"><div class="mv" style="color:${color}">—</div><div class="ml">${label}</div></div>`;
            }
            let num = Number(raw);
            if (spec.divBy) num = num / spec.divBy;
            const dec = spec.decimals !== undefined ? spec.decimals : 1;
            const formatted = (Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec)).toFixed(dec);
            return `<div class="metric-card"><div class="mv" style="color:${color}">${formatted}${spec.unit || ""}</div><div class="ml">${label}</div></div>`;
        }

        function showDetail(node, highlightComputerId = null) {
            const d = typeof node.data === "function" ? node.data() : (node.data || node);
            const panel = document.getElementById("detailPanel");
            const body = document.getElementById("detailBody");
            const title = document.getElementById("detailTitle");

            title.textContent = `Cluster #${d.id} — ${d.size} computer${d.size !== 1 ? "s" : ""}`;

            // Dynamic metrics section: show only the metrics included in the
            // lens data matrix (dataset_metric_columns).  Color columns
            // (jaccard_outlier_score, software_drift_score) are appended when
            // they are part of the coloring function but not in the dataset
            // metrics.  A "Computers" count card is always rendered.
            let html = '';
            {
                // 1. Determine which metric columns to display
                const datasetCols = (currentLensMeta && currentLensMeta.dataset_metric_columns)
                    ? currentLensMeta.dataset_metric_columns
                    : null;
                const colorCols = (currentLensMeta && currentLensMeta.color && currentLensMeta.color.columns) || [];

                let displayCols;
                if (datasetCols && datasetCols.length) {
                    // Use the dataset metrics; append color-only columns that
                    // are not already in the list (e.g. jaccard_outlier_score)
                    displayCols = [...datasetCols];
                    colorCols.forEach(c => {
                        if (!displayCols.includes(c)) displayCols.push(c);
                    });
                } else if (datasetCols !== null) {
                    // datasetCols is explicitly empty ([]): only show color columns
                    displayCols = [...colorCols];
                } else {
                    // Legacy cached graph without dataset_metric_columns:
                    // fall back to lens metric_columns, then color columns
                    const lensCols = (currentLensMeta && currentLensMeta.metric_columns)
                        ? currentLensMeta.metric_columns
                        : [];
                    displayCols = lensCols.length ? [...lensCols] : [...colorCols];
                }

                // 2. Build metric cards
                const metricCards = displayCols
                    .map(c => renderLensMetricCard(c, d))
                    .filter(c => c);

                // 3. Always add a "Computers" count card
                const sizeColor = "#8b5cf6";
                metricCards.push(
                    `<div class="metric-card" style="border-color:rgba(139,92,246,0.3);">` +
                    `<div class="mv" style="color:${sizeColor}">${d.size}</div>` +
                    `<div class="ml">Computers</div></div>`
                );

                // 4. Lens-specific extras (hardware details for obsolescence,
                //    migrated-count for migration)
                let extras = '';
                if (activeLens === 'obsolescence') {
                    if (d.cpu_models && d.cpu_models.length) {
                        extras += `<div style="margin-top:0.6rem;font-size:0.75rem;color:var(--brand-secondary);line-height:1.3;">
                        <strong>CPU:</strong> ${d.cpu_models.join(', ')}
                    </div>`;
                    }
                    if (d.gpus && d.gpus.length) {
                        extras += `<div style="margin-top:0.3rem;font-size:0.75rem;color:var(--brand-secondary);line-height:1.3;">
                        <strong>GPU:</strong> ${d.gpus.join(', ')}
                    </div>`;
                    }
                }
                if (activeLens === 'migration') {
                    const migRatio = `${d.migrated_count || 0} / ${d.size || 0}`;
                    // Prepend the migrated count card
                    metricCards.unshift(
                        `<div class="metric-card" style="border-color:rgba(99,102,241,0.3);">` +
                        `<div class="mv" style="color:#6366f1;">${migRatio}</div>` +
                        `<div class="ml">Migrated PCs</div></div>`
                    );
                }
                if (activeLens === 'diversity') {
                    const distCount = (d.top_attributes || []).filter(a => a.lift >= 1.5).length;
                    metricCards.splice(metricCards.length - 1, 0,
                        `<div class="metric-card amber">` +
                        `<div class="mv">${distCount}</div>` +
                        `<div class="ml">Distinctive Attributes</div></div>`
                    );
                }

                html += `
            <div>
                <p class="detail-section-title">Metrics</p>
                <div class="detail-metrics">
                    ${metricCards.join("")}
                </div>
                ${extras}
            </div>`;
            }

            // Reason for grouping: characteristic attributes of the node
            const topAttrs = d.top_attributes || [];
            if (topAttrs.length) {
                html += `<div>
                <p class="detail-section-title">Why are these computers grouped?</p>
                <div class="attr-reason-list">`;
                topAttrs.forEach(a => {
                    const name = escHtml(a.name);
                    const distinctive = a.lift >= 1.5;
                    const badge = distinctive
                        ? `<span class="attr-star" title="Atributo distintivo: mucho más presente en este nodo que en el resto de la flota">★</span>`
                        : "";
                    html += `<div class="attr-reason ${distinctive ? "attr-reason-dist" : ""}">
                        <span class="attr-name">${name}</span>
                        <span class="attr-bar"><span class="attr-bar-fill" style="width:${Math.min(100, a.pct)}%"></span></span>
                        <span class="attr-pct">${a.pct}%</span>
                        ${badge}
                    </div>`;
                });
                html += `</div></div>`;
            }

            // Projects
            const projects = d.projects || [];
            let projectList = [];
            if (Array.isArray(projects)) {
                projectList = projects;
            } else if (typeof projects === "object") {
                projectList = Object.keys(projects).map(k => ({
                    id: /^\d+$/.test(k) ? k : null,
                    name: /^\d+$/.test(k) ? `Project ${k}` : k,
                    count: projects[k]
                }));
            }

            if (projectList.length) {
                html += `<div>
                <p class="detail-section-title">Projects (${projectList.length})</p>
                <div class="badge-list">`;
                projectList.forEach(p => {
                    const label = p.name || `Project ${p.id}`;
                    if (p.id) {
                        html += `<a class="badge" style="text-decoration:none;cursor:pointer;display:inline-flex;align-items:center;"
                                href="https://${FQDN}/projects/results/${p.id}" target="_blank" rel="noopener">
                                ${label}<span class="badge-count">${p.count}</span>
                             </a>`;
                    } else {
                        html += `<span class="badge">${label}<span class="badge-count">${p.count}</span></span>`;
                    }
                });
                html += `</div></div>`;
            }

            // Statuses
            const statuses = d.statuses || {};
            const statusKeys = Object.keys(statuses);
            if (statusKeys.length) {
                html += `<div>
                <p class="detail-section-title">Statuses</p>
                <div class="badge-list">`;
                statusKeys.forEach(k => {
                    html += `<span class="badge">${k}<span class="badge-count">${statuses[k]}</span></span>`;
                });
                html += `</div></div>`;
            }

            // Computers list
            const ids = d.computer_ids || [];
            const names = d.computer_names || [];
            const computers = ids.map((id, i) => ({ id, name: names[i] || null }));

            let shownComputers = computers.slice(0, MAX_LISTED);
            let remaining = ids.length - shownComputers.length;

            if (highlightComputerId != null && !shownComputers.some(c => c.id === highlightComputerId)) {
                const found = computers.find(c => c.id === highlightComputerId);
                if (found) {
                    shownComputers.unshift(found);
                    remaining = Math.max(0, ids.length - shownComputers.length);
                }
            }

            html += `<div>
            <p class="detail-section-title">Computers (${ids.length})</p>
            <div class="computers-list" id="computersList">`;
            shownComputers.forEach(({ id, name }) => {
                const isMatch = (highlightComputerId != null && id === highlightComputerId);
                const label = name ? `${escHtml(name)} <span style="opacity:.5;font-weight:400">#${id}</span>` : `#${id}`;
                const highlightStyle = isMatch
                    ? 'background:rgba(162,28,175,0.18);border-color:var(--brand-primary);font-weight:600;'
                    : '';
                html += `<a class="computer-link" id="comp-item-${id}" style="${highlightStyle}"
                        href="https://${FQDN}/computers/results/${id}"
                        target="_blank" rel="noopener">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                    <line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                ${label}
                ${isMatch ? '<span style="margin-left:auto;font-size:0.68rem;color:var(--brand-primary);background:rgba(162,28,175,0.12);padding:1px 6px;border-radius:4px;font-weight:600;">Match</span>' : ''}
            </a>`;
            });
            html += `</div>`;
            if (remaining > 0) {
                html += `<button class="show-more-btn" onclick="showAllComputers(${JSON.stringify(computers)}, ${highlightComputerId != null ? highlightComputerId : 'null'})">
                Show ${remaining} more…
            </button>`;
            }
            html += `</div>`;

            body.innerHTML = html;
            panel.classList.add("open");

            if (highlightComputerId != null) {
                setTimeout(() => {
                    const el = document.getElementById(`comp-item-${highlightComputerId}`);
                    if (el) el.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }, 120);
            }
        }

        function closeDetail(e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            const panel = document.getElementById("detailPanel");
            if (panel) panel.classList.remove("open");
        }

        /* ── Edge detail: why is this edge displayed ─────────────────────── */
        function showEdgeDetail(edge) {
            const d = edge.data();
            const panel = document.getElementById("detailPanel");
            const body = document.getElementById("detailBody");
            const title = document.getElementById("detailTitle");

            const shared = d.shared_computer_ids || [];
            title.textContent = `Edge ${d.sourceNode} \u2194 ${d.targetNode} \u2014 ${d.shared_count || 0} shared computer${(d.shared_count || 0) !== 1 ? "s" : ""}`;

            let html = `<div>
                <p class="detail-section-title">Why is this edge displayed?</p>
                <p style="font-size:0.82rem;color:var(--brand-secondary);line-height:1.55;margin:0 0 0.25rem;">`;
            if (shared.length === 0) {
                html += `This edge connects clusters ${d.sourceNode} and ${d.targetNode}.`;
            } else {
                html += `The clusters ${d.sourceNode} and ${d.targetNode} are linked because these computers appear in <b>both</b> nodes (Mapper cover overlap):`;
            }
            html += `</p></div>`;

            if (shared.length) {
                const names = d.shared_computer_names || [];
                html += `<div>
                    <p class="detail-section-title">Shared computers (${shared.length})</p>
                    <div class="computers-list">`;
                shared.forEach((id, i) => {
                    const label = names[i] ? `${escHtml(names[i])} <span style="opacity:.5;font-weight:400">#${id}</span>` : `#${id}`;
                    html += `<a class="computer-link"
                            href="https://${FQDN}/computers/results/${id}"
                            target="_blank" rel="noopener">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                        <line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
                    </svg>
                    ${label}
                </a>`;
                });
                html += `</div></div>`;
            }

            body.innerHTML = html;
            panel.classList.add("open");
        }

        function showAllComputers(computers, highlightComputerId = null) {
            const list = document.getElementById("computersList");
            if (!list) return;
            list.innerHTML = "";
            computers.forEach(({ id, name }) => {
                const isMatch = (highlightComputerId != null && id === highlightComputerId);
                const label = name ? `${escHtml(name)} <span style="opacity:.5;font-weight:400">#${id}</span>` : `#${id}`;
                const highlightStyle = isMatch
                    ? 'background:rgba(162,28,175,0.18);border-color:var(--brand-primary);font-weight:600;'
                    : '';
                list.innerHTML += `<a class="computer-link" id="comp-item-${id}" style="${highlightStyle}"
                    href="https://${FQDN}/computers/results/${id}"
                    target="_blank" rel="noopener">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                    <line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                ${label}
                ${isMatch ? '<span style="margin-left:auto;font-size:0.68rem;color:var(--brand-primary);background:rgba(162,28,175,0.12);padding:1px 6px;border-radius:4px;font-weight:600;">Match</span>' : ''}
            </a>`;
            });
            const btn = document.querySelector(".show-more-btn");
            if (btn) btn.remove();

            if (highlightComputerId != null) {
                setTimeout(() => {
                    const el = document.getElementById(`comp-item-${highlightComputerId}`);
                    if (el) el.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }, 120);
            }
        }

        /* ── Computer Search & Locate ───────────────────────────────────── */
        let searchDebounceTimer = null;

        function handleComputerSearch(query) {
            clearTimeout(searchDebounceTimer);
            searchDebounceTimer = setTimeout(() => {
                executeComputerSearch(query);
            }, 100);
        }

        function handleSearchKeyDown(e) {
            if (e.key === "Escape") {
                clearComputerSearch(e);
            } else if (e.key === "Enter") {
                e.preventDefault();
                const dropdown = document.getElementById("searchDropdown");
                if (dropdown && dropdown.style.display !== "none") {
                    const firstItem = dropdown.querySelector(".search-item");
                    if (firstItem) {
                        firstItem.click();
                    }
                }
            }
        }

        function executeComputerSearch(query) {
            const dropdown = document.getElementById("searchDropdown");
            const clearBtn = document.getElementById("searchClearBtn");
            const q = (query || "").trim().toLowerCase();

            if (!q) {
                if (dropdown) {
                    dropdown.style.display = "none";
                    dropdown.innerHTML = "";
                }
                if (clearBtn) clearBtn.style.display = "none";
                clearSearchHighlight();
                return;
            }

            if (clearBtn) clearBtn.style.display = "flex";

            if (!currentData || !currentData.nodes || !currentData.nodes.length) {
                if (dropdown) {
                    dropdown.innerHTML = `<div class="search-no-results">No graph data loaded</div>`;
                    dropdown.style.display = "flex";
                }
                return;
            }

            // Search matches in currentData.nodes (works in both 2D and 3D)
            const matches = [];
            const cleanQ = q.startsWith("#") ? q.slice(1).trim() : q;
            if (!cleanQ) return;

            currentData.nodes.forEach(node => {
                const ids = node.computer_ids || [];
                const names = node.computer_names || [];

                ids.forEach((cid, i) => {
                    const cname = names[i] || "";
                    const idStr = String(cid);
                    const nameStr = String(cname).toLowerCase();

                    if (idStr.includes(cleanQ) || nameStr.includes(cleanQ)) {
                        matches.push({
                            nodeId: String(node.id),
                            clusterId: node.id,
                            clusterSize: node.size,
                            computerId: cid,
                            computerName: cname || `#${cid}`
                        });
                    }
                });
            });

            // Render dropdown
            if (!dropdown) return;
            if (matches.length === 0) {
                dropdown.innerHTML = `<div class="search-no-results">No computers found matching "${escHtml(query)}"</div>`;
            } else {
                const topMatches = matches.slice(0, 30);
                dropdown.innerHTML = topMatches.map(m => `
                    <div class="search-item" onclick="locateComputer('${m.nodeId}', ${m.computerId})">
                        <div class="search-item-name">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                                <line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
                            </svg>
                            <span>${escHtml(m.computerName)}</span>
                            <span style="opacity:0.5;font-weight:400;font-size:0.72rem;">#${m.computerId}</span>
                        </div>
                        <span class="search-item-cluster">Cluster #${m.clusterId} (${m.clusterSize} PCs)</span>
                    </div>
                `).join("");
                if (matches.length > 30) {
                    dropdown.innerHTML += `<div class="search-no-results" style="border-top:1px solid rgba(0,0,0,0.05);padding:6px;">+${matches.length - 30} more results… refine search</div>`;
                }
            }
            dropdown.style.display = "flex";
        }

        function locateComputer(nodeId, computerId) {
            const dropdown = document.getElementById("searchDropdown");
            if (dropdown) dropdown.style.display = "none";

            const strNodeId = String(nodeId);
            const numComputerId = computerId != null ? Number(computerId) : null;

            if (graph3d) {
                const gData = graph3d.graphData();
                const targetNode = (gData.nodes || []).find(n => String(n.id) === strNodeId);
                if (targetNode) {
                    const distance = 90;
                    const hyp = Math.hypot(targetNode.x || 1, targetNode.y || 1, targetNode.z || 1);
                    const distRatio = 1 + distance / (hyp || 1);
                    graph3d.cameraPosition(
                        { x: (targetNode.x || 0) * distRatio, y: (targetNode.y || 0) * distRatio, z: (targetNode.z || 0) * distRatio },
                        targetNode,
                        800
                    );
                    showDetail({ data: () => targetNode }, numComputerId);
                }
            }
        }

        function clearSearchHighlight() {
        }

        function clearComputerSearch(e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            const input = document.getElementById("computerSearchInput");
            if (input) {
                input.value = "";
                input.focus();
            }
            const dropdown = document.getElementById("searchDropdown");
            if (dropdown) {
                dropdown.style.display = "none";
                dropdown.innerHTML = "";
            }
            const clearBtn = document.getElementById("searchClearBtn");
            if (clearBtn) clearBtn.style.display = "none";
            clearSearchHighlight();
            closeDetail();
        }

        // Close search dropdown on click outside
        document.addEventListener("click", function (e) {
            const searchContainer = document.querySelector(".search-container");
            const dropdown = document.getElementById("searchDropdown");
            if (searchContainer && dropdown && !searchContainer.contains(e.target)) {
                dropdown.style.display = "none";
            }
        });

        /* ── Trigger On-Demand Recalculation ────────────────────────────── */
        let pollInterval = null;

        function confirmRecalculate() {
            const confirmModal = document.getElementById("recalc-confirm-modal");
            if (confirmModal) confirmModal.style.display = "flex";
        }

        function closeRecalcConfirmModal() {
            const confirmModal = document.getElementById("recalc-confirm-modal");
            if (confirmModal) confirmModal.style.display = "none";
        }

        async function acceptRecalculate() {
            closeRecalcConfirmModal();
            await triggerRecalculate();
        }

        async function triggerRecalculate() {
            const btn = document.getElementById("recalcBtn");
            const icon = document.getElementById("recalcIcon");
            const modal = document.getElementById("recalc-modal");
            const logsContainer = document.getElementById("recalc-logs-container");
            const stepBadge = document.getElementById("recalc-step-badge");

            btn.disabled = true;
            icon.style.animation = "spin 1s linear infinite";

            logsContainer.innerHTML = '<div style="color:#94a3b8;">Triggering recalculation run…</div>';
            stepBadge.textContent = "Starting";
            stepBadge.style.background = "var(--brand-primary)";
            const spinner = document.getElementById("recalc-spinner");
            const title = document.getElementById("recalc-modal-title");
            const closeBtn = document.getElementById("recalc-close-btn");
            const footerInfo = document.getElementById("recalc-footer-info");
            if (spinner) spinner.style.display = "block";
            if (title) title.textContent = "Recalculating TDA Topology…";
            if (closeBtn) closeBtn.style.display = "none";
            if (footerInfo) footerInfo.textContent = "Updating all 6 mathematical projections";
            modal.style.display = "flex";

            try {
                const resp = await fetch(`${ROOT_PATH}/api/v1/recalculate`, { method: "POST" });
                if (!resp.ok && resp.status !== 409) {
                    throw new Error(`HTTP ${resp.status}`);
                }

                // Start live status polling (every 1s)
                if (pollInterval) clearInterval(pollInterval);
                pollInterval = setInterval(pollRecalcStatus, 1000);

            } catch (err) {
                console.error("Recalculate trigger error:", err);
                modal.style.display = "none";
                btn.disabled = false;
                icon.style.animation = "none";
                alert(`Error starting recalculation: ${err.message}`);
            }
        }

        async function pollRecalcStatus() {
            try {
                const resp = await fetch(`${ROOT_PATH}/api/v1/status`);
                if (!resp.ok) return;
                const status = await resp.json();

                const modal = document.getElementById("recalc-modal");
                const logsContainer = document.getElementById("recalc-logs-container");
                const stepBadge = document.getElementById("recalc-step-badge");

                if (status.current_step) {
                    stepBadge.textContent = status.current_step;
                }

                if (status.logs && status.logs.length) {
                    logsContainer.innerHTML = status.logs.map(line => {
                        let color = "#e2e8f0";
                        if (line.includes("✓")) color = "#4ade80";
                        else if (line.includes("✗") || line.includes("Error") || line.includes("Fatal")) color = "#f87171";
                        else if (line.includes("Warning")) color = "#fbbf24";
                        else if (line.includes("Computing lens")) color = "#60a5fa";
                        return `<div style="color:${color};">${line}</div>`;
                    }).join("");
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                }

                if (!status.is_running) {
                    // Done!
                    clearInterval(pollInterval);
                    pollInterval = null;

                    const btn = document.getElementById("recalcBtn");
                    const icon = document.getElementById("recalcIcon");
                    const spinner = document.getElementById("recalc-spinner");
                    const title = document.getElementById("recalc-modal-title");
                    const closeBtn = document.getElementById("recalc-close-btn");
                    const footerInfo = document.getElementById("recalc-footer-info");

                    btn.disabled = false;
                    icon.style.animation = "none";

                    if (spinner) spinner.style.display = "none";
                    if (title) title.textContent = "Recalculation Complete";
                    if (stepBadge) {
                        stepBadge.textContent = "Success";
                        stepBadge.style.background = "#16a34a";
                    }
                    if (footerInfo) {
                        footerInfo.textContent = `Completed in ${status.last_run_duration || 0}s`;
                    }
                    if (closeBtn) {
                        closeBtn.style.display = "inline-block";
                    }

                    // Refresh current lens or reload lenses in background
                    if (activeLens) {
                        const activeBtn = document.querySelector(`.lens-btn[data-lens="${activeLens}"]`);
                        if (activeBtn) {
                            activeLens = null; // force reload
                            selectLens(activeBtn.getAttribute("data-lens"), activeBtn);
                        }
                    } else {
                        loadLenses();
                    }
                }
            } catch (err) {
                console.error("Poll status error:", err);
            }
        }

        function closeRecalcModal() {
            const modal = document.getElementById("recalc-modal");
            if (modal) modal.style.display = "none";
        }

        /* ── Bootstrap: load lens list ──────────────────────────────────── */
        async function loadLenses() {
            const listEl = document.getElementById("lensList");
            try {
                const resp = await fetch(`${ROOT_PATH}/api/v1/lenses`);
                if (resp.status === 401 || resp.status === 403) {
                    checkAuth();
                    return;
                }
                const availableLenses = await resp.json();

                // Fetch lens descriptors (label/description of built-in + custom lenses)
                let lensDetails = [];
                try {
                    const [det, pfx] = await Promise.all([
                        fetch(`${ROOT_PATH}/api/v1/lenses/details`),
                        fetch(`${ROOT_PATH}/api/v1/config/available-prefixes`)
                    ]);
                    if (det.ok) lensDetails = await det.json();
                    if (pfx.ok) {
                        const pfxList = await pfx.json();
                        window.tdaPrefixCatalog = {};
                        pfxList.forEach(p => {
                            if (p.prefix && p.name) {
                                window.tdaPrefixCatalog[p.prefix] = p.name;
                                window.tdaPrefixCatalog[p.prefix.toUpperCase()] = p.name;
                            }
                        });
                    }
                } catch (_) {}
                const detailsMap = {};
                lensDetails.forEach(s => { detailsMap[s.name] = s; });

                // Display order: store descriptors first, then fallback
                const lensesToDisplay = (lensDetails && lensDetails.length)
                    ? lensDetails.map(s => s.name)
                    : (availableLenses && availableLenses.length > 0
                        ? availableLenses
                        : DEFAULT_LENSES);

                if (!lensesToDisplay || lensesToDisplay.length === 0) {
                    listEl.innerHTML = '<p style="font-size:0.85rem;color:var(--brand-secondary);font-style:italic;">No maps defined.<br>Click "Recalculate Now" to generate graphs, or create maps in Settings.</p>';
                    return;
                }

                listEl.innerHTML = "";
                lensesToDisplay.forEach(lens => {
                    const isAvailable = availableLenses.includes(lens);
                    const spec = detailsMap[lens];
                    const meta = LENS_META[lens] || {
                        label: (spec && spec.label) || lens,
                        color: paletteFor(lens),
                        desc: (spec && spec.description) || "",
                    };
                    const btn = document.createElement("button");
                    btn.className = "lens-btn";
                    btn.setAttribute("data-lens", lens);
                    if (!isAvailable) {
                        btn.style.opacity = "0.6";
                        btn.title = "Graph not yet generated. Click Recalculate Now to generate.";
                    }
                    btn.innerHTML = `
                    <span class="lens-dot" style="background:${meta.color}"></span>
                    ${meta.label || lens.charAt(0).toUpperCase() + lens.slice(1)}
                    <span class="lens-meta">${meta.desc || (isAvailable ? "" : "Not generated")}</span>`;
                    btn.onclick = () => selectLens(lens, btn);
                    listEl.appendChild(btn);
                });

                // Auto-select the lens requested via #<lens>, or the first available one
                let targetBtn = null;
                const hashLens = (window.location.hash || "").replace(/^#/, "");
                if (hashLens) {
                    targetBtn = listEl.querySelector(`.lens-btn[data-lens="${hashLens}"]`);
                }
                if (!targetBtn) {
                    targetBtn = listEl.querySelector(`.lens-btn:not([style*="opacity"])`) || listEl.querySelector(".lens-btn");
                }
                if (targetBtn) targetBtn.click();

            } catch (err) {
                console.error("Error loading lenses:", err);
                listEl.innerHTML = `<p style="color:var(--error, #ef4444);font-size:0.85rem;">Error loading lenses: ${err.message}</p>`;
            }
        }

        /* ── Authentication State & Logic ──────────────────────────────── */
        let currentUser = null;

        async function checkAuth() {
            const loginModal = document.getElementById("login-modal");
            const profileSection = document.getElementById("userProfileSection");
            try {
                const resp = await fetch(`${ROOT_PATH}/api/v1/auth/me`);
                if (resp.status === 401 || resp.status === 403) {
                    // Show login modal
                    loginModal.style.display = "flex";
                    profileSection.style.display = "none";
                    return false;
                }
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

                currentUser = await resp.json();
                loginModal.style.display = "none";

                // Render profile
                const nameEl = document.getElementById("userName");
                const roleEl = document.getElementById("userRole");
                const avatarEl = document.getElementById("userAvatar");

                const displayName = currentUser.first_name ? `${currentUser.first_name} ${currentUser.last_name || ""}` : currentUser.username;
                nameEl.textContent = displayName;
                roleEl.textContent = currentUser.is_superuser ? "Superuser" : "Staff";
                avatarEl.textContent = (currentUser.username || "U").charAt(0).toUpperCase();
                profileSection.style.display = "flex";

                loadLenses();
                return true;
            } catch (err) {
                console.error("Auth check failed:", err);
                loginModal.style.display = "flex";
                profileSection.style.display = "none";
                return false;
            }
        }

        async function submitLogin(e) {
            e.preventDefault();
            const username = document.getElementById("loginUsername").value.trim();
            const password = document.getElementById("loginPassword").value;
            const errEl = document.getElementById("loginError");
            const btn = document.getElementById("loginSubmitBtn");

            errEl.style.display = "none";
            btn.disabled = true;
            btn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;border-top-color:#fff;"></div> Signing in…';

            try {
                const resp = await fetch(`${ROOT_PATH}/api/v1/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });

                const data = await resp.json();
                if (!resp.ok) {
                    throw new Error(data.detail || "Authentication failed");
                }

                // Success
                btn.disabled = false;
                btn.innerHTML = '<span>Sign in</span>';
                await checkAuth();

            } catch (err) {
                btn.disabled = false;
                btn.innerHTML = '<span>Sign in</span>';
                errEl.textContent = err.message;
                errEl.style.display = "block";
            }
        }

        async function logout() {
            try {
                await fetch(`${ROOT_PATH}/api/v1/auth/logout`, { method: "POST" });
            } catch (_) { }
            // Clear all cookies
            document.cookie = "tda_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            document.cookie = "mf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            document.cookie = "auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

            currentUser = null;
            document.getElementById("userProfileSection").style.display = "none";
            document.getElementById("lensList").innerHTML = "";
            if (graph3d) { try { graph3d._destructor(); } catch (_) { } graph3d = null; }
            const cyContainer = document.getElementById("cy");
            if (cyContainer) cyContainer.innerHTML = "";
            document.getElementById("cy-placeholder").style.display = "flex";
            document.getElementById("statsSection").style.display = "none";
            document.getElementById("colorLegend").classList.remove("visible");

            const loginModal = document.getElementById("login-modal");
            loginModal.style.display = "flex";
            const passInput = document.getElementById("loginPassword");
            if (passInput) passInput.value = "";
        }

        /* ── Bootstrap: start auth check ────────────────────────────────── */
        checkAuth();
