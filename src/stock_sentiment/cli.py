"""Command-line entry point.

    stock-sentiment run --tickers AAPL,TSLA
    stock-sentiment serve --port 8000
"""
from __future__ import annotations

import argparse
import json
import sys

from stock_sentiment.logging_config import configure_logging, get_logger

logger = get_logger(__name__)


def _cmd_run(args: argparse.Namespace) -> int:
    from stock_sentiment.pipeline import run_pipeline

    tickers = args.tickers.split(",") if args.tickers else None
    report = run_pipeline(tickers=tickers, news_path=args.news_path)
    print(json.dumps(report.as_dict(), indent=2, default=str))
    return 0 if report.succeeded else 1


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("stock_sentiment.api.main:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stock-sentiment")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run the batch ingest/analysis pipeline")
    run_p.add_argument("--tickers", help="Comma-separated ticker list (default: config defaults)")
    run_p.add_argument("--news-path", help="Path to a news CSV (default: config path, or synthetic sample)")
    run_p.set_defaults(func=_cmd_run)

    serve_p = sub.add_parser("serve", help="Run the FastAPI server")
    serve_p.add_argument("--host", default="0.0.0.0")
    serve_p.add_argument("--port", type=int, default=8000)
    serve_p.add_argument("--reload", action="store_true")
    serve_p.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
