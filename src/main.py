"""Orquesta el pipeline completo: guion -> imágenes -> audio -> vídeo -> subida.
Uso: python src/main.py [--no-upload] [--tema "..."]
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

from guion_gen import generar_guion
from image_gen import generar_imagen
from tts_gen import generar_audio
from render import renderizar_escena, concatenar_escenas

TEMAS_POR_DEFECTO = [
    "el fallo de ingeniería del rodamiento IMS en Porsche",
    "por qué los motores diésel de camión pueden entrar en retroalimentación o runaway",
    "el peligro mortal del fenómeno shimmy o death wobble en motos",
    "el peor error de diseño del Ford Pinto y su depósito explosivo",
    "cómo funciona el freno de motor Jake Brake en los camiones pesados",
    "el motivo por el que se prohibieron los motores de 2 tiempos en MotoGP",
    "por qué nunca debes apagar de golpe un motor turbo tras exigirle potencia",
    "el desastre de las correas de distribución bañadas en aceite PureTech",
    "la razón técnica por la que los camiones tienen tantas marchas",
    "el fallo catastrófico del cambio DSG de 7 velocidades en seco",
    "por qué el embrague en seco de las Ducati suena a roto",
    "qué le ocurre a tu motor si te equivocas de marcha y haces un money shift",
    "el secreto de los turbos de geometría variable y por qué se atascan",
    "por qué los motores rotativos Wankel de Mazda consumen tanto aceite",
    "el peligro de los frenos de aire en camiones cuando pierden presión",
    "la verdad oculta detrás de la válvula EGR y la carbonilla en el motor",
    "por qué los frenos cerámicos chirrían tanto a baja velocidad",
    "el fallo de diseño que hacía volcar al Mercedes Clase A original",
    "cómo funciona el cambio Quickshifter en motos sin usar embrague",
    "por qué los camiones usan llantas con tantas tuercas y flechas indicadoras",
    "el colapso de los motores V8 Northstar de Cadillac por los tornillos de culata",
    "qué es la hidrolimpieza o hydro-locking y cómo un charco dobla bielas",
    "por qué las motos de cross modernas requieren cambiar pistón por horas de uso",
    "el peligro oculto de la regeneración del filtro de partículas DPF/FAP",
    "el motor indestructible Mercedes OM617 que superaba el millón de kilómetros",
]

def ejecutar(tema: str, subir: bool) -> None:
    print(f"Generando guion sobre: {tema}")
    guion = generar_guion(tema)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        rutas_escenas = []

        for i, escena in enumerate(guion["escenas"]):
            imagen = tmp / f"img_{i}.png"
            audio = tmp / f"audio_{i}.mp3"
            clip = tmp / f"clip_{i}.mp4"

            if not generar_imagen(escena["prompt_imagen"], str(imagen)):
                print(f"No se pudo generar la imagen de la escena {i}, se aborta este vídeo.")
                sys.exit(1)

            generar_audio(escena["texto"], str(audio))
            renderizar_escena(str(imagen), str(audio), str(clip))
            rutas_escenas.append(str(clip))

        salida_final = tmp / "short_final.mp4"
        concatenar_escenas(rutas_escenas, str(salida_final))

        if subir:
            from upload_youtube import subir_short
            url = subir_short(str(salida_final), guion["titulo"], guion["descripcion"])
            print(f"Publicado: {url}")
        else:
            destino_local = Path("preview.mp4")
            destino_local.write_bytes(salida_final.read_bytes())
            print(f"Modo prueba: vídeo guardado en {destino_local.resolve()}, no se sube.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tema", default=None)
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()

    import random
    tema = args.tema or random.choice(TEMAS_POR_DEFECTO)
    ejecutar(tema, subir=not args.no_upload)
