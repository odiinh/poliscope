from pipeline.ingest.fetch_platforms import to_text


def test_to_text_keeps_body_drops_chrome():
    html = (
        "<nav><a href='/issues/tax'>Tax</a></nav><script>x=1</script>"
        "<h2>Taxes</h2><p>Cut   the\nrate.</p><li>Fund schools</li>"
    )
    lines, links = to_text(html)
    assert lines == ["Taxes", "Cut the rate.", "Fund schools"]
    assert links == ["/issues/tax"]
