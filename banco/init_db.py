from banco import BancoDeDados

db = BancoDeDados()
db.adicionar_placa("ABC1234")
db.adicionar_placa("IXX9F23")
print("Placas inseridas com sucesso!")
# para rodar -> python init_db.py

print(db.listar_placas())
