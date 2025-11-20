# database.py
# Simple MySQL connector for Hospital-Management-System
# Exposes `conn` and `cursor` at module level.

import os
import mysql.connector
from mysql.connector import errorcode

# --- Configuration (edit here or set environment variables) ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD}", "TXsThakur@18")   # or set env var DB_PASSWORD
DB_NAME = os.environ.get("DB_NAME", "hospital_db")
CREATE_SQL_FILE = os.path.join(os.path.dirname(__file__), "create_tables.sql")
# ------------------------------------------------------------

def _connect(select_db=True):
    """Return a mysql.connector connection. If select_db is False, do not set database."""
    kwargs = dict(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    if select_db:
        kwargs["database"] = DB_NAME
    return mysql.connector.connect(**kwargs)

def _run_sql_file(conn, sql_path):
    """Run statements from a .sql file using the provided connection."""
    if not os.path.isfile(sql_path):
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    # naive split on ';' — good for simple schema files
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    cur = conn.cursor()
    try:
        for stmt in statements:
            try:
                cur.execute(stmt)
            except mysql.connector.Error as e:
                # Some statements may produce warnings if re-run; show but continue
                print(f"[database.py] Warning executing statement: {e}")
        conn.commit()
    finally:
        cur.close()

# Try to connect directly to the target DB
try:
    conn = _connect(select_db=True)
except mysql.connector.Error as err:
    # If DB does not exist, try to create it from create_tables.sql
    if getattr(err, "errno", None) == errorcode.ER_BAD_DB_ERROR:
        print(f"[database.py] Database '{DB_NAME}' not found. Attempting to create it using {CREATE_SQL_FILE}...")
        try:
            # Connect without selecting a DB
            temp_conn = _connect(select_db=False)
            # Create the database and run SQL file which usually includes CREATE DATABASE; but ensure DB exists
            try:
                temp_cur = temp_conn.cursor()
                temp_cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET 'utf8mb4'")
                temp_cur.close()
                # Now run the SQL file (it may contain USE statements)
                _run_sql_file(temp_conn, CREATE_SQL_FILE)
            finally:
                temp_conn.close()
            # Reconnect to the newly created database
            conn = _connect(select_db=True)
        except FileNotFoundError as e:
            raise SystemExit(f"[database.py] ERROR: {e}\nPlace create_tables.sql in the project root or create the database manually.")
        except mysql.connector.Error as e2:
            raise SystemExit(f"[database.py] ERROR while creating DB: {e2}")
    else:
        raise SystemExit(f"[database.py] ERROR connecting to MySQL: {err}")

# Provide a buffered cursor for other modules to import and use safely
try:
    cursor = conn.cursor(buffered=True)
except Exception as e:
    # Close conn if cursor creation fails
    try:
        conn.close()
    except Exception:
        pass
    raise SystemExit(f"[database.py] ERROR creating cursor: {e}")

def close():
    """Close cursor and connection."""
    global cursor, conn
    try:
        if cursor:
            cursor.close()
    except Exception:
        pass
    try:
        if conn:
            conn.close()
    except Exception:
        pass
