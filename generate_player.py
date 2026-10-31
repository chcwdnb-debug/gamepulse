import random
from datetime import date, timedelta

def generate_players(n_players,start_date, n_days):
    players = []

    for i in range(n_players):
        
        player_id=f"P{i+1:06d}"
        signup_date = start_date +timedelta(days=random.randint(0, n_days-1))
        region1= random.choices(["US", "EU","APAC","LATAM"], weights=[0.4, 0.3,0.2,0.1])[0] 
        platform1 = random.choices(["PC", "PS5","Xbox"], weights=[0.45, 0.3,0.25])[0] 
        is_payer = random.random() <0.05
        p = {"region": region1, "platform": platform1,"player_id":player_id,"signup_date":signup_date ,"is_payer": is_payer}
        players.append(p)
        
    return players


if __name__ == "__main__":    
    players = generate_players(1000, date(2026, 9, 1), 30)
    print(players[:3])        
    print(len(players))
     
    assert len(players) == 1000

  
    ids = [p["player_id"] for p in players]
    assert len(set(ids)) == len(ids)

   
   
    days =[p["signup_date"]for p in players]
    assert min(days)>=date(2026,9,1)
    assert max(days)<=date(2026,9,30)
   

   
    regions =[p["region"]for p in players] 
    assert set(regions) == {"US", "EU", "APAC", "LATAM"}


   
    platforms=[p["platform"]for p in players]
    assert set(platforms)=={"PC", "PS5","Xbox"}
     

    print("All checks passed")