from utils import get_connection

def exe_first_query():
    conn, cursor = get_connection()
    cursor.execute("""select a.*
        from usr.patients as p
        cross join meeting.patients_last_appointments_for_query_1(p.id, '(L|M)%', '(L|M)%') as a;""")
    data = cursor.fetchall()
    head = [desc[0] for desc in cursor.description]
    return data, head
