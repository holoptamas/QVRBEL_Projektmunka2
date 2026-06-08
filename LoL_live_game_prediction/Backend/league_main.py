from flask import Flask, send_from_directory
from flask_cors import CORS
from pathlib import Path

from LoL_live_game_prediction.Backend.league_api_controller import LeagueApiController
from LoL_live_game_prediction.Backend.prediction_service import PredictionService
from LoL_live_game_prediction.Backend.league_gameclient_api_handler import GameClientApiDataRetriever


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR.parent / "League_Neural_Networks" / "league_model.pth"
TRAIN_CSV_PATH = BASE_DIR.parent / "League_Match_Data" / "DS_2026_06_02_20_00_train.csv"

FRONTEND_DIST_PATH = (BASE_DIR.parent.parent/"AngularCode"/ "LoL_prediction"/ "dist"/ "LoL_prediction"/ "browser")

app = Flask(__name__,static_folder=str(FRONTEND_DIST_PATH),static_url_path="")

CORS(app)

game_client = GameClientApiDataRetriever()

prediction_service = PredictionService(game_client=game_client, model_path=MODEL_PATH, train_csv_path=TRAIN_CSV_PATH)

prediction_service.start_prediction_loop()

api_controller = LeagueApiController(prediction_service)
api_controller.register_routes(app)


@app.route("/")
def serve_angular_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_angular_files(path):
    file_path = FRONTEND_DIST_PATH / path

    if file_path.exists():
        return send_from_directory(app.static_folder, path)

    return send_from_directory(app.static_folder, "index.html")


# py -m LoL_live_game_prediction.Backend.league_main
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )