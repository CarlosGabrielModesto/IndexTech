# import calc
from calc import basicos as basic
from calc import avançados as advncd
from calc import porcentagem as prcnt

# Solicita do usuário dois números inteiros
x = int(input("Digite um número inteiro: "))
y = int(input("Digite mais um número inteiro: "))

# Informa as opções de cálculos disponíveis
print(f"""
--------------------------
| Operações disponíveis:
| 
| 1 - {basic.somar.__name__}
| 2 - {basic.subtrair.__name__}
| 3 - {basic.multiplicar.__name__}
| 4 - {basic.dividir.__name__}
| 5 - {advncd.exponenciar.__name__}
| 6 - {prcnt.gerar_percentual.__name__}
|-------------------------
""")

# Capta a escolha do usuário e seleciona a função correspondente
match input("Selecione uma opção: "):
    case "1":
        print(basic.somar(x, y))
    case "2":
        print(basic.subtrair(x, y))
    case "3":
        print(basic.multiplicar(x, y))
    case "4":
        print(basic.dividir(x, y))
    case "5":
        print(advncd.exponenciar(x, y))
    case "6":
        print(prcnt.gerar_percentual(x, y))
    case __:
        print("Operação não reconhecida")
        exit()

