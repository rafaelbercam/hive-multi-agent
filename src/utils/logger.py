import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class WorkerMetrics:
    name: str
    start_time: float
    end_time: Optional[float] = None
    tokens_used: int = 0
    status: str = "pending"
    error: Optional[str] = None

    @property
    def duration(self) -> float:
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

class HiveLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"hive_session_{self.session_id}.jsonl"
        self.metrics: Dict[str, WorkerMetrics] = {}
        self.queen_decisions: list = []

    def log_queen_decision(self, query: str, decomposition: list[str]):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "queen_decision",
            "query": query,
            "decomposition": decomposition,
        }
        self.queen_decisions.append(entry)
        self._write_log(entry)

    def start_worker(self, worker_name: str):
        self.metrics[worker_name] = WorkerMetrics(
            name=worker_name,
            start_time=time.time(),
        )

    def end_worker(self, worker_name: str, tokens: int = 0, status: str = "success", error: Optional[str] = None):
        if worker_name in self.metrics:
            self.metrics[worker_name].end_time = time.time()
            self.metrics[worker_name].tokens_used = tokens
            self.metrics[worker_name].status = status
            self.metrics[worker_name].error = error

            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "worker_complete",
                "worker": worker_name,
                "duration": self.metrics[worker_name].duration,
                "tokens": tokens,
                "status": status,
            }
            if error:
                entry["error"] = error
            self._write_log(entry)

    def log_final_aggregation(self, result: str, total_tokens: int):
        result_str = str(result) if result else "N/A"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "final_result",
            "total_tokens": total_tokens,
            "result_preview": result_str[:200],
        }
        self._write_log(entry)

    def _write_log(self, entry: Dict[str, Any]):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_metrics(self) -> Dict[str, Any]:
        total_duration = 0
        total_tokens = 0
        worker_stats = {}

        for name, metric in self.metrics.items():
            total_duration = max(total_duration, metric.duration)
            total_tokens += metric.tokens_used
            worker_stats[name] = {
                "duration": metric.duration,
                "tokens": metric.tokens_used,
                "status": metric.status,
            }

        return {
            "session_id": self.session_id,
            "total_duration": total_duration,
            "total_tokens": total_tokens,
            "workers": worker_stats,
            "log_file": str(self.log_file),
        }

    def print_summary(self):
        metrics = self.get_metrics()
        print("\n" + "="*70)
        print("HIVE EXECUTION SUMMARY")
        print("="*70)
        print(f"Session ID: {metrics['session_id']}")
        print(f"Total Duration: {metrics['total_duration']:.2f}s")
        print(f"Total Tokens: {metrics['total_tokens']}")
        print("\nWorker Breakdown:")
        for worker, stats in metrics['workers'].items():
            print(f"  {worker:15} - {stats['duration']:6.2f}s | {stats['tokens']:5} tokens | {stats['status']}")
        print(f"\nLog file: {metrics['log_file']}")
        print("="*70 + "\n")
