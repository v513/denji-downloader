from flask import Flask, request, render_template, send_file
import yt_dlp
import os
import webbrowser
import multiprocessing
import time
from pathlib import Path

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    carpeta_descargas = str(Path.home() / "Downloads")

    if request.method == "POST":
        url = request.form["url"]
        tipo = request.form["tipo"]

        if tipo == "video":
            resolucion = request.form["resolucion"]
            try:
                if resolucion.endswith("p"):
                    height = int(resolucion.replace("p", ""))
                elif "x" in resolucion:
                    width, height = resolucion.lower().split("x")
                    height = int(height)
                else:
                    height = int(resolucion)
            except:
                return "❌ Resolución personalizada inválida."

            ydl_opts = {
                'format': f"bestvideo[height<={height}]+bestaudio/best",
                'outtmpl': os.path.join(carpeta_descargas, f'%(title)s_{height}p.%(ext)s'),
                'merge_output_format': 'mp4'
            }

        elif tipo == "audio":
            formato = request.form["formato_audio"]
            if formato not in ["mp3", "wav", "ogg"]:
                return "❌ Formato de audio no válido."

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(carpeta_descargas, f'%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': formato,
                    'preferredquality': '192',
                }]
            }

        else:
            return "❌ Tipo no válido."

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            archivo_final = ydl.prepare_filename(info)

        if tipo == "audio":
            archivo_final = archivo_final.rsplit(".", 1)[0] + f".{formato}"

        return send_file(archivo_final, as_attachment=True)

    return render_template("index.html")


# 🔁 Esta función debe ir antes de usarse en iniciar_app()
def abrir_navegador():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")


def iniciar_app():
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg_bin")
    os.environ["PATH"] += os.pathsep + ffmpeg_dir

    multiprocessing.Process(target=abrir_navegador).start()
    app.run(debug=False)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    iniciar_app()
