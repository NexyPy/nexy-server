from benchlib import load, report, scenarios, stacks
from run import cpu_count

OHA_REPORT = {
    "summary": {"successRate": 1.0, "requestsPerSec": 12345.6},
    "latencyPercentiles": {"p50": 0.0021, "p99": 0.0105},
    "statusCodeDistribution": {"200": 1000, "500": 2},
    "errorDistribution": {"connection closed": 3},
}

ROW = {
    "stack": "nexy",
    "scenario": "json",
    "rps": 12345.6,
    "p50_ms": 2.1,
    "p99_ms": 10.5,
    "statuses": {"200": 1000, "500": 2},
    "failures": 3,
    "success": 1.0,
    "rss_idle_mib": 80.2,
    "rss_peak_mib": 95.7,
}


def test_parse_reads_requests_per_second():
    assert load.parse(OHA_REPORT).rps == 12345.6


def test_parse_converts_latency_to_milliseconds():
    assert round(load.parse(OHA_REPORT).p99_ms, 3) == 10.5


def test_parse_counts_failed_requests():
    assert load.parse(OHA_REPORT).failures == 3


def test_error_count_adds_non_2xx_and_failures():
    assert report.error_count(ROW) == 5


def test_markdown_line_formats_thousands():
    assert "| 12,346 |" in report.line(ROW)


def test_cpu_count_reads_a_range():
    assert cpu_count("0-3") == 4


def test_cpu_count_reads_a_list():
    assert cpu_count("0,2,4-5") == 4


def test_oha_argv_sends_the_body_of_a_post(monkeypatch):
    monkeypatch.setattr(load, "oha_binary", lambda: "oha")
    validate = scenarios.by_name(["validate"])[0]
    assert "-d" in load.oha_argv("http://x/items", validate, 5, 8)


def test_nexy_serves_static_files_under_public():
    nexy = stacks.by_name(["nexy"])[0]
    assert nexy.path("static", "/static/asset.txt") == "/public/asset.txt"


def test_nexy_builds_before_it_starts():
    assert stacks.by_name(["nexy"])[0].prepare()[-1] == "build"


def test_unknown_scenario_is_refused():
    try:
        scenarios.by_name(["nope"])
    except ValueError:
        return
    raise AssertionError("an unknown scenario was accepted")


def test_requests_cut_at_the_deadline_are_not_failures():
    assert load.failures({"aborted due to deadline": 14}) == 0


def test_median_run_keeps_the_middle_run(monkeypatch):
    import types

    import run

    values = iter([300.0, 100.0, 200.0])
    monkeypatch.setattr(
        run.load, "run", lambda argv, client: load.Measure(next(values), 0, 0, 1, {}, 0)
    )
    monkeypatch.setattr(run.time, "sleep", lambda seconds: None)
    args = types.SimpleNamespace(repeat=3, pause=0)
    assert run.median_run([], [], args).rps == 200.0
