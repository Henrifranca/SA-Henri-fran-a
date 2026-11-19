class Paciente:
    def __init__(self, id_paciente, nome, idade, sintoma, nivel, medico_responsavel=None):
        self.id = id_paciente
        self.nome = nome
        self.idade = idade
        self.sintoma = sintoma
        self.nivel = int(nivel)
        self.medico_responsavel = medico_responsavel
