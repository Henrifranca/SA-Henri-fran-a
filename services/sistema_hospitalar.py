import json
from pathlib import Path
from models.paciente import Paciente
from models.medico import Medico
from models.exame import Exame
from models.registro_ajuda import RegistroAjuda

class SistemaHospitalar:
    def __init__(self, arquivo_dados=None):
        self.arquivo_dados = Path(arquivo_dados) if arquivo_dados else Path(__file__).resolve().parent.parent / "sistema_hospitalar.json"
        self.pacientes = []
        self.medicos = []
        self.exames = []
        self.historico_ajuda = []
        self.contador_id_paciente = 1
        self.contador_id_medico = 1
        self.contador_id_exame = 1
        self.guia_doencas = {
            "gripe": "Informação educativa: repouso e hidratação podem ajudar. Procure avaliação profissional se necessário.",
            "fratura": "Suspeita de fratura precisa de avaliação presencial por profissional de saúde.",
            "infecção": "O tratamento depende da causa e deve ser definido por profissional de saúde.",
            "enxaqueca": "Procure orientação profissional para avaliar sintomas e opções de cuidado.",
            "alergia": "Evite o possível agente e procure orientação profissional, especialmente se houver reação importante."
        }
        self.orientacoes_ajuda = {
            1: "Intensidade leve informada. Se quiser, converse com alguém de confiança.",
            2: "Intensidade moderada-baixa informada. Uma pausa e uma conversa com alguém de confiança podem ajudar.",
            3: "Intensidade moderada informada. Considere procurar apoio de alguém de confiança ou de um profissional.",
            4: "Intensidade alta informada. Procure apoio de um profissional de saúde ou de alguém de confiança.",
            5: "Você informou intensidade muito alta. Procure ajuda presencial imediata de um serviço de saúde ou emergência."
        }
        self.carregar_dados()

    def salvar_dados(self):
        dados = {
            "contador_id_paciente": self.contador_id_paciente,
            "contador_id_medico": self.contador_id_medico,
            "contador_id_exame": self.contador_id_exame,
            "medicos": [{"id": m.id, "nome": m.nome, "especialidade": m.especialidade} for m in self.medicos],
            "pacientes": [{
                "id": p.id, "nome": p.nome, "idade": p.idade, "sintoma": p.sintoma,
                "nivel": p.nivel, "medico_id": p.medico_responsavel.id if p.medico_responsavel else None
            } for p in self.pacientes],
            "exames": [{
                "id": e.id, "paciente_id": e.paciente.id, "medico_id": e.medico.id,
                "nome_exame": e.nome_exame, "resultado": e.resultado
            } for e in self.exames],
            "historico_ajuda": [{"relato": h.relato, "nivel_risco": h.nivel_risco} for h in self.historico_ajuda]
        }
        self.arquivo_dados.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.arquivo_dados.with_suffix(".tmp")
        temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=4), encoding="utf-8")
        temporario.replace(self.arquivo_dados)

    def carregar_dados(self):
        if not self.arquivo_dados.exists():
            return
        try:
            dados = json.loads(self.arquivo_dados.read_text(encoding="utf-8"))
            self.contador_id_paciente = dados.get("contador_id_paciente", 1)
            self.contador_id_medico = dados.get("contador_id_medico", 1)
            self.contador_id_exame = dados.get("contador_id_exame", 1)
            self.medicos = [Medico(m["id"], m["nome"], m["especialidade"]) for m in dados.get("medicos", [])]
            mapa_medicos = {m.id: m for m in self.medicos}
            self.pacientes = [
                Paciente(p["id"], p["nome"], p.get("idade", ""), p.get("sintoma", ""),
                         p.get("nivel", 1), mapa_medicos.get(p.get("medico_id")))
                for p in dados.get("pacientes", [])
            ]
            mapa_pacientes = {p.id: p for p in self.pacientes}
            self.exames = []
            for e in dados.get("exames", []):
                paciente, medico = mapa_pacientes.get(e.get("paciente_id")), mapa_medicos.get(e.get("medico_id"))
                if paciente and medico:
                    self.exames.append(Exame(e["id"], paciente, medico, e["nome_exame"], e.get("resultado", "")))
            self.historico_ajuda = [RegistroAjuda(h.get("relato", ""), h.get("nivel_risco", 1)) for h in dados.get("historico_ajuda", [])]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as erro:
            raise RuntimeError(f"Não foi possível ler {self.arquivo_dados.name}: {erro}") from erro

    @staticmethod
    def _texto(valor, campo):
        valor = str(valor or "").strip()
        if not valor:
            raise ValueError(f"Preencha o campo: {campo}.")
        return valor

    def cadastrar_paciente(self, nome, idade, sintoma, nivel, medico_id=None):
        nome = self._texto(nome, "nome do paciente")
        idade = self._texto(idade, "idade")
        sintoma = self._texto(sintoma, "sintoma/doença")
        try:
            idade_num = int(idade)
            nivel_num = int(nivel)
        except (TypeError, ValueError):
            raise ValueError("Idade e gravidade devem ser números inteiros.")
        if idade_num < 0 or not 1 <= nivel_num <= 5:
            raise ValueError("Informe idade válida e gravidade entre 1 e 5.")
        medico = self.obter_medico(medico_id) if medico_id else None
        paciente = Paciente(self.contador_id_paciente, nome, idade_num, sintoma, nivel_num, medico)
        self.pacientes.append(paciente)
        self.contador_id_paciente += 1
        self.salvar_dados()
        return paciente

    def cadastrar_medico(self, nome, especialidade):
        nome = self._texto(nome, "nome do médico")
        especialidade = self._texto(especialidade, "especialidade")
        medico = Medico(self.contador_id_medico, nome, especialidade)
        self.medicos.append(medico)
        self.contador_id_medico += 1
        self.salvar_dados()
        return medico

    def obter_paciente(self, paciente_id):
        try:
            paciente_id = int(paciente_id)
        except (TypeError, ValueError):
            raise ValueError("Selecione um paciente válido.")
        paciente = next((p for p in self.pacientes if p.id == paciente_id), None)
        if not paciente:
            raise ValueError("Paciente não encontrado.")
        return paciente

    def obter_medico(self, medico_id):
        try:
            medico_id = int(medico_id)
        except (TypeError, ValueError):
            raise ValueError("Selecione um médico válido.")
        medico = next((m for m in self.medicos if m.id == medico_id), None)
        if not medico:
            raise ValueError("Médico não encontrado.")
        return medico

    def cadastrar_exame(self, paciente_id, medico_id, nome_exame, resultado):
        paciente = self.obter_paciente(paciente_id)
        medico = self.obter_medico(medico_id)
        nome_exame = self._texto(nome_exame, "nome do exame")
        resultado = str(resultado or "").strip()
        exame = Exame(self.contador_id_exame, paciente, medico, nome_exame, resultado)
        self.exames.append(exame)
        self.contador_id_exame += 1
        self.salvar_dados()
        return exame

    def vincular_medico(self, paciente_id, medico_id):
        paciente = self.obter_paciente(paciente_id)
        medico = self.obter_medico(medico_id)
        paciente.medico_responsavel = medico
        self.salvar_dados()

    def dar_alta(self, paciente_id):
        paciente = self.obter_paciente(paciente_id)
        self.pacientes.remove(paciente)
        self.exames = [e for e in self.exames if e.paciente.id != paciente.id]
        self.salvar_dados()
        return paciente

    def buscar(self, termo, tipo="paciente"):
        termo = (termo or "").strip().casefold()
        if tipo == "medico":
            return [m for m in self.medicos if termo in m.especialidade.casefold() or termo in m.nome.casefold()]
        return [p for p in self.pacientes if termo in p.nome.casefold()]

    def fila_prioridade(self):
        return sorted(self.pacientes, key=lambda p: (p.nivel, -p.id), reverse=True)

    def registrar_ajuda(self, relato, nivel_risco):
        relato = self._texto(relato, "relato")
        try:
            nivel = int(nivel_risco)
        except (TypeError, ValueError):
            raise ValueError("Escolha uma intensidade entre 1 e 5.")
        if not 1 <= nivel <= 5:
            raise ValueError("A intensidade deve estar entre 1 e 5.")
        registro = RegistroAjuda(relato, nivel)
        self.historico_ajuda.append(registro)
        self.salvar_dados()
        return registro, self.orientacoes_ajuda[nivel]

    def estatisticas(self):
        return {
            "pacientes": len(self.pacientes),
            "medicos": len(self.medicos),
            "exames": len(self.exames),
            "ajuda": len(self.historico_ajuda),
            "gravidade": {n: sum(1 for p in self.pacientes if p.nivel == n) for n in range(1, 6)}
        }
