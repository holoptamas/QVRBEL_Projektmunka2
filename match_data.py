class PlayerData:
    def __init__(self, role: str, champ_id: int, champ_name: str, gold_spent: int, level: int, kills: int, deaths: int, assists: int, creepscore: int, wardscore: int):  
        self.champ_id: int = champ_id
        self.champ_name: str = champ_name        
        self.gold_spent: int = gold_spent
        self.level: int = level
        self.kills: int = kills
        self.deaths: int = deaths
        self.assists: int = assists
        self.creepscore: int = creepscore
        self.wardscore: int = wardscore

        self.role: str
        if role == "UTILITY":
            self.role = "SUPPORT"
        else:
            self.role = role
        
class TeamData:
    def __init__(self, players: list[PlayerData], win: int, towers_taken: int, inhibitors_taken: int, dragons_taken: int, grubs_taken: int, riftherald_taken: int, baron_taken: int):
        self.players: list[PlayerData] = players
        self.win:int = win
        self.towers_taken: int = towers_taken
        self.inhibitors_taken: int = inhibitors_taken
        self.dragons_taken: int = dragons_taken
        self.grubs_taken: int = grubs_taken
        self.riftherald_taken: int = riftherald_taken
        self.baron_taken: int = baron_taken

        self.team_kills = 0
        for player in self.players:
            self.team_kills += player.kills
        
        self.team_gold_spent = 0
        for player in self.players:
            self.team_gold_spent += player.gold_spent
        
class MatchData:
    def __init__(self, game_version:str, game_duration: int, blue_team: TeamData, red_team: TeamData):
        game_version_tmp = game_version.split(".")[0:2]
        self.game_version = game_version_tmp[0] + "." + game_version_tmp[1]
        self.game_duration = game_duration
        self.blue_team: TeamData = blue_team
        self.red_team: TeamData = red_team

class GameClientPlayerData:
    def __init__(self, player_name:str, role: str, champ_id: int, champ_name: str, gold_spent: int, level: int, kills: int, deaths: int, assists: int, creepscore: int, wardscore: int):  
        self.player_name:str = player_name
        self.champ_id: int = champ_id
        self.champ_name: str = champ_name        
        self.gold_spent: int = gold_spent
        self.level: int = level
        self.kills: int = kills
        self.deaths: int = deaths
        self.assists: int = assists
        self.creepscore: int = creepscore
        self.wardscore: int = wardscore

        self.role: str
        if role == "UTILITY":
            self.role = "SUPPORT"
        #for debugging remove later
        elif role == "NONE":
            self.role = "MIDDLE"
        else:
            self.role = role 
        
        
class GameClientTeamData:
    def __init__(self, players: list[GameClientPlayerData], towers_taken: int, inhibitors_taken: int, dragons_taken: int, grubs_taken: int, riftherald_taken: int, atakhan_taken: int, baron_taken: int, feats: int):
        self.players: list[GameClientPlayerData] = players
        self.towers_taken: int = towers_taken
        self.inhibitors_taken: int = inhibitors_taken
        self.dragons_taken: int = dragons_taken
        self.grubs_taken: int = grubs_taken
        self.riftherald_taken: int = riftherald_taken
        self.atakhan_taken: int = atakhan_taken
        self.baron_taken: int = baron_taken
        self.feats: int = feats

        #feats and atakhan are temporary

        self.team_kills = 0
        for player in self.players:
            self.team_kills += player.kills
        
        self.team_gold_spent = 0
        for player in self.players:
            self.team_gold_spent += player.gold_spent
        
class GameClientMatchData:
    def __init__(self, game_duration: int, blue_team: GameClientTeamData, red_team: GameClientTeamData):
        self.game_duration = game_duration
        self.blue_team: GameClientTeamData = blue_team
        self.red_team: GameClientTeamData = red_team