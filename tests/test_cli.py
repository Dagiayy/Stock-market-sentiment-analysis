from __future__ import annotations

import json

import pytest

from stock_sentiment import cli


def test_build_parser_run_defaults():
    parser = cli.build_parser()
    args = parser.parse_args(["run", "--tickers", "AAPL,TSLA"])
    assert args.command == "run"
    assert args.tickers == "AAPL,TSLA"


def test_build_parser_serve_defaults():
    parser = cli.build_parser()
    args = parser.parse_args(["serve"])
    assert args.host == "0.0.0.0"
    assert args.port == 8000


def test_main_run_invokes_pipeline_and_prints_report(monkeypatch, capsys):
    class FakeReport:
        succeeded = True

        def as_dict(self):
            return {"succeeded": True}

    def fake_run_pipeline(tickers=None, news_path=None):
        assert tickers == ["AAPL"]
        return FakeReport()

    monkeypatch.setattr("stock_sentiment.pipeline.run_pipeline", fake_run_pipeline)

    exit_code = cli.main(["run", "--tickers", "AAPL"])

    assert exit_code == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["succeeded"] is True


def test_main_run_returns_nonzero_on_failure(monkeypatch, capsys):
    class FakeReport:
        succeeded = False

        def as_dict(self):
            return {"succeeded": False, "error": "boom"}

    monkeypatch.setattr("stock_sentiment.pipeline.run_pipeline", lambda **kwargs: FakeReport())

    exit_code = cli.main(["run"])
    assert exit_code == 1


def test_main_requires_a_subcommand():
    with pytest.raises(SystemExit):
        cli.main([])
