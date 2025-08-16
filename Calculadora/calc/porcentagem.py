def gerar_percentual(x, y):
    if y != 0:
        return (x / y) * 100
    else:
        return "O divisor não pode ser zero!\n Desligando sistema..."