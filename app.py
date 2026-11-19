from flask import Flask, render_template, request, redirect, url_for, flash, session
from services.sistema_hospitalar import SistemaHospitalar

# Inicia a aplicação e prepara o Flask para controlar as páginas do sistema.
app = Flask(__name__)

# Essa chave permite que o Flask mantenha as informações da sessão do usuário.
app.secret_key = "chave_secreta_hospital_segura"

# Cria o acesso ao sistema hospitalar, onde ficam reunidos os dados e cadastros.
sistema = SistemaHospitalar()


# ==========================================
# LOGIN E LOGOUT
# ==========================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        perfil = request.form.get("perfil")

        session['usuario'] = usuario
        session['perfil'] = perfil

        flash(f"Acesso liberado! Perfil ativo: {perfil.capitalize()}.", "success")

        if perfil == 'paciente':
            return redirect(url_for("exames"))

        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada com segurança.", "success")
    return redirect(url_for("login"))


# ==========================================
# VISÃO GERAL
# ==========================================

@app.route("/visao-geral")
def index():
    if 'perfil' not in session:
        return redirect(url_for('login'))

    if session.get('perfil') == 'paciente':
        return redirect(url_for('exames'))

    try:
        total_pacientes = len(sistema.pacientes) if hasattr(sistema, 'pacientes') else 0
        total_medicos = len(sistema.medicos) if hasattr(sistema, 'medicos') else 0
        total_exames = len(sistema.exames) if hasattr(sistema, 'exames') else 0
        total_ajuda = len(sistema.registros_ajuda) if hasattr(sistema, 'registros_ajuda') else 0
    except Exception:
        total_pacientes = total_medicos = total_exames = total_ajuda = 0

    return render_template(
        "index.html",
        total_pacientes=total_pacientes,
        total_medicos=total_medicos,
        total_exames=total_exames,
        total_ajuda=total_ajuda
    )


# ==========================================
# PACIENTES
# ==========================================

@app.route("/pacientes", methods=["GET", "POST"])
def pacientes():
    if 'perfil' not in session:
        return redirect(url_for('login'))

    perfil = session.get('perfil')

    if perfil == 'paciente':
        flash("Acesso negado. Você só pode visualizar seus próprios exames.", "danger")
        return redirect(url_for('exames'))

    if request.method == "POST":
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        idade = request.form.get("idade")
        doenca = request.form.get("doenca") if perfil == 'medico' else "Aguardando avaliação médica"

        try:
            if hasattr(sistema, 'cadastrar_paciente'):
                sistema.cadastrar_paciente(nome, cpf, idade, doenca)
            else:
                from models.paciente import Paciente
                novo = Paciente(nome=nome, cpf=cpf, idade=idade, observacoes=doenca)
                sistema.pacientes.append(novo)

            flash("Paciente registrado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao salvar: {str(e)}", "danger")

        return redirect(url_for("pacientes"))

    pacientes_lista = sistema.pacientes if hasattr(sistema, 'pacientes') else []
    return render_template("pacientes.html", pacientes=pacientes_lista, perfil=perfil)


# ==========================================
# ÁREA MÉDICA
# ==========================================

@app.route("/medicos", methods=["GET", "POST"])
def medicos():
    if 'perfil' not in session:
        return redirect(url_for('login'))

    if session.get('perfil') != 'medico':
        flash("Área restrita exclusivamente ao corpo médico.", "danger")
        return redirect(url_for('index'))

    if request.method == "POST":
        nome = request.form.get("nome")
        crm = request.form.get("crm")
        especialidade = request.form.get("especialidade")

        try:
            if hasattr(sistema, 'cadastrar_medico'):
                sistema.cadastrar_medico(nome, crm, especialidade)
            else:
                from models.medico import Medico
                novo = Medico(nome=nome, crm=crm, especialidade=especialidade)
                sistema.medicos.append(novo)

            flash("Médico cadastrado!", "success")
        except Exception as e:
            flash(f"Erro: {str(e)}", "danger")

        return redirect(url_for("medicos"))

    medicos_lista = sistema.medicos if hasattr(sistema, 'medicos') else []
    return render_template("medicos.html", medicos=medicos_lista)


# ==========================================
# EXAMES
# ==========================================

@app.route("/exames", methods=["GET", "POST"])
def exames():
    if 'perfil' not in session:
        return redirect(url_for('login'))

    perfil = session.get('perfil')
    usuario_logado = session.get('usuario', '').strip()

    if request.method == "POST":
        if perfil == 'paciente':
            flash("Pacientes não têm permissão para solicitar exames.", "danger")
            return redirect(url_for('exames'))

        nome_exame = request.form.get("nome_exame")
        cpf_paciente = request.form.get("cpf_paciente", "").strip()

        try:
            if hasattr(sistema, 'agendar_exame'):
                sistema.agendar_exame(nome_exame, cpf_paciente)
            else:
                from models.exame import Exame
                novo = Exame(nome=nome_exame, paciente=cpf_paciente)
                sistema.exames.append(novo)

            flash("Exame solicitado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro: {str(e)}", "danger")

        return redirect(url_for("exames"))

    todos_exames = sistema.exames if hasattr(sistema, 'exames') else []

    if perfil == 'paciente':
        exames_filtrados = []
        for e in todos_exames:
            pac_ref = e.get('paciente') if isinstance(e, dict) else getattr(e, 'paciente', '')
            if str(pac_ref).strip() == usuario_logado:
                exames_filtrados.append(e)
        exames_lista = exames_filtrados
    else:
        exames_lista = todos_exames

    return render_template("exames.html", exames=exames_lista, perfil=perfil)


# ==========================================
# TRIAGEM E AJUDA (Com Tela de Bloqueio 403)
# ==========================================

@app.route("/ajuda")
def ajuda():
    if 'perfil' not in session:
        return redirect(url_for('login'))
        
    # Se o perfil for paciente, exibe a tela de bloqueio personalizada
    if session.get('perfil') == 'paciente':
        return render_template("bloqueio.html"), 403
        
    registros = sistema.registros_ajuda if hasattr(sistema, 'registros_ajuda') else []
    return render_template("ajuda.html", registros=registros)


# ==========================================
# BUSCA
# ==========================================

@app.route("/busca")
def busca():
    if 'perfil' not in session or session.get('perfil') == 'paciente':
        return redirect(url_for('login'))

    termo = request.args.get("q", "")
    return render_template("busca.html", termo=termo)


# Tratamento de erro 404
@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("erro.html", erro="Página não encontrada"), 404


if __name__ == "__main__":
    app.run(debug=True)