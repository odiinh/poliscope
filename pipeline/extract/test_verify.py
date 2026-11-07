from pipeline.extract.verify import verify_dims

SOURCE = "We will  cut the income tax\nto 4 percent — starting now. Schools matter."


def test_verify_dims():
    dims = {
        "tax": {
            "stance": 0.8,
            "salience": 1,
            "confidence": 1,
            "evidence": [
                "cut the income tax to 4 percent - starting now.",
                "We will raise taxes.",
            ],
        },
        "education": {
            "stance": -0.5,
            "salience": 0.5,
            "confidence": 0.5,
            "evidence": ["Schools are great."],
        },
        "health": {"stance": None, "salience": 0, "confidence": 0, "evidence": []},
    }
    out, kept, given = verify_dims(dims, SOURCE)
    assert (kept, given) == (1, 3)
    assert out["tax"]["evidence"] == ["cut the income tax to 4 percent - starting now."]
    assert out["education"] == {
        "stance": None,
        "salience": 0.0,
        "confidence": 0.0,
        "evidence": [],
    }
    assert out["health"]["stance"] is None
