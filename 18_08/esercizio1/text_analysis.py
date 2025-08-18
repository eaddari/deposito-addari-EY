def conta_parole(testo):
    parole = testo.split()
    return len(parole)

def conta_righe(testo):
    righe = testo.split('\n')
    return len(righe)


if __name__ == "__main__":

    file_path = "C:\\desktopnoonedrive\\Ai Academy\\deposito-addari-EY\\18_08\\esercizio1\\misc_files\\testo_18_08.txt"

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    print("Numero di parole:", conta_parole(content))
    print("Numero di righe:", conta_righe(content))
