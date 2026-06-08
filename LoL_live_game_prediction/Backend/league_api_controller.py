from flask import jsonify


class LeagueApiController:
    def __init__(self, prediction_service):
        self.prediction_service = prediction_service

    def register_routes(self, app):

        @app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "running"})

        @app.route("/prediction", methods=["GET"])
        def prediction():
            return jsonify(self.prediction_service.get_latest_prediction())
        
        @app.route("/match-data", methods=["GET"])
        def match_data():
            return jsonify(self.prediction_service.get_latest_game_state())
        
        @app.route("/dashboard", methods=["GET"])
        def dashboard():
            return jsonify({
                "prediction": self.prediction_service.get_latest_prediction(),
                "match_data": self.prediction_service.get_latest_game_state()
            })