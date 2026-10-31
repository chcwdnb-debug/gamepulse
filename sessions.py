import random
from datetime import date, datetime, timedelta
from generate_player import generate_players


def make_event(player, event_type, ts):
    return {
        "player_id": player["player_id"],
        "event_type": event_type,
        "timestamp": ts,
        "platform": player["platform"],
        "region": player["region"],
        "game_version": player["game_version"],
    }


def is_active(days_since_signup):
    # TODO: 第 0 天返回 True
      
    if  days_since_signup==0:
        return True
    else:
        return random.random() < 0.4/days_since_signup ** 0.5 
        
    # TODO: 其他天以 0.4 / days_since_signup ** 0.5 的概率返回 True
   

def generate_session(player, day):
    events = []
    # TODO: login 时间 = day 当天 00:00 + 随机 480~1380 分钟（即 8:00~23:00）
    login = datetime(day.year,day.month,day.day) +timedelta(minutes=random.randint(480,1380))
    # TODO: 加 login 事件（用 make_event）
    events.append(make_event(player,"login",login))
    
    # TODO: 随机 1~5 场比赛，每场：

    for i in range(random.randint(1,5)):
    #         start = 上一个事件的时间 + 1~5 分钟   （提示：events[-1]["timestamp"]）
        match_start=events[-1]["timestamp"]+timedelta(minutes= random.randint(1,5))
    #         end   = start + 10~25 分钟
        match_end = match_start+timedelta(minutes=random.randint(10,25))

    #         加 match_start、match_end
        events.append(make_event(player,"match_start",match_start))
        events.append(make_event(player,"match_end",match_end))

    # TODO: logout = 最后一个事件 + 1~5 分钟
    logout = events[-1]["timestamp"] + timedelta(minutes=random.randint(1,5))
    events.append(make_event(player,"logout",logout))
    return events


def generate_events(players, start_date, n_days):
    end_date = start_date + timedelta(days=n_days - 1)
    all_events = []
    for player in players:
        # TODO: 对 signup_date 到 end_date 之间的每一天：
        #         如果 is_active(距离注册的天数)：
        #             session = generate_session(player, 当天)
        #             如果是第 0 天：先加 signup 事件（时间 = session[0]["timestamp"] 减 1 分钟）
        #             再把 session 加进 all_events
        for d in range((end_date -player["signup_date"]).days + 1):
            day= player["signup_date"] + timedelta(days=d)
            if is_active((day-player["signup_date"]).days): 
                session = generate_session(player, day)
                if day==player["signup_date"]:
                    all_events.append(make_event(player,"signup",session[0]["timestamp"] -timedelta(minutes=1)))
                all_events.extend(session)

    return all_events


if __name__ == "__main__":
    random.seed(42)    # ≈ srand(42)，让每次运行结果一样，方便 debug
    players = generate_players(1000, date(2026, 9, 1), 30)
    events = generate_events(players, date(2026, 9, 1), 30)
    for e in events[:10]:
        print(e)
    print(len(events))
    print(max(e["timestamp"] for e in events))