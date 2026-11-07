"""Brief C step 8: run every model stage, validate against contracts/schemas, write data/public/.

The only writer of data/public/. On fixture inputs it builds and validates but writes nothing.
"""

import shutil

from jsonschema import Draft7Validator

from pipeline.model import backtest, forecasts, outcomes, pca_map
from pipeline.model.common import (
    BUILD,
    EXTRACT,
    INGEST,
    PUBLIC,
    ROOT,
    load_profiles,
    log,
    read_json,
    write_build,
)


def main():
    shutil.rmtree(BUILD, ignore_errors=True)
    profiles, real_profiles = load_profiles()
    write_build("profiles", profiles)
    if (EXTRACT / "reliability.json").exists():
        write_build("reliability", read_json(EXTRACT / "reliability.json"))
    for stage in (outcomes, forecasts, backtest, pca_map):
        stage.main()
    # no cohort qualified: drop it so the app keeps the fixture
    if not read_json(BUILD / "signal.json"):
        (BUILD / "signal.json").unlink()

    for path in sorted(BUILD.glob("*.json")):
        schema = read_json(ROOT / "contracts/schemas" / f"{path.stem}.schema.json")
        Draft7Validator(schema).validate(read_json(path))
    log.info("validated %s", ", ".join(p.name for p in sorted(BUILD.glob("*.json"))))

    real = real_profiles and (INGEST / "panel.csv").exists()
    if not real:
        log.warning("fixture inputs: data/public/ left unchanged")
        return
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for stale in PUBLIC.glob("*.json"):
        stale.unlink()
    for path in BUILD.glob("*.json"):
        shutil.copyfile(path, PUBLIC / path.name)
    log.info("wrote data/public/")


if __name__ == "__main__":
    main()
