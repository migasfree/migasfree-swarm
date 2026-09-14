"""
Unit tests for TDA Microservice Components
"""
import sys
import os
import unittest

# Add app to path
APP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "defaults", "app")
sys.path.insert(0, APP_DIR)

from lens_store import (
    BUILTIN_LENSES,
    validate_lens,
    DATASET_METRICS,
)
from tda_worker import get_lens_specs_for_run
from engine.sql_builder import (
    build_sql_errors,
    build_sql_faults,
    build_sql_sync,
    build_sql_all_attributes,
)


try:
    import pandas as pd
    import numpy as np
    from tda_engine import apply_lens_projection
    HAS_ENGINE_DEPS = True
except ImportError:
    HAS_ENGINE_DEPS = False


class TestTdaEngine(unittest.TestCase):
    def test_builtin_lenses_loaded(self):
        """Verify that all 6 default built-in lenses are loaded from JSON."""
        names = {l["name"] for l in BUILTIN_LENSES}
        expected = {"health", "obsolescence", "software", "migration", "sync", "diversity"}
        self.assertTrue(expected.issubset(names), f"Missing lenses in {names}")

    def test_get_lens_specs_for_run(self):
        """Verify get_lens_specs_for_run returns lenses with scheduled=True."""
        specs = get_lens_specs_for_run()
        self.assertTrue(len(specs) >= 6)
        for spec in specs:
            self.assertTrue(spec.get("scheduled", True))

    def test_sql_builder_filters(self):
        """Verify SQL builder query outputs."""
        sql_err = build_sql_errors(30)
        self.assertIn("INTERVAL '30 days'", sql_err)

        sql_fault = build_sql_faults(60)
        self.assertIn("INTERVAL '60 days'", sql_fault)

        sql_sync = build_sql_sync(15)
        self.assertIn("INTERVAL '15 days'", sql_sync)

        sql_attrs = build_sql_all_attributes([3, 5])
        self.assertIn("a.property_att_id=3", sql_attrs)
        self.assertIn("a.property_att_id=5", sql_attrs)

    def test_validate_lens_valid(self):
        """Verify validation of a proper custom lens."""
        sample = {
            "name": "custom-test",
            "label": "Custom Test Lens",
            "description": "A unit test lens",
            "lens": {"type": "pca", "components": 2},
        }
        validated = validate_lens(sample)
        self.assertEqual(validated["name"], "custom-test")
        self.assertEqual(validated["label"], "Custom Test Lens")
        self.assertEqual(validated["lens"]["type"], "pca")

    def test_validate_lens_invalid_name(self):
        """Verify invalid lens name is rejected."""
        sample = {
            "name": "INVALID NAME WITH SPACES!",
            "label": "Invalid",
        }
        with self.assertRaises(ValueError):
            validate_lens(sample)

    def test_validate_lens_umap(self):
        """Verify validation and normalization of a UMAP lens."""
        sample = {
            "name": "umap-software",
            "label": "UMAP Software",
            "lens": {
                "type": "umap",
                "components": 2,
                "matrix_source": "packages",
                "n_neighbors": 20,
                "min_dist": 0.25,
            },
        }
        validated = validate_lens(sample)
        self.assertEqual(validated["name"], "umap-software")
        self.assertEqual(validated["lens"]["type"], "umap")
        self.assertEqual(validated["lens"]["matrix_source"], "packages")
        self.assertEqual(validated["lens"]["n_neighbors"], 20)
        self.assertEqual(validated["lens"]["min_dist"], 0.25)

        # Test defaults when omitted
        sample_default = {
            "name": "umap-default",
            "label": "UMAP Default",
            "lens": {"type": "umap"},
        }
        validated_default = validate_lens(sample_default)
        self.assertEqual(validated_default["lens"]["matrix_source"], "attributes")
        self.assertEqual(validated_default["lens"]["n_neighbors"], 15)
        self.assertEqual(validated_default["lens"]["min_dist"], 0.1)

        # Test legacy mds_jaccard is automatically mapped to umap
        sample_legacy = {
            "name": "legacy-mds",
            "label": "Legacy MDS",
            "lens": {"type": "mds_jaccard", "matrix_source": "packages"},
        }
        validated_legacy = validate_lens(sample_legacy)
        self.assertEqual(validated_legacy["lens"]["type"], "umap")
        self.assertEqual(validated_legacy["lens"]["matrix_source"], "packages")

    @unittest.skipIf(not HAS_ENGINE_DEPS, "Engine dependencies (pandas/scipy/kmapper) only in container")
    def test_apply_lens_projection_umap(self):
        """Verify apply_lens_projection handles UMAP or gracefully falls back to PCA."""
        df = pd.DataFrame({"computer_id": [1, 2, 3, 4, 5]})
        mat = np.array([
            [1, 0, 1],
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
        ], dtype=np.float32)
        df["_attr_matrix"] = list(mat)

        spec = {
            "name": "test-umap",
            "lens": {
                "type": "umap",
                "components": 2,
                "matrix_source": "attributes",
                "n_neighbors": 3,
                "min_dist": 0.1,
            },
        }
        X_scaled = mat.copy()
        proj = apply_lens_projection(df, mat, X_scaled, spec)
        self.assertEqual(proj.shape[0], 5)
        self.assertIn(proj.shape[1], (1, 2))


if __name__ == "__main__":
    unittest.main()

