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
from engine.sql_builder import (
    build_sql_errors,
    build_sql_faults,
    build_sql_sync,
    build_sql_all_attributes,
)


class TestTdaEngine(unittest.TestCase):
    def test_builtin_lenses_loaded(self):
        """Verify that all 6 default built-in lenses are loaded from JSON."""
        names = {l["name"] for l in BUILTIN_LENSES}
        expected = {"health", "obsolescence", "software", "migration", "sync", "diversity"}
        self.assertTrue(expected.issubset(names), f"Missing lenses in {names}")

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


if __name__ == "__main__":
    unittest.main()
