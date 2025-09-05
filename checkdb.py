import sqlite3

def check_db():
    try:
        # Database se connect
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()

        # Table exist hai ya nahi check karo
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments';")
        table = cursor.fetchone()
        if not table:
            print("⚠️ Table 'appointments' abhi tak nahi bana.")
            return

        print("✅ Table 'appointments' found!")

        # Kuch records dekh lo
        cursor.execute("SELECT * FROM appointments LIMIT 5;")
        rows = cursor.fetchall()

        if rows:
            print("\n📋 Sample Records:")
            for row in rows:
                print(row)
        else:
            print("ℹ️ Table khaali hai (no data yet).")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
