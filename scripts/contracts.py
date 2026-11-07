"""Validate each public file and sync the app's inputs."""

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
PUBLIC = ROOT / "data/public"
FIXTURES = CONTRACTS / "fixtures"
GENERATED = ROOT / "app/src/generated"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    from jsonschema import Draft7Validator

    schemas = CONTRACTS / "schemas"
    for fixture in sorted(FIXTURES.glob("*.json")):
        schema = read_json(schemas / f"{fixture.stem}.schema.json")
        Draft7Validator.check_schema(schema)
        validator = Draft7Validator(schema)
        validator.validate(read_json(fixture))
        public = PUBLIC / fixture.name
        if public.exists():
            validator.validate(read_json(public))


def sync():
    GENERATED.mkdir(parents=True, exist_ok=True)
    sources = {"dimensions.json": CONTRACTS / "dimensions.json"}
    for fixture in sorted(FIXTURES.glob("*.json")):
        public = PUBLIC / fixture.name
        sources[fixture.name] = public if public.is_file() else fixture
    prompt = CONTRACTS / "prompt/extract_v1.md"
    if prompt.is_file():
        sources[prompt.name] = prompt
    else:
        (GENERATED / prompt.name).unlink(missing_ok=True)
    for name, source in sources.items():
        shutil.copyfile(source, GENERATED / name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync", action="store_true")
    if parser.parse_args().sync:
        sync()
    else:
        validate()
