import os
from typing import Optional
from banco.banco import BancoDeDados   # <-- agora correto

DB = BancoDeDados()


def limpa_tela():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_menu():
    print("=== Gerenciar Placas - Cancela ===")
    print("1) Adicionar placa")
    print("2) Remover placa")
    print("3) Listar placas autorizadas")
    print("4) Ver movimentação (últimas 50)")
    print("5) Sair")


def ler_input_placa(prompt: str) -> Optional[str]:
    raw = input(prompt).strip()
    if not raw:
        print("Placa vazia.")
        return None

    placa_norm = DB._normalize_plate(raw)
    if not placa_norm:
        print("Placa inválida após normalização.")
        return None

    return placa_norm


def adicionar_placa():
    print("\n=== Adicionar Placa ===")
    placa = ler_input_placa("Digite a placa (ex: ABC1D234): ")
    if not placa:
        return

    descricao = input("Descrição (opcional): ").strip()
    ok = DB.adicionar_placa(placa, descricao)

    if ok:
        print(f"✅ Placa {placa} adicionada com sucesso.")
    else:
        print(f"⚠️ Placa {placa} já existe ou ocorreu um erro.")


def remover_placa():
    print("\n=== Remover Placa ===")
    placa = ler_input_placa("Digite a placa a remover: ")
    if not placa:
        return

    ok = DB.remover_placa(placa)

    if ok:
        print(f"✅ Placa {placa} removida.")
    else:
        print(f"⚠️ Placa {placa} não encontrada.")


def listar_placas():
    print("\n=== Placas Autorizadas ===")
    placas = DB.listar_placas()

    if not placas:
        print("Nenhuma placa cadastrada.")
        return

    for i, (placa, desc) in enumerate(placas, start=1):
        print(f"{i:02d}. {placa} - {desc}")


def ver_movimentacao():
    print("\n=== Movimentação (Últimas 50) ===")
    movs = DB.listar_movimentacao()

    if not movs:
        print("Sem movimentações registradas.")
        return

    for i, (placa, data_hora, tipo) in enumerate(movs[:50], start=1):
        print(f"{i:03d} | {data_hora} | {placa} | {tipo}")


def main():
    while True:
        limpa_tela()
        mostrar_menu()

        escolha = input("\nEscolha: ").strip()

        if escolha == "1":
            adicionar_placa()
        elif escolha == "2":
            remover_placa()
        elif escolha == "3":
            listar_placas()
        elif escolha == "4":
            ver_movimentacao()
        elif escolha == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
