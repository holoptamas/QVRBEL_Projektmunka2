import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private apiUrl = 'http://localhost:5000/'

  constructor(private http: HttpClient) {}

  getPrediction(): Observable<Prediction> {
    return this.http.get<Prediction>(`${this.apiUrl}/prediction`)
  }

  getMatchData(): Observable<MatchData> {
    return this.http.get<MatchData>(`${this.apiUrl}/match-data`)
  }

  getDashboard(): Observable<Dashboard> {
  return this.http.get<any>(`${this.apiUrl}/dashboard`).pipe(
    map(data => new Dashboard(data))
  )
}
}

export class Prediction {
  blueWinProbability: number;
  redWinProbability: number;
  confidence: number;
  predictedWinner: string;
  status: string;
  message?: string;

  constructor(data: any) {
    this.blueWinProbability = data.blue_win_probability;
    this.redWinProbability = data.red_win_probability;
    this.confidence = data.confidence;
    this.predictedWinner = data.predicted_winner;
    this.status = data.status;
    this.message = data.message;
  }
}

export class PlayerData {
  playerName: string;
  role: string;
  championId: number;
  championName: string;
  goldSpent: number;
  level: number;
  kills: number;
  deaths: number;
  assists: number;
  creepScore: number;
  wardScore: number;

  constructor(data: any) {
    this.playerName = data.player_name;
    this.role = data.role;
    this.championId = data.champion_id;
    this.championName = data.champion_name;
    this.goldSpent = data.gold_spent;
    this.level = data.level;
    this.kills = data.kills;
    this.deaths = data.deaths;
    this.assists = data.assists;
    this.creepScore = data.creep_score;
    this.wardScore = data.ward_score;
  }
}  

export class TeamData {
  teamKills: number;
  teamGoldSpent: number;
  towersTaken: number;
  inhibitorsTaken: number;
  dragonsTaken: number;
  grubsTaken: number;
  riftheraldTaken: number;
  baronTaken: number;
  players: PlayerData[];

  constructor(data: any) {
    this.teamKills = data.team_kills;
    this.teamGoldSpent = data.team_gold_spent;
    this.towersTaken = data.towers_taken;
    this.inhibitorsTaken = data.inhibitors_taken;
    this.dragonsTaken = data.dragons_taken;
    this.grubsTaken = data.grubs_taken;
    this.riftheraldTaken = data.riftherald_taken;
    this.baronTaken = data.baron_taken;
    this.players = data.players.map((p: any) => new PlayerData(p));
  }
}

export class MatchData{
  status: string 
  message?: string 
  game_duration: number
  game_minute: string
  game_seconds: number
  blue_team: TeamData 
  red_team: TeamData

  constructor(data:any){
    this.status = data.status
    this.message = data.message
    this.game_duration = data.game_duration
    this.game_minute = (this.game_duration / 60).toFixed(0)
    this.game_seconds = this.game_duration % 60
    this.blue_team = new TeamData(data.blue_team)
    this.red_team = new TeamData(data.red_team)
  }
}

export class Dashboard {
  prediction: Prediction;
  matchData: MatchData;

  constructor(data: any) {
    this.prediction = new Prediction(data.prediction);
    this.matchData = new MatchData(data.match_data);
  }
}