from flask import Flask, render_template, request, redirect, url_for, flash
from services.sistema_hospitalar import SistemaHospitalar

app = Flask(__name__)
app.secret_key = "chave_secreta_hospital"

# Instancia o sistema hospitalar global
sistema = SistemaHospitalar()

@app.route("/")
def index():
    # Calcula de forma segura os totais para exibir nos KPIs da Visão Geral
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

@app.route("/pacientes", methods=["GET", "POST"])
def pacientes():
    if request.method == "POST":
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        idade = request.form.get("idade")
        observacoes = request.form.get("observacoes")
        
        # Conexão real com a classe do sistema para cadastrar e salvar
        try:
            if hasattr(sistema, 'cadastrar_paciente'):
                sistema.cadastrar_paciente(nome, cpf, idade, observacoes)
            elif hasattr(sistema, 'adicionar_paciente'):
                sistema.adicionar_paciente(nome, cpf, idade, observacoes)
            else:
                # Caso a classe utilize um modelo direto
                from models.paciente import Paciente
                novo_paciente = Paciente(nome=nome, cpf=cpf, idade=idade, observacoes=observacoes)
                sistema.pacientes.append(novo_paciente)
            
            flash("Paciente cadastrado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao cadastrar paciente: {str(e)}", "danger")
            
        return redirect(url_for("pacientes"))
    
    # Busca a lista real de pacientes salvos
    pacientes_lista = sistema.pacientes if hasattr(sistema, 'pacientes') else []
    return render_template("pacientes.html", pacientes=pacientes_lista)

@app.route("/medicos", methods=["GET", "POST"])
def medicos():
    if request.method == "POST":
        nome = request.form.get("nome")
        crm = request.form.get("crm")
        especialidade = request.form.get("especialidade")
        
        # Conexão real com a classe do sistema para cadastrar médico
        try:
            if hasattr(sistema, 'cadastrar_medico'):
                sistema.cadastrar_medico(nome, crm, especialidade)
            else:
                from models.medico import Medico
                novo_medico = Medico(nome=nome, crm=crm, especialidade=especialidade)
                sistema.medicos.append(novo_medico)
                
            flash("Médico registrado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao registrar médico: {str(e)}", "danger")
            
        return redirect(url_for("medicos"))
        
    # Busca a lista real de médicos cadastrados
    medicos_lista = sistema.medicos if hasattr(sistema, 'medicos') else []
    return render_template("medicos.html", medicos=medicos_lista)

@app.route("/exames", methods=["GET", "POST"])
def exames():
    if request.method == "POST":
        nome_exame = request.form.get("nome_exame")
        cpf_paciente = request.form.get("cpf_paciente")
        
        try:
            if hasattr(sistema, 'agendar_exame'):
                sistema.agendar_exame(nome_exame, cpf_paciente)
            else:
                from models.exame import Exame
                novo_exame = Exame(nome=nome_exame, paciente=cpf_paciente)
                sistema.exames.append(novo_exame)
                
            flash("Exame solicitado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao solicitar exame: {str(e)}", "danger")
            
        return redirect(url_for("exames"))
        
    exames_lista = sistema.exames if hasattr(sistema, 'exames') else []
    return render_template("exames.html", exames=exames_lista)

@app.route("/ajuda", methods=["GET", "POST"])
def ajuda():
    if request.method == "POST":
        descricao = request.form.get("descricao")
        try:
            if hasattr(sistema, 'registrar_ajuda'):
                sistema.registrar_ajuda(descricao)
            else:
                from models.registro_ajuda import RegistroAjuda
                novo_reg = RegistroAjuda(descricao=descricao)
                sistema.registros_ajuda.append(novo_reg)
                
            flash("Atendimento registrado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao registrar atendimento: {str(e)}", "danger")
            
        return redirect(url_for("ajuda"))
        
    registros = sistema.registros_ajuda if hasattr(sistema, 'registros_ajuda') else []
    return render_template("ajuda.html", registros=registros)

@app.route("/busca")
def busca():
    termo = request.args.get("q", "")
    return render_template("busca.html", termo=termo)

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("erro.html", erro="Página não encontrada"), 404

if __name__ == "__main__":
    app.run(debug=True)