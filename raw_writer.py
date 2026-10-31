import json
import os
import random
from collections import defaultdict
from datetime import date

from generate_player import generate_players
from sessions import generate_events


def write_raw(events, out_dir="data/raw"):
    os.makedirs(out_dir, exist_ok=True)          # 文件夹不存在就创建

    # 按事件发生的日期分组：{date(2026,9,1): [事件, 事件, ...], ...}
    by_day = defaultdict(list)                   # ≈ map<date, vector<event>>，key 不存在时自动建空 list
    for e in events:
        by_day[e["timestamp"].date()].append(e)  # datetime.date() 取出日期部分

    for day, day_events in sorted(by_day.items()):
        path = os.path.join(out_dir, f"events_{day}.jsonl")
        with open(path, "w", encoding="utf-8") as f:   # with ≈ RAII，出了代码块自动关文件
            for e in day_events:
                row = dict(e)                                  # 复制一份，不改原数据
                row["timestamp"] = e["timestamp"].isoformat()  # datetime → "2026-09-01T18:40:00"
                f.write(json.dumps(row) + "\n")
    print(f"wrote {len(events)} events into {len(by_day)} files")


if __name__ == "__main__":
    random.seed(42)
    players = generate_players(1000, date(2026, 9, 1), 30)
    events = generate_events(players, date(2026, 9, 1), 30)
    write_raw(events)