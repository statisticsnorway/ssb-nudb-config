from nudb_config import settings


def test_content_settings_after_merge_from_tomls() -> None:
    combo_settings = settings.merge_tomls("/tests/external_tomls_samples")

    # variables.toml
    assert "fullfort_gk" in combo_settings.variables
    assert combo_settings.variables.fullfort_gk.length == [2]
    
    # datasets.toml
    assert "inr" in combo_settings.datasets.igang.variables
    assert "ftype" == combo_settings.datasets.igang.dataset_specific_renames.ftype
    assert 8.0 == combo_settings.datasets.igang.thresholds_empty.snr

    # paths.toml
    assert "/buckets/delt-utdanning/nudb-data/klargjorte-data/" == combo_settings.paths.local_daplalab.delt_utdanning

    # check existing fields from main config in combined settings
    assert "fnr"  in combo_settings.variables
    assert 11 in combo_settings.variables.fnr.length
    assert "avslutta" in combo_settings.datasets
    assert "/ssb/stamme03/nudbut/nyeste" == combo_settings.paths.on_prem.delt_utdanning

    # check if removal worked
    assert "snr_mrk" not in combo_settings.variables