import mysql.connector
import sys

# Configurazione database
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'user',
    'password': 'userpass',
    'database': 'userdb'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def inserisci_utente(nome, email, eta):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO users (nome, email, eta) VALUES (%s, %s, %s)"
    cursor.execute(query, (nome, email, eta))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Utente {nome} inserito con successo!")

def visualizza_utenti():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, email, eta, created_at FROM users ORDER BY id")
    utenti = cursor.fetchall()
    
    if utenti:
        print("\n=== UTENTI NEL DATABASE ===")
        print("ID | Nome | Email | Eta | Creato")
        print("-" * 50)
        for utente in utenti:
            print(f"{utente[0]} | {utente[1]} | {utente[2]} | {utente[3]} | {utente[4]}")
    else:
        print("Nessun utente nel database")
    
    cursor.close()
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("Uso: python sql.py [inserisci|visualizza]")
        return
    
    comando = sys.argv[1].lower()
    
    if comando == "inserisci":
        nome = input("Nome: ")
        email = input("Email: ")
        eta = int(input("Eta: "))
        inserisci_utente(nome, email, eta)
    
    elif comando == "visualizza":
        visualizza_utenti()
    
    else:
        print("Comando non riconosciuto. Usa 'inserisci' o 'visualizza'")

if __name__ == "__main__":
    main()