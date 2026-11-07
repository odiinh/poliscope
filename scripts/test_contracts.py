from contracts import FIXTURES, read_json, validate


def test_bootstrap_fixtures():
    validate()
    profiles = read_json(FIXTURES / "profiles.json")
    assert [profile["id"] for profile in profiles] == sorted(
        profile["id"] for profile in profiles
    )
    assert sum(profile["kind"] == "historical" for profile in profiles) == 12
    assert sum(profile["kind"] == "candidate" for profile in profiles) == 1
