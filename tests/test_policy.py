from __future__ import annotations

import unittest

from gateway.policy import FIRST_WAVE_MODEL_NAMES, FIRST_WAVE_MODEL_SPECS


class LaunchModelPolicyTest(unittest.TestCase):
    def test_claude_fable_5_is_published_at_configured_price(self) -> None:
        self.assertIn("claude-fable-5", FIRST_WAVE_MODEL_NAMES)
        model = next(spec for spec in FIRST_WAVE_MODEL_SPECS if spec.model == "claude-fable-5")
        self.assertEqual(model.input_price, 8.0)
        self.assertEqual(model.output_price, 40.0)


if __name__ == "__main__":
    unittest.main()
