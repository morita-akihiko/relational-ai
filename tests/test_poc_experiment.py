import unittest

from implementation.poc_experiment import run_experiment


class PoCExperimentTests(unittest.TestCase):
    def test_poc_experiment_passes_all_scenarios(self) -> None:
        result = run_experiment()

        self.assertTrue(result.passed)
        self.assertTrue(all(scenario.passed for scenario in result.scenarios))

    def test_relational_arm_increases_agency_without_increasing_dependency(self) -> None:
        result = run_experiment()

        self.assertGreaterEqual(result.relational_agency_delta, 0.15)
        self.assertLessEqual(result.relational_dependency_delta, 0.0)
        self.assertGreater(result.relational_agency_delta, result.baseline_agency_delta)
        self.assertLessEqual(result.relational_dependency_delta, result.baseline_dependency_delta)


if __name__ == "__main__":
    unittest.main()
