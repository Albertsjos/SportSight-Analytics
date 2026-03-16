import os
import csv
import random
import glob

# Delete old CSVs
for f in glob.glob("*.csv"):
    try:
        os.remove(f)
        print(f"Deleted {f}")
    except Exception as e:
        print(f"Error removing {f}: {e}")

teams = {
    "FC Barcelona": [
        "Marc-André ter Stegen", "Jules Koundé", "Ronald Araújo", "Andreas Christensen", "Alejandro Balde",
        "Frenkie de Jong", "Pedri", "Gavi",
        "Raphinha", "Robert Lewandowski", "Lamine Yamal"
    ],
    "Liverpool": [
        "Alisson Becker", "Trent Alexander-Arnold", "Virgil van Dijk", "Ibrahima Konaté", "Andrew Robertson",
        "Alexis Mac Allister", "Dominik Szoboszlai", "Ryan Gravenberch",
        "Mohamed Salah", "Darwin Núñez", "Luis Díaz"
    ],
    "Manchester City": [
        "Ederson", "Kyle Walker", "Rúben Dias", "John Stones", "Nathan Aké",
        "Rodri", "Kevin De Bruyne", "Bernardo Silva",
        "Phil Foden", "Erling Haaland", "Jack Grealish"
    ],
    "Real Madrid": [
        "Thibaut Courtois", "Dani Carvajal", "Éder Militão", "Antonio Rüdiger", "Ferland Mendy",
        "Aurélien Tchouaméni", "Toni Kroos", "Federico Valverde",
        "Jude Bellingham", "Rodrygo", "Vinícius Júnior"
    ]
}

# Generate 38 matchdays for each team
for team_name, players in teams.items():
    filename = f"{team_name.replace(' ', '_').lower()}_season.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["match", "player_name", "goals", "assists", "shots_on_target", "tackles"])
        
        for match_day in range(1, 39):
            opponent = f"Opponent {match_day}"
            for player in players:
                is_attacker = any(name in player for name in ["Lewandowski", "Raphinha", "Yamal", "Salah", "Núñez", "Díaz", "Haaland", "Foden", "Grealish", "Rodrygo", "Vinícius", "Bellingham"])
                is_mid = any(name in player for name in ["de Jong", "Pedri", "Gavi", "Mac Allister", "Szoboszlai", "Gravenberch", "Rodri", "De Bruyne", "Silva", "Tchouaméni", "Kroos", "Valverde"])
                
                if is_attacker:
                    goals = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
                    assists = random.choices([0, 1, 2], weights=[50, 35, 15])[0]
                    shots = goals + random.randint(1, 4)
                    tackles = random.randint(0, 2)
                elif is_mid:
                    goals = random.choices([0, 1, 2], weights=[80, 15, 5])[0]
                    assists = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
                    shots = goals + random.randint(0, 3)
                    tackles = random.randint(2, 6)
                else: # defender / gk
                    goals = random.choices([0, 1], weights=[95, 5])[0]
                    assists = random.choices([0, 1], weights=[85, 15])[0]
                    shots = goals + random.randint(0, 2)
                    tackles = random.randint(3, 8)
                
                # Make GK stats
                if player in ["Marc-André ter Stegen", "Alisson Becker", "Ederson", "Thibaut Courtois"]:
                    goals = 0
                    assists = 0
                    shots = 0
                    tackles = random.randint(0, 1)

                writer.writerow([opponent, player, goals, assists, shots, tackles])
    
    print(f"Generated {filename}")

print("Done.")
