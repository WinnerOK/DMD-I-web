from utils import get_connection

def execute_query(num):
    conn, cursor = get_connection()
    if num == 1:
        cursor.execute("""
            select a.*
            from usr.patients as p
            cross join meeting.patients_last_appointments_for_query_1(p.id, '(L|M)%', '(L|M)%') as a;
        """)
    elif num == 2:
        cursor.execute("""
            select r.*
            from meeting.doctors_appointments_report('2018-12-01', '2019-12-01') as r;
        """)
    elif num == 3:
        # TODO: insert 3rd query
        cursor.execute("""
            select * from usr.get_experiences_doctors();
        """)
    elif num == 4:
        cursor.execute("""
            select finance.get_possible_profit_last_month() as profit_last_month;
        """)
    elif num == 5:
        cursor.execute("""
            select * from usr.get_experiences_doctors();
        """)

    data = cursor.fetchall()
    head = [desc[0] for desc in cursor.description]
    return data, head
