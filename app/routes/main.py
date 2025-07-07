from flask import Blueprint, render_template, current_app

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    datos = current_app.config["DATOS_GLOBALES"]
    return render_template(
        "index.html",
        clientes_count=len(datos["clientes"]),
        vehiculos_count=len(datos["vehiculos"]),
    )


@main_bp.route("/gestionar_vehiculos")
def gestionar_vehiculos():
    datos = current_app.config["DATOS_GLOBALES"]
    return render_template("gestionar_vehiculos.html", vehiculos=datos["vehiculos"])


@main_bp.route("/gestionar_clientes")
def gestionar_clientes():
    datos = current_app.config["DATOS_GLOBALES"]
    return render_template("gestionar_clientes.html", clientes=datos["clientes"])


@main_bp.route("/resultados")
def resultados():
    datos = current_app.config["DATOS_GLOBALES"]
    return render_template("resultados.html", resultados=datos.get("resultados"))


@main_bp.route("/diagnostico")
def diagnostico():
    return render_template("diagnostico.html")


@main_bp.route("/mapa-simple")
def mapa_simple():
    return render_template("mapa_simple.html")
