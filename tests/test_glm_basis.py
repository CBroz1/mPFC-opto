"""Tests for the basis-construction helpers in `GLMBasis`.

`requires_db` even though every function here is pure: they share a module with
`@schema` tables, so importing it opens a DataJoint connection. Extracting them
into a table-free module would make these runnable without a server.

Also skipped when `jax` is unimportable; see the `glm_basis` fixture.
"""

import numpy as np
import pytest

pytestmark = pytest.mark.requires_db


class TestWrapTo2Pi:
    def test_maps_into_zero_to_two_pi(self, glm_basis):
        x = np.array([-3 * np.pi, -0.1, 0.0, 1.0, 7.0, 100.0])
        out = glm_basis._wrap_to_2pi(x)
        assert np.all(out >= 0)
        assert np.all(out < 2 * np.pi)

    def test_is_identity_inside_the_range(self, glm_basis):
        x = np.array([0.0, 1.0, 3.0, 6.0])
        assert glm_basis._wrap_to_2pi(x) == pytest.approx(x)

    def test_preserves_angle_modulo_two_pi(self, glm_basis):
        x = np.array([-1.0, 0.5, 8.0])
        out = glm_basis._wrap_to_2pi(x)
        assert np.cos(out) == pytest.approx(np.cos(x))
        assert np.sin(out) == pytest.approx(np.sin(x))


class TestNanToZero:
    def test_replaces_nan(self, glm_basis):
        out = np.asarray(glm_basis._nan_to_zero(np.array([1.0, np.nan, 3.0])))
        assert not np.any(np.isnan(out))
        assert out[1] == 0.0

    def test_leaves_finite_values_alone(self, glm_basis):
        x = np.array([[1.0, 2.0], [3.0, 4.0]])
        assert np.asarray(glm_basis._nan_to_zero(x)) == pytest.approx(x)

    def test_returns_a_jax_array(self, glm_basis):
        """Downstream code indexes the result with jax semantics."""
        out = glm_basis._nan_to_zero(np.array([1.0, 2.0]))
        assert type(out).__module__.startswith("jax")


class TestGetUnitColumns:
    def test_selects_only_unit_columns(self, glm_basis):
        import pandas as pd

        df = pd.DataFrame(
            {
                "time": [0.0, 0.05],
                "unit_0": [0, 1],
                "unit_11": [1, 0],
                "speed": [1.0, 2.0],
            }
        )
        assert glm_basis.get_unit_columns(df) == ["unit_0", "unit_11"]

    def test_returns_empty_when_there_are_no_units(self, glm_basis):
        import pandas as pd

        df = pd.DataFrame({"time": [0.0], "speed": [1.0]})
        assert glm_basis.get_unit_columns(df) == []
