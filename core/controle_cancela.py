from banco.banco import BancoDeDados

class ControleCancela:
    def __init__(self, db=None):
        self.db = db if db is not None else BancoDeDados()

    def verificar_placa(self, placa: str):
        if not placa:
            return False, "PLACA INVÁLIDA"

        placa = placa.upper().strip()


        if not self.db.placa_autorizada(placa):
            self.db.registrar_movimento(placa, "NEGADO")
            return False, "ACESSO NEGADO"


        if self.db.esta_no_patio(placa):
            self.db.registrar_movimento(placa, "SAIDA")
            return True, "SAÍDA LIBERADA"


        self.db.registrar_movimento(placa, "ENTRADA")
        return True, "ENTRADA LIBERADA"


if __name__ == "__main__":
    controle = ControleCancela()
    placa_testada = input("Digite a placa detectada: ").strip()
    resultado, mensagem = controle.verificar_placa(placa_testada)
    print("Resultado:", resultado)
    print("Mensagem:", mensagem)
