# Pipelines

Every analysis follows the DataJoint `Params` → `Selection` → `Computed`
pattern: a lookup table of hyperparameters, a manual table pairing those
parameters with input data, and a computed table that does the work.

## Sleep

| Module                    | Tables                                                          |
| ------------------------- | --------------------------------------------------------------- |
| `sleep.sleep_table_dmr`   | `SleepScoringParams` → `SleepScoringSelection` → `SleepScoring` |
| `sleep.updown_tables_dmr` | `UpDownStateParams` → `UpDownStateSelection` → `UpDownStates`   |
| `sleep.pss_dmr`           | `PSSParams` → `PSSSelection` → `SleepPSS`                       |

`pss_dmr` also exposes the spectral-slope helpers directly. `fit_pss_from_psd`
returns `(pss, intercept, slope)` where `pss == -slope`, so that a **larger**
`pss` means a steeper 1/f falloff.

## Behavior

| Module                          | Tables                                                       |
| ------------------------------- | ------------------------------------------------------------ |
| `behavior.forktrack_tables_dmr` | `ForkTrackParams` → `ForkTrackSelection` → `ForkTrackEvents` |
| `behavior.wtrack_tables_dmr`    | `WTrackParams` → `WTrackSelection` → `WTrackEvents`          |

`behavior.FiltersEM` and `behavior.AS_EM_module` implement the Smith et al.
state-space EM estimate of a learning curve. They define no tables and need no
database.

## GLM

| Module                            | Tables                                              |
| --------------------------------- | --------------------------------------------------- |
| `GLM.path_progression_tables_dmr` | `PathProgressSelection` → `PathProgress`            |
| `GLM.glm_tables_dmr`              | `GLMSelection` → `GLMStorage`                       |
| `GLM.GLMBasis`                    | `GLMBasisParams` → `GLMBasisSelection` → `GLMBasis` |

`GLMStorage` bins spiking, position, path progression, turns, and reward into 50
ms bins. `GLMBasis` then expands those covariates into `nemos` bases and stores
the design matrix.
