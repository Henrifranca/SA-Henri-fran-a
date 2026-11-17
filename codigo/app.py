import os
import json
from time import sleep

# CLASSE: PACIENTE
# Representa as informações básicas de um paciente cadastrado.
class Paciente:
    def __init__(self, id_paciente, nome, idade, sintoma, nivel, medico_responsavel=None):
        self.id = id_paciente
        self.nome = nome
        self.idade = idade
        self.sintoma = sintoma
        self.nivel = nivel
        self.medico_responsavel = medico_responsavel  # Armazena o objeto Médico responsável

    def __str__(self):
        medico_nome = self.medico_responsavel.nome if self.medico_responsavel else "Não atribuído"
        return f"[ID: {self.id}] Nome: {self.nome} | Idade: {self.idade} | Sintoma: {self.sintoma} | Gravidade: {self.nivel} | Médico: {medico_nome}"

# CLASSE: MÉDICO
# Representa as informações de um médico cadastrado no hospital.
class Medico:
    def __init__(self, id_medico, nome, especialidade):
        self.id = id_medico
        self.nome = nome
        self.especialidade = especialidade

    def __str__(self):
        return f"[ID: {self.id}] Dr(a). {self.nome} | Especialidade: {self.especialidade}"

# CLASSE: EXAME
# Representa um exame médico solicitado/cadastrado para um paciente.
class Exame:
    def __init__(self, id_exame, paciente, medico, nome_exame, resultado):
        self.id = id_exame
        self.paciente = paciente
        self.medico = medico
        self.nome_exame = nome_exame
        self.resultado = resultado

    def __str__(self):
        return f"[Exame ID: {self.id}] Paciente: {self.paciente.nome} (ID: {self.paciente.id}) | Médico: Dr(a). {self.medico.nome} | Exame: {self.nome_exame} | Resultado: {self.resultado}"


# CLASSE: REGISTRO DE AJUDA
# Armazena os relatos e o nível deles.
class RegistroAjuda:
    """Representa uma autoavaliação feita pelo usuário."""
    def __init__(self, relato, nivel_risco):
        self.relato = relato
        self.nivel_risco = nivel_risco

    def __str__(self):
        return f"Relato: \"{self.relato}\" | Nível de Risco: {self.nivel_risco}/5"


# CLASSE PRINCIPAL: SISTEMA HOSPITALAR
# Gerencia listas e regras dos menus e interações do sistema.
class SistemaHospitalar:
    def __init__(self):
        # Listas para armazenar os dados em memória
        self.pacientes = []
        self.medicos = []
        self.exames = []           # Lista de exames cadastrados
        self.historico_ajuda = [] 
        
        # Contadores para gerar IDs únicos automaticamente
        self.contador_id_paciente = 1
        self.contador_id_medico = 1
        self.contador_id_exame = 1
        
        # Nome do arquivo JSON para persistência
        self.arquivo_dados = "sistema_hospitalar.json"
        
        # Guia de doenças médicas com tratamentos simulados de referência
        self.guia_doencas = {
            "gripe": "Repouso, hidratação e antitérmicos se houver febre.",
            "fratura": "Imobilização do membro, raio-X e avaliação ortopédica.",
            "infecção": "Uso de antibióticos prescritos após avaliação médica.",
            "enxaqueca": "Analgésicos, repouso em ambiente escuro e silencioso.",
            "alergia": "Uso de anti-histamínicos e afastamento do agente alérgico."
        }

        # Orientações para o sistema de autoajuda baseadas no risco de 1 a 5
        self.orientacoes_ajuda = {
            1: "Nível leve. Tente respirar fundo, beber uma água e fazer algo relaxante.",
            2: "Nível moderado-baixo. Considere conversar com alguém ou dar uma pausa.",
            3: "Nível moderado. Pode ser útil fazer uma caminhada.",
            4: "Nível alto. É importante buscar o apoio de um profissional.",
            5: "Nível crítico. Procure ajuda imediata de um serviço especializado."
        }

        # Carrega os dados salvos automaticamente ao iniciar
        self.carregar_dados()

    # Método para salvar todos os dados no arquivo JSON
    def salvar_dados(self):
        dados = {
            "contador_id_paciente": self.contador_id_paciente,
            "contador_id_medico": self.contador_id_medico,
            "contador_id_exame": self.contador_id_exame,
            "medicos": [{"id": m.id, "nome": m.nome, "especialidade": m.especialidade} for m in self.medicos],
            "pacientes": [
                {
                    "id": p.id,
                    "nome": p.nome,
                    "idade": p.idade,
                    "sintoma": p.sintoma,
                    "nivel": p.nivel,
                    "medico_id": p.medico_responsavel.id if p.medico_responsavel else None
                } for p in self.pacientes
            ],
            "exames": [
                {
                    "id": e.id,
                    "paciente_id": e.paciente.id,
                    "medico_id": e.medico.id,
                    "nome_exame": e.nome_exame,
                    "resultado": e.resultado
                } for e in self.exames
            ],
            "historico_ajuda": [{"relato": h.relato, "nivel_risco": h.nivel_risco} for h in self.historico_ajuda]
        }

        try:
            with open(self.arquivo_dados, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[ERRO] Não foi possível salvar os dados: {e}")
            sleep(2)

    # Método para carregar os dados do arquivo JSON
    def carregar_dados(self):
        if not os.path.exists(self.arquivo_dados):
            return

        try:
            with open(self.arquivo_dados, "r", encoding="utf-8") as f:
                dados = json.load(f)

            self.contador_id_paciente = dados.get("contador_id_paciente", 1)
            self.contador_id_medico = dados.get("contador_id_medico", 1)
            self.contador_id_exame = dados.get("contador_id_exame", 1)

            # Carrega médicos
            self.medicos = [Medico(m["id"], m["nome"], m["especialidade"]) for m in dados.get("medicos", [])]

            # Carrega pacientes e reconecta os objetos de médicos
            self.pacientes = []
            for p_data in dados.get("pacientes", []):
                medico_encontrado = None
                if p_data["medico_id"]:
                    medico_encontrado = next((m for m in self.medicos if m.id == p_data["medico_id"]), None)
                
                paciente = Paciente(
                    p_data["id"],
                    p_data["nome"],
                    p_data["idade"],
                    p_data["sintoma"],
                    p_data["nivel"],
                    medico_encontrado
                )
                self.pacientes.append(paciente)

            # Carrega exames e reconecta pacientes e médicos
            self.exames = []
            for e_data in dados.get("exames", []):
                paciente_encontrado = next((p for p in self.pacientes if p.id == e_data["paciente_id"]), None)
                medico_encontrado = next((m for m in self.medicos if m.id == e_data["medico_id"]), None)

                if paciente_encontrado and medico_encontrado:
                    exame = Exame(
                        e_data["id"],
                        paciente_encontrado,
                        medico_encontrado,
                        e_data["nome_exame"],
                        e_data["resultado"]
                    )
                    self.exames.append(exame)

            # Carrega histórico de ajuda
            self.historico_ajuda = [RegistroAjuda(h["relato"], h["nivel_risco"]) for h in dados.get("historico_ajuda", [])]

        except Exception as e:
            print(f"[ERRO] Não foi possível carregar os dados salvos: {e}")
            sleep(2)

    # Limpa o terminal
    def limpar_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    # Valida e garante que o usuário digite um número inteiro válido entre 1 e 5
    def obter_nivel_gravidade(self):
        while True:
            try:
                nivel = int(input("Nível da gravidade (1 a 5): "))
                if 1 <= nivel <= 5:
                    return nivel
                print("Número inválido! Digite um valor entre 1 e 5.")
                sleep(1.5)
            except ValueError:
                print("Entrada inválida! Digite apenas números inteiros.")
                sleep(1.5)

    # Coleta dados de um Paciente, vincula um médico (opcional) e o adiciona à lista
    def cadastrar_paciente(self):
        print("\n=== NOVO PACIENTE ===")
        nome = input("Nome do paciente: ")
        idade = input("Idade: ")
        sintoma = input("Sintoma/Doença principal: ")
        nivel = self.obter_nivel_gravidade()

        # Verificação e Vinculação de Médico Responsável no cadastro
        medico_escolhido = None
        if not self.medicos:
            print("\n[AVISO] Não há médicos disponíveis no momento. O paciente ficará sem médico vinculado.")
            sleep(2)
        else:
            print("\n--- SELECIONAR MÉDICO RESPONSÁVEL ---")
            print("0. Nenhum / Pular")
            for i, m in enumerate(self.medicos, 1):
                print(f"{i} - Dr(a). {m.nome} ({m.especialidade})")
            
            try:
                op_medico = int(input("Escolha o número do médico: "))
                if 1 <= op_medico <= len(self.medicos):
                    medico_escolhido = self.medicos[op_medico - 1]
                    print(f"-> Médico {medico_escolhido.nome} vinculado com sucesso!")
                    sleep(1.5)
                else:
                    print("Nenhum médico vinculado.")
                    sleep(1.5)
            except ValueError:
                print("Entrada inválida para médico. Seguindo sem médico vinculado.")
                sleep(1.5)

        # Cria o paciente utilizando o ID automático atual e incrementa o contador
        novo_paciente = Paciente(self.contador_id_paciente, nome, idade, sintoma, nivel, medico_escolhido)
        self.pacientes.append(novo_paciente)
        self.contador_id_paciente += 1

        # Salva automaticamente após cadastrar
        self.salvar_dados()

        print(f"\n-> Paciente '{nome}' cadastrado com sucesso! (ID: {novo_paciente.id})")
        
        # Verifica se o sintoma informado existe no dicionário de guia médico
        sintoma_minusculo = sintoma.lower()
        if sintoma_minusculo in self.guia_doencas:
            print(f"[GUIA MÉDICO] Tratamento sugerido: {self.guia_doencas[sintoma_minusculo]}")

        if nivel == 5:
            print("[ALERTA] Paciente em estado crítico! Encaminhar para emergência!")
        sleep(3)

    # Coleta dados de um Medico e o adiciona à lista
    def cadastrar_medico(self):
        print("\n=== NOVO MÉDICO ===")
        nome = input("Nome do médico: ")
        especialidade = input("Especialidade: ")

        # Cria o médico utilizando o ID automático atual e incrementa o contador
        novo_medico = Medico(self.contador_id_medico, nome, especialidade)
        self.medicos.append(novo_medico)
        self.contador_id_medico += 1

        # Salva automaticamente após cadastrar
        self.salvar_dados()

        print(f"-> Médico '{nome}' cadastrado com sucesso! (ID: {novo_medico.id})")
        sleep(2)

    # Cadastra um exame associando um médico e um paciente
    def cadastrar_exame(self):
        print("\n=== CADASTRAR EXAME ===")
        if not self.pacientes:
            print("Erro: Não há pacientes cadastrados para receber exames.")
            sleep(2)
            return
        if not self.medicos:
            print("Erro: Não há médicos cadastrados para solicitar exames.")
            sleep(2)
            return

        # Selecionar o médico solicitante
        print("Selecione o médico solicitante:")
        for i, m in enumerate(self.medicos, 1):
            print(f"{i} - Dr(a). {m.nome} ({m.especialidade})")
        
        try:
            op_medico = int(input("Número do médico: "))
            if not (1 <= op_medico <= len(self.medicos)):
                print("Médico inválido.")
                sleep(1.5)
                return
            medico_selecionado = self.medicos[op_medico - 1]
        except ValueError:
            print("Entrada inválida.")
            sleep(1.5)
            return

        # Selecionar o paciente
        print("\nSelecione o paciente:")
        for i, p in enumerate(self.pacientes, 1):
            print(f"{i} - {p.nome} (ID: {p.id})")
        
        try:
            op_paciente = int(input("Número do paciente: "))
            if not (1 <= op_paciente <= len(self.pacientes)):
                print("Paciente inválido.")
                sleep(1.5)
                return
            paciente_selecionado = self.pacientes[op_paciente - 1]
        except ValueError:
            print("Entrada inválida.")
            sleep(1.5)
            return

        nome_exame = input("\nNome/Tipo do Exame (ex: Raio-X, Hemograma): ")
        resultado = input("Resultado / Laudo preliminar: ")

        novo_exame = Exame(self.contador_id_exame, paciente_selecionado, medico_selecionado, nome_exame, resultado)
        self.exames.append(novo_exame)
        self.contador_id_exame += 1

        # Salva automaticamente após cadastrar o exame
        self.salvar_dados()

        print(f"\n-> Exame '{nome_exame}' cadastrado com sucesso para {paciente_selecionado.nome}! (ID do Exame: {novo_exame.id})")
        sleep(2.5)

    # Exibe a listagem de todos os pacientes cadastrados no sistema
    def listar_pacientes(self):
        print("\n=== LISTA DE PACIENTES ===")
        if not self.pacientes:
            print("Nenhum paciente cadastrado.")
        else:
            for i, p in enumerate(self.pacientes, 1):
                print(f"{i} - {p}")
        input("\nPressione ENTER para voltar ao menu...")

    # Exibe submenus para listar cadastro do medico ou consultar o guia de doenças
    def listar_medicos(self):
        print("\n=== LISTA DE MÉDICOS ===")
        print("1. Ver lista de médicos cadastrados")
        print("2. Consultar Guia de Doenças e Tratamentos")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            print("\n=== LISTA DE MÉDICOS ===")
            if not self.medicos:
                print("Nenhum médico cadastrado.")
            else:
                for i, m in enumerate(self.medicos, 1):
                    print(f"{i} - {m}")
        elif escolha == "2":
            print("\n=== GUIA DE DOENÇAS E TRATAMENTOS ===")
            for doenca, tratamento in self.guia_doencas.items():
                print(f"• {doenca.capitalize()}: {tratamento}")
        
        input("\nPressione ENTER para voltar ao menu...")

    # Permite visualizar os exames cadastrados
    def visualizar_exames(self):
        print("\n=== VISUALIZAR EXAMES ===")
        if not self.exames:
            print("Nenhum exame cadastrado no sistema.")
            input("\nPressione ENTER para voltar ao menu...")
            return

        print("1. Ver todos os exames")
        print("2. Filtrar exames por Paciente")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("\n--- TODOS OS EXAMES ---")
            for e in self.exames:
                print(e)
        elif opcao == "2":
            termo = input("Digite o nome do paciente (ou parte dele): ").lower()
            encontrados = [e for e in self.exames if termo in e.paciente.nome.lower()]
            
            print(f"\n--- EXAMES ENCONTRADOS ({len(encontrados)}) ---")
            if not encontrados:
                print("Nenhum exame encontrado para este paciente.")
            else:
                for e in encontrados:
                    print(e)
        else:
            print("Opção inválida.")

        input("\nPressione ENTER para voltar ao menu...")

    # Permite vincular ou alterar o médico de um paciente já cadastrado
    def vincular_medico_paciente(self):
        print("\n=== VINCULAR MÉDICO A PACIENTE ===")
        
        if not self.pacientes:
            print("Não há pacientes cadastrados no sistema.")
            sleep(2)
            return
        
        if not self.medicos:
            print("Não há médicos cadastrados no sistema para realizar o vínculo.")
            sleep(2)
            return

        print("Escolha o paciente que deseja atualizar:")
        for i, p in enumerate(self.pacientes, 1):
            medico_atual = p.medico_responsavel.nome if p.medico_responsavel else "Nenhum"
            print(f"{i} - {p.nome} (ID: {p.id} | Médico Atual: {medico_atual})")

        try:
            op_paciente = int(input("\nDigite o número do paciente: "))
            indice_paciente = op_paciente - 1

            if 0 <= indice_paciente < len(self.pacientes):
                paciente_selecionado = self.pacientes[indice_paciente]
                
                print(f"\nEscolha o médico para o(a) paciente {paciente_selecionado.nome}:")
                for j, m in enumerate(self.medicos, 1):
                    print(f"{j} - Dr(a). {m.nome} ({m.especialidade})")

                op_medico = int(input("Digite o número do médico: "))
                indice_medico = op_medico - 1

                if 0 <= indice_medico < len(self.medicos):
                    medico_escolhido = self.medicos[indice_medico]
                    paciente_selecionado.medico_responsavel = medico_escolhido
                    
                    # Salva após atualizar o vínculo
                    self.salvar_dados()
                    
                    print(f"\n-> Sucesso! Dr(a). {medico_escolhido.nome} foi vinculado(a) ao(à) paciente {paciente_selecionado.nome}.")
                else:
                    print("Opção de médico inválida.")
            else:
                print("Opção de paciente inválida.")
            sleep(2.5)
        except ValueError:
            print("Entrada inválida! Digite apenas números inteiros.")
            sleep(1.5)

    # Permite dar alta remover um paciente específico da lista.
    def dar_alta(self):
        print("\n=== DAR ALTA ===")
        if not self.pacientes:
            print("Não há pacientes internados para dar alta.")
            sleep(2)
            return

        for i, p in enumerate(self.pacientes, 1):
            print(f"{i} - {p.nome} (ID: {p.id} | Gravidade: {p.nivel})")

        try:
            escolha = int(input("\nDigite o número do paciente que vai receber alta: "))
            indice = escolha - 1

            if 0 <= indice < len(self.pacientes):
                paciente_removido = self.pacientes.pop(indice)
                
                # Salva após remover o paciente
                self.salvar_dados()
                
                print(f"-> Alta concedida para o paciente: {paciente_removido.nome} (ID: {paciente_removido.id})!")
            else:
                print("Opção inválida! Paciente não encontrado.")
            sleep(2)
        except ValueError:
            print("Entrada inválida! Digite um número.")
            sleep(1.5)

    # Gerencia a autoavaliação e retorna elas
    def sistema_auto_ajuda(self):
        """Espaço de autoavaliação"""
        print("\n=== ESPAÇO DE AUTOAJUDA ===")
        print("Escreva livremente o que você está sentindo:")
        relato = input("-> ")
        
        print("\nAvaliação de Intensidade:")
        print("1 - Muito leve / Calmo")
        print("2 - Leve / Desconfortável")
        print("3 - Moderado / Preocupante")
        print("4 - Intenso / Difícil")
        print("5 - Muito intenso / Urgente")

        while True:
            try:
                nivel = int(input("\nQual o nível de intensidade (1 a 5)? "))
                if 1 <= nivel <= 5:
                    break
                print("Número inválido! Digite entre 1 e 5.")
                sleep(1.5) 
            except ValueError:
                print("Digite apenas números inteiros.")
                sleep(1.5) 

        registro = RegistroAjuda(relato, nivel)
        self.historico_ajuda.append(registro)

        # Salva após registrar a autoajuda
        self.salvar_dados()

        print("\n" + "-" * 40)
        print(f"[ORIENTAÇÃO] {self.orientacoes_ajuda[nivel]}")
        print("-" * 40)
        input("\nPressione ENTER para voltar ao menu...")

    # Exibe estatísticas gerais
    def exibir_estatisticas(self):
        print("\n=== ESTATÍSTICAS DO SISTEMA ===")
        total_pacientes = len(self.pacientes)
        total_medicos = len(self.medicos)
        total_exames = len(self.exames)
        total_ajuda = len(self.historico_ajuda)

        print(f"• Total de Pacientes Cadastrados: {total_pacientes}")
        print(f"• Total de Médicos Cadastrados: {total_medicos}")
        print(f"• Total de Exames Cadastrados: {total_exames}")
        print(f"• Total de Registros de Autoajuda: {total_ajuda}")

        if total_pacientes > 0:
            print("\nDistribuição de Gravidade dos Pacientes:")
            for nivel in range(1, 6):
                quantidade = sum(1 for p in self.pacientes if p.nivel == nivel)
                print(f"  - Nível {nivel}: {quantidade} paciente(s)")

        input("\nPressione ENTER para voltar ao menu...")

    # Sistema de Busca
    def buscar_cadastros(self):
        print("\n=== BUSCA INTELIGENTE ===")
        print("1. Buscar Paciente por Nome")
        print("2. Buscar Médico por Especialidade")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            if not self.pacientes:
                print("Não há pacientes cadastrados no sistema.")
                sleep(2)
                return
            termo = input("Digite o nome do paciente (ou parte dele): ").lower()
            encontrados = [p for p in self.pacientes if termo in p.nome.lower()]
            
            print(f"\n=== RESULTADOS DA BUSCA ({len(encontrados)}) ===")
            if not encontrados:
                print("Nenhum paciente encontrado.")
            else:
                for p in encontrados:
                    print(p)
                    
        elif opcao == "2":
            if not self.medicos:
                print("Não há médicos cadastrados no sistema.")
                sleep(2)
                return
            termo = input("Digite a especialidade do médico (ou parte dela): ").lower()
            encontrados = [m for m in self.medicos if termo in m.especialidade.lower()]
            
            print(f"\n=== RESULTADOS DA BUSCA ({len(encontrados)}) ===")
            if not encontrados:
                print("Nenhum médico encontrado com essa especialidade.")
            else:
                for m in encontrados:
                    print(m)
        else:
            print("Opção inválida.")
        
        input("\nPressione ENTER para voltar ao menu...")

    # Fila de Atendimento por Prioridade
    def exibir_fila_prioridade(self):
        print("\n=== FILA DE ATENDIMENTO (POR PRIORIDADE) ===")
        if not self.pacientes:
            print("Nenhum paciente cadastrado.")
        else:
            # Ordena os pacientes do nível 5 para o nível 1
            pacientes_ordenados = sorted(self.pacientes, key=lambda p: p.nivel, reverse=True)
            
            print("A ordem prioriza os casos mais graves (Nível 5 no topo):\n")
            for i, p in enumerate(pacientes_ordenados, 1):
                print(f"{i}. [Gravidade: {p.nivel}] Nome: {p.nome} | Sintoma: {p.sintoma}")
        
        input("\nPressione ENTER para voltar ao menu...")

    # Controla o loop principal e a exibição do menu ordenado
    def executar(self):
        while True:
            self.limpar_terminal()
            print("\n=== SISTEMA HOSPITALAR ===")
            print("--- CADASTROS ---")
            print("1. Cadastrar Paciente")
            print("2. Cadastrar Médico")
            print("3. Cadastrar Exame")
            print("\n=== CONSULTAS E LISTAS ---")
            print("4. Listar Pacientes")
            print("5. Listar Médicos / Guia Médico")
            print("6. Visualizar Exames")
            print("7. Fila de Atendimento Prioritário")
            print("8. Buscar Paciente ou Médico")
            print("\n=== GERENCIAMENTO E APOIO ---")
            print("9. Vincular Médico a Paciente")
            print("10. Dar Alta a Paciente")
            print("11. Espaço de Autoajuda")
            print("12. Estatísticas do Sistema")
            print("0. Sair")
            print("==========================")

            opcao = input("\nEscolha uma opção: ")
            self.limpar_terminal()

            match opcao:
                case "1":
                    self.cadastrar_paciente()
                case "2":
                    self.cadastrar_medico()
                case "3":
                    self.cadastrar_exame()
                case "4":
                    self.listar_pacientes()
                case "5":
                    self.listar_medicos()
                case "6":
                    self.visualizar_exames()
                case "7":
                    self.exibir_fila_prioridade()
                case "8":
                    self.buscar_cadastros()
                case "9":
                    self.vincular_medico_paciente()
                case "10":
                    self.dar_alta()
                case "11":
                    self.sistema_auto_ajuda()
                case "12":
                    self.exibir_estatisticas()
                case "0":
                    print("\nEncerrando o sistema...")
                    sleep(2)
                    self.limpar_terminal()
                    break
                case _:
                    print("\nOpção inválida! Escolha entre 0 e 12.")
                    sleep(1.5)

# BLOCO PRINCIPAL
# Ponto de partida do script: instancia o sistema e inicia a execução
if __name__ == "__main__":
    sistema = SistemaHospitalar()
    sistema.executar()