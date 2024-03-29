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
            select u.first_name, u.last_name, r.*
            from meeting.doctors_appointments_report((current_date - interval '1 year')::date, current_date) as r
            join usr.users as u on r.doctor_id = u.id
            order by doctor_id, day_of_week, time_slot;
        """)
    elif num == 3:
        cursor.execute("""
            select *
            from usr.frequent_patients((now() - interval '1 month')::date,'now'::date);
        """)
    elif num == 4:
        cursor.execute("""
            select finance.get_possible_profit_last_month() as profit_last_month;
        """)
    elif num == 5:
        cursor.execute("""
            select * from usr.get_experiences_doctors(patients_per_year := 5, patients_total := 100, years_period := 10);
        """)

    data = cursor.fetchall()
    head = [desc[0] for desc in cursor.description]
    conn.close()
    return data, head


def custom_query(query):
    conn, cursor = get_connection()
    cursor.execute(query)
    data = cursor.fetchall()
    head = [desc[0] for desc in cursor.description]
    conn.close()
    return data, head
