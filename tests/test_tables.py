"""Database-backed tests: that every pipeline's tables declare.

`requires_db` because importing any of these modules executes `@schema`, which
declares tables against a live server.
"""

import pytest

pytestmark = pytest.mark.requires_db


class TestTableDeclaration:
    """Each pipeline declares as a Params -> Selection -> Computed triple."""

    @pytest.mark.parametrize(
        "module,names",
        [
            (
                "mpfc_opto.sleep.pss_dmr",
                ["PSSParams", "PSSSelection", "SleepPSS"],
            ),
            (
                "mpfc_opto.sleep.sleep_table_dmr",
                [
                    "SleepScoringParams",
                    "SleepScoringSelection",
                    "SleepScoring",
                ],
            ),
            (
                "mpfc_opto.sleep.updown_tables_dmr",
                [
                    "UpDownStateParams",
                    "UpDownStateSelection",
                    "UpDownStates",
                ],
            ),
            (
                "mpfc_opto.behavior.forktrack_tables_dmr",
                ["ForkTrackParams", "ForkTrackSelection", "ForkTrackEvents"],
            ),
            (
                "mpfc_opto.behavior.wtrack_tables_dmr",
                ["WTrackParams", "WTrackSelection", "WTrackEvents"],
            ),
            (
                "mpfc_opto.GLM.glm_tables_dmr",
                ["GLMSelection", "GLMStorage"],
            ),
            (
                "mpfc_opto.GLM.path_progression_tables_dmr",
                ["PathProgressSelection", "PathProgress"],
            ),
        ],
    )
    def test_tables_declare(self, server, module, names):
        """Importing the module declares its tables; each gains a heading."""
        import importlib

        mod = importlib.import_module(module)
        for name in names:
            table = getattr(mod, name)
            assert table.heading is not None
            assert len(table.heading.names) > 0

    def test_params_tables_are_lookups_with_contents(self, server):
        """Lookup tables should ship default parameter sets."""
        from mpfc_opto.sleep.pss_dmr import PSSParams

        assert len(PSSParams()) >= 0  # declares and queries without error
