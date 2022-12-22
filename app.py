from flask import Flask, jsonify, request
from db.connection import connection, cursor
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)


@app.route("/api/playlists", methods=["GET"])
def all_playlists():
    if request.method == "GET":
        cursor.execute("""
        SELECT playlists.playlist_id, playlists.name, playlists.description, playlists.location, playlists.cuisine, users.nickname, CAST(CAST(AVG(votes.vote_count) AS DECIMAL(10, 1)) AS VARCHAR(4)) AS vote_count FROM playlists
        LEFT JOIN votes
        ON playlists.playlist_id = votes.playlist_id 
        LEFT JOIN users
        ON playlists.owner_email = users.user_email
        GROUP BY playlists.playlist_id, users.nickname
        ORDER BY vote_count DESC;
        """)
        playlists = cursor.fetchall()
        results = json.dumps({"playlists": playlists})
        loaded_results = json.loads(results)
        return loaded_results


@app.route("/api/playlists/<playlist_id>", methods=["GET"])
def specific_playlist(playlist_id):
    try:
        int(playlist_id)
    except:
        return jsonify({"msg": "invalid playlist id"}), 400
    if request.method == "GET":
        cursor.execute(
            """
                SELECT
                    name,
                    place_id,
                    nickname AS owner_nickname,
                    location,
                    cuisine,
                    description,
                    playlists.playlist_id
                FROM playlists
                INNER JOIN restaurants
                ON playlists.playlist_id = restaurants.playlist_id
                INNER JOIN users
                ON owner_email = user_email
                WHERE playlists.playlist_id = %s;
            """,
            [playlist_id],
        )
    playlist = cursor.fetchall()
    results = json.dumps({"playlist": playlist})
    loaded_results = json.loads(results)
    # *** TO DO *** ensure that it's not possible to submit an empty playlist to the site, so that there will always be content to be displayed, so long as the playlist_id is valid
    if len(loaded_results["playlist"]) == 0:
        return jsonify({"msg": "playlist not found"}), 404
    else:
        return loaded_results
