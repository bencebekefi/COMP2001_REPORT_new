import pyodbc

try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DIST-6-505.uopnet.plymouth.ac.uk;"
        "DATABASE=COMP2001_BBekefi;"
        "UID=BBekefi;"
        "PWD=AqrM335*"
    )
    print("Connection successful!")
except Exception as e:
    print("Connection failed:", e)

