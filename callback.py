import os
from dotenv import find_dotenv, load_dotenv
from flask import Flask, Response, render_template, request

load_dotenv(find_dotenv())

from util import spotify

print("Starting Server")

app = Flask(__name__)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    code = request.args.get("code")

    if code is None:
        return Response(
            "Servidor a funcionar perfeitamente!",
            status=200,
        )

    token_info = spotify.generate_token(code)

    if "access_token" not in token_info:
        error = token_info.get("error", "unknown")
        desc = token_info.get("error_description", "")
        return Response(f"Token exchange failed: {error} - {desc}", status=400)

    access_token = token_info["access_token"]
    refresh_token = token_info.get("refresh_token", "Não disponível")

    profile_resp = spotify.get_user_profile_raw(access_token)
    if profile_resp.status_code != 200 or not profile_resp.text.strip():
        return Response(
            f"Spotify profile fetch failed: HTTP {profile_resp.status_code} - {profile_resp.text[:300]}",
            status=502,
        )

    spotify_user = profile_resp.json()
    user_id = spotify_user.get("id", "Desconhecido")

    return Response(
        f"<h2>Autenticação bem-sucedida para o utilizador: {user_id}</h2>"
        f"<p><b>O teu Refresh Token:</b></p>"
        f"<textarea style='width:100%;height:100px;'>{refresh_token}</textarea>",
        status=200,
        content_type="text/html; charset=utf-8",
    )


if __name__ == "__main__":
    app.run(debug=True)
