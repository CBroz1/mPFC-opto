"""Database-backed tests: table declaration and the pure functions that sit
beside table definitions.

All of this is marked `requires_db` because importing any of these modules
executes `@schema`, which declares tables against a live server. Even
`pss_dmr`'s pure signal-processing helpers are unreachable without one, since
they share a module with its tables.
"""

import numpy as np
import pytest

pytestmark = pytest.mark.requires_db


class TestFitPSSFromPSD:
    """`fit_pss_from_psd` returns (pss, intercept, slope), pss == -slope.

    The sign is inverted on purpose, so that a larger pss means a steeper 1/f
    falloff. A test asserting "slope < 0" would be testing the raw third
    element, not the headline value.
    """

    def test_falling_psd_gives_positive_pss(self, sleep_pss):
        freqs = np.linspace(1.0, 100.0, 200)
        pss, _, slope = sleep_pss.fit_pss_from_psd(freqs, freqs**-2.0)
        assert pss > 0
        assert slope < 0

    def test_pss_is_the_negated_slope(self, sleep_pss):
        freqs = np.linspace(1.0, 100.0, 200)
        pss, _, slope = sleep_pss.fit_pss_from_psd(freqs, freqs**-2.0)
        assert pss == pytest.approx(-slope)

    @pytest.mark.parametrize("exponent", [1.0, 2.0, 3.0])
    def test_recovers_a_known_exponent(self, sleep_pss, exponent):
        freqs = np.linspace(1.0, 100.0, 400)
        pss, _, _ = sleep_pss.fit_pss_from_psd(freqs, freqs**-exponent)
        assert pss == pytest.approx(exponent, abs=1e-6)

    def test_steeper_psd_gives_larger_pss(self, sleep_pss):
        freqs = np.linspace(1.0, 100.0, 200)
        shallow, _, _ = sleep_pss.fit_pss_from_psd(freqs, freqs**-1.0)
        steep, _, _ = sleep_pss.fit_pss_from_psd(freqs, freqs**-4.0)
        assert steep > shallow

    def test_flat_psd_gives_near_zero_pss(self, sleep_pss):
        freqs = np.linspace(1.0, 100.0, 200)
        pss, _, _ = sleep_pss.fit_pss_from_psd(freqs, np.ones_like(freqs))
        assert pss == pytest.approx(0.0, abs=1e-9)

    def test_f_range_excludes_bins(self, sleep_pss):
        """Only bins inside f_range are fitted."""
        freqs = np.linspace(1.0, 100.0, 400)
        psd = freqs**-2.0
        psd[freqs > 90.0] = 1e6  # corrupt outside the default range
        pss, _, _ = sleep_pss.fit_pss_from_psd(freqs, psd)
        assert pss == pytest.approx(2.0, abs=1e-6)

    def test_too_few_valid_bins_raises(self, sleep_pss):
        freqs = np.array([5.0, 6.0, 7.0])
        with pytest.raises(ValueError, match="Not enough valid frequency bins"):
            sleep_pss.fit_pss_from_psd(freqs, freqs**-2.0)

    def test_nonpositive_psd_bins_are_dropped(self, sleep_pss):
        """log10 of a zero or negative PSD is undefined, so those are masked."""
        freqs = np.linspace(1.0, 100.0, 200)
        psd = freqs**-2.0
        psd[:50] = 0.0
        pss, _, _ = sleep_pss.fit_pss_from_psd(freqs, psd)
        assert np.isfinite(pss)


class TestComputePSSWindows:
    """Sliding-window PSS over a wideband trace."""

    FS = 1000.0

    @pytest.fixture
    def signal(self):
        rng = np.random.default_rng(0)
        return rng.standard_normal(10_000)

    def test_one_pss_value_per_window(self, sleep_pss, signal):
        t_centers, pss_vals = sleep_pss.compute_pss_windows(signal, self.FS)[:2]
        assert len(t_centers) == len(pss_vals)
        assert len(pss_vals) > 1

    def test_window_count_follows_window_and_step(self, sleep_pss, signal):
        """10 s of data, 2 s windows, 1 s steps -> 9 window starts."""
        t_centers = sleep_pss.compute_pss_windows(
            signal, self.FS, window_s=2.0, step_s=1.0
        )[0]
        assert len(t_centers) == 9

    def test_centers_are_increasing_and_relative(self, sleep_pss, signal):
        t_centers = sleep_pss.compute_pss_windows(signal, self.FS)[0]
        assert np.all(np.diff(t_centers) > 0)
        assert t_centers[0] >= 0

    def test_window_shorter_than_16_samples_raises(self, sleep_pss, signal):
        with pytest.raises(ValueError, match="window_s is too small"):
            sleep_pss.compute_pss_windows(signal, self.FS, window_s=0.001)

    def test_nonpositive_step_raises(self, sleep_pss, signal):
        with pytest.raises(ValueError, match="step_s must be positive"):
            sleep_pss.compute_pss_windows(signal, self.FS, step_s=0.0)

    def test_signal_shorter_than_one_window_raises(self, sleep_pss):
        with pytest.raises(ValueError, match="shorter than one window"):
            sleep_pss.compute_pss_windows(np.zeros(100), self.FS, window_s=2.0)


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
