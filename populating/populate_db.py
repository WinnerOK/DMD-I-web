import psycopg2
from psycopg2.extensions import cursor, connection
import requests
from typing import Tuple
from .rand_person import *
from threading import Thread, Lock
import random
import re
from collections import defaultdict

lock = Lock()

ONLY_PRODUCE_SQL = True

COUNTERS = defaultdict(int)


class Writer:

    def __init__(self):
        self.file = open("queries.sql", "w")
        self.lines = 0

    def write(self, query):
        query = re.sub('(%\(.*?\)s)', "'\g<1>'", query)
        query = query.replace("'None'", "null")
        self.file.write(query + ";\n")
        self.lines += 1

    def close(self):
        print(self.lines)
        self.file.close()


out = Writer()


def get_connection() -> Tuple[cursor, connection]:
    result = requests.get('https://dmd-project-p3.herokuapp.com/cred/postgres')
    credentials = dict(item.split(":") for item in result.text.split('<br>'))
    conn = psycopg2.connect(' '.join(map(lambda item: '='.join(item), credentials.items())))
    cur = conn.cursor()
    return cur, conn


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def fast_insert(cur, conn, tablename, fields, table):
    if ONLY_PRODUCE_SQL:
        global COUNTERS
        COUNTERS[tablename] += len(table)

    for rows in chunker(table, 100):
        args_str = ','.join(cur.mogrify(f"""({', '.join([f"%({x})s" for x in fields])})""", x).decode() for x in rows)

        out.write(f"INSERT INTO {tablename} ({', '.join(fields)}) VALUES {args_str}")

        if not ONLY_PRODUCE_SQL:
            cur.execute(f"INSERT INTO {tablename} ({', '.join(fields)}) VALUES {args_str}")

        conn.commit()


def populate_users(n, cur, conn):
    '''
    populate db by fake people and returns their entries from db

    :param n: number of people to generate
    :param cur: cursor
    :param conn: connection
    :return: people ids
    '''
    fields = [
        "first_name",
        "last_name",
        "email",
        "hash_pass",
        "birth_date",
        "insurance_company",
        "insurance_number"
    ]

    people = [Person() for _ in range(n)]

    fast_insert(cur, conn, "usr.users", fields, people)

    if ONLY_PRODUCE_SQL:
        people_ids = [i for i in range(COUNTERS["usr.users"])]
    else:
        cur.execute(f"SELECT * FROM usr.users;")
        people_entries = cur.fetchall()
        people_ids = [item[0] for item in people_entries]
    return people_ids


def populate_one_field_id(table_name, people, hrs=None, staff=True, is_doctor=False, is_paramedic=False):
    cur, conn = get_connection()
    fields = ['id']
    table_tuple = tuple(map(lambda x: {"id": x}, people))

    if is_doctor:
        fields.append('specialization')
        fields.append('clinic_number')

    if is_paramedic:
        fields.append('position')

    if staff:
        table_tuple = populate_staff(people, hrs)

    fast_insert(cur, conn, f"usr.{table_name}", fields, table_tuple)

    cur.close()
    conn.close()


def populate_staff(people, hrs=None):
    '''
    first n people will be hired as hrs
    populates staff with hrs

    :param is_doctor: doctor field
    :param people: people entries instances
    :param hrs: hs list
    :return: created HR entries
    '''

    cur, conn = get_connection()
    fields = [
        "id",
        "employment_start",
        "hired_by",
        "salary",
        "schedule_type",
    ]

    if hrs is None:
        fields.remove("hired_by")

    staff = []

    for i in range(len(people)):
        staff_item = Staff()
        staff_item.id = people[i]
        if hrs is not None:
            staff_item.hired_by = hrs[i % len(hrs)]
        staff.append(staff_item)

    fast_insert(cur, conn, "usr.staff", fields, staff)

    cur.close()
    conn.close()

    return staff


def doctors_nurses(doctors, nurses):
    assert len(doctors) > 2
    assert len(nurses) > 2

    table_array = []

    cur, conn = get_connection()
    fields = [
        "doctor_id",
        "nurse_id"
    ]

    for i in range(len(doctors) // 2):
        for j in range(len(nurses) // 2):
            table_array.append({"doctor_id": doctors[i], "nurse_id": nurses[j]})

    fast_insert(cur, conn, "usr.doctors_nurses", fields, table_array)

    cur.close()
    conn.close()


def in_patient_directions(patients, doctors):
    assert len(doctors) > 2
    assert len(patients) > 2

    table_array = []

    cur, conn = get_connection()
    fields = [
        "is_made_by",
        "directs"
    ]

    for i in range(len(patients) // 2):
        table_array.append({"is_made_by": random.choice(doctors), "directs": patients[i]})

    fast_insert(cur, conn, "meeting.in_patient_directions", fields, table_array)

    cur.close()
    conn.close()


def create_chats_and_populate_chat_participants(chats, people):
    cur, conn = get_connection()
    fields = [
        "name",
        "chat_type"
    ]

    chats = [Chat() for _ in range(chats)]

    fast_insert(cur, conn, "msg.chats", fields, chats)

    if ONLY_PRODUCE_SQL:
        chat_ids = [i for i in range(COUNTERS['msg.chats'])]
    else:
        cur.execute(f"SELECT * FROM msg.chats;")
        chats_entries = cur.fetchall()
        chat_ids = [item[0] for item in chats_entries]

    fields = [
        "chat_id",
        "user_id"
    ]

    chats_participants = defaultdict(lambda: [])

    table_array = []
    for chat_id in chat_ids:
        for person in people:
            if random.choice([True, False]):
                chats_participants[chat_id].append(person)
                table_array.append({"chat_id": chat_id, "user_id": person})

    fast_insert(cur, conn, "msg.chats_participants", fields, table_array)

    cur.close()
    conn.close()

    return chats_participants


def create_and_populate_medical_records_and_modifications(patients, doctors):
    cur, conn = get_connection()
    fields = [
        "content",
        "belongs_to"
    ]

    messages = [{
        "content": fake.medical_record_content(),
        "belongs_to": patient
    } for patient in patients
    ]

    fast_insert(cur, conn, "medical_data.medical_records", fields, messages)

    if ONLY_PRODUCE_SQL:
        medical_records_ids = [i for i in range(COUNTERS["medical_data.medical_records"])]
    else:
        cur.execute(f"SELECT * FROM medical_data.medical_records;")
        medical_records_entries = cur.fetchall()
        medical_records_ids = [item[0] for item in medical_records_entries]

    fields = [
        "change",
        "change_type",
        "modifies",
        "is_made_by"
    ]

    table_array = []
    for medical_record_id in medical_records_ids * 2:
        msg = Message()
        table_array.append({"change": fake.medical_record_content(),
                            "change_type": msg.change_type,
                            "modifies": medical_record_id,
                            "is_made_by": random.choice(doctors)
                            })

    fast_insert(cur, conn, "medical_data.medical_record_modifications", fields, table_array)

    cur.close()
    conn.close()


def create_and_populate_messages_and_modifications(staff, messages):
    cur, conn = get_connection()
    fields = [
        "text"
    ]

    messages = [{"text": Message().content} for _ in range(messages)]

    fast_insert(cur, conn, "board.messages", fields, messages)

    if ONLY_PRODUCE_SQL:
        messages_ids = [i for i in range(COUNTERS["board.messages"])]
    else:
        cur.execute(f"SELECT * FROM board.messages;")
        messages_entries = cur.fetchall()
        messages_ids = [item[0] for item in messages_entries]

    fields = [
        "change",
        "change_type",
        "modifies",
        "made_by"
    ]

    table_array = []
    for message in messages_ids:
        for employee in staff:
            if random.choice([True, False]):
                msg = Message()
                table_array.append({"change": msg.content,
                                    "change_type": msg.change_type,
                                    "modifies": message,
                                    "made_by": employee
                                    })

    fast_insert(cur, conn, "board.modifications", fields, table_array)

    cur.close()
    conn.close()


def create_and_populate_paramedic_group_and_divisions(paramedics, group):
    cur, conn = get_connection()
    fields = [
        "is_active"
    ]

    groups = [{fields[0]: random.choice([True, False])} for _ in range(group)]

    fast_insert(cur, conn, "usr.paramedic_groups", fields, groups)

    if ONLY_PRODUCE_SQL:
        groups_ids = [i for i in range(COUNTERS["usr.paramedic_groups"])]
    else:
        cur.execute(f"SELECT * FROM usr.paramedic_groups;")
        groups_entries = cur.fetchall()
        groups_ids = [item[0] for item in groups_entries]

    fields = [
        "paramedic_id",
        "group_id"
    ]

    paramedics_group = defaultdict(lambda: [])

    table_array = []
    for group in groups_ids:
        for paramedic in paramedics:
            if random.choice([True, False]):
                paramedics_group[group].append(paramedic)
                table_array.append({"group_id": group, "paramedic_id": paramedic})

    fast_insert(cur, conn, "usr.paramedic_group_divisions", fields, table_array)

    cur.close()
    conn.close()

    return groups_ids


def create_directions(doctors, patients):
    table_array = []

    cur, conn = get_connection()
    fields = [
        "directs",
        "is_made_by",
        "directs_to",
    ]

    for i in range(len(doctors) + len(patients)):
        table_array.append({"directs": random.choice(patients),
                            "is_made_by": random.choice(doctors),
                            "directs_to": random.choice(doctors),
                            })

    fast_insert(cur, conn, "meeting.redirections", fields, table_array)

    cur.close()
    conn.close()


def create_invoices(cur, conn, invoices):
    fields = [
        "text",
        "amount",
        "paid_by"
    ]

    with lock:
        fast_insert(cur, conn, "finance.invoices", fields, invoices)

        if ONLY_PRODUCE_SQL:
            invoices_ids = [i for i in range(COUNTERS["finance.invoices"])]
        else:
            cur.execute(f"SELECT * FROM finance.invoices;")
            invoices_entries = cur.fetchall()
            invoices_ids = [item[0] for item in invoices_entries]
        return invoices_ids[-len(invoices):]


def ambulance_calls_and_payment(patients, groups, receptionists):
    table_array = []

    cur, conn = get_connection()

    invoices = [{"text": "ambulance call", "amount": random.randint(100, 1000), "paid_by": patient} for patient in
                patients]

    invoices_ids = create_invoices(cur, conn, invoices)

    fields = [
        "location",
        "assigned_group",
        "assigned_invoice",
        "is_made_by"
    ]

    for ind, patient in enumerate(patients):
        table_array.append({"location": '(1, 2)',
                            "is_made_by": patient,
                            "assigned_group": random.choice(groups),
                            "assigned_invoice": invoices_ids[ind]
                            })

    fast_insert(cur, conn, "medical_data.ambulance_calls", fields, table_array)

    fields = [
        "type",
        "insurance_company",
        "insurance_number",
        "accepted_by",
        "pays_for"
    ]

    table_array = []
    for i in range(len(invoices)):
        p = Person()
        table_array.append({"type": p.payment_type,
                            "insurance_company": p.insurance_company,
                            "insurance_number": p.insurance_number,
                            "accepted_by": receptionists[i % len(receptionists)],
                            "pays_for": invoices_ids[i]
                            })

    fast_insert(cur, conn, "finance.payments", fields, table_array)

    cur.close()
    conn.close()


def populate_prescription_dependant_tables(patients, pharmacists, inventory_managers):
    table_array = []
    cur, conn = get_connection()

    prescriptions = [{"issue_date": Message().datetime} for _ in range(len(patients))]

    fields = [
        "issue_date"
    ]

    fast_insert(cur, conn, "medical_data.prescriptions", fields, prescriptions)

    if ONLY_PRODUCE_SQL:
        prescriptions_ids = [i for i in range(COUNTERS["medical_data.prescriptions"])]
    else:
        cur.execute(f"SELECT * FROM medical_data.prescriptions;")
        prescriptions_entries = cur.fetchall()
        prescriptions_ids = [item[0] for item in prescriptions_entries]

    fields = [
        "name",
        "cost_per_unit",
        "quantity",
        "units",
        "is_consumable",
        "category",
        "need_prescription",
    ]

    for i in range(len(patients)):
        table_array.append({"name": f"some important pill{i}",
                            "cost_per_unit": random.randint(1, 100),
                            "quantity": random.randint(50, 100),
                            "units": "Items",
                            "is_consumable": True,
                            "category": "Pharmacy item",
                            "need_prescription": True,
                            })

    fast_insert(cur, conn, "inventory.inventory_items", fields, table_array)

    if ONLY_PRODUCE_SQL:
        inventory_items_ids = [i for i in range(COUNTERS["inventory.inventory_items"])]
    else:
        cur.execute(f"SELECT * FROM inventory.inventory_items;")
        inventory_items_entries = cur.fetchall()
        inventory_items_ids = [item[0] for item in inventory_items_entries]

    fields = [
        "prescription_id",
        "inventory_item_id"
    ]

    table_array = []
    for i in range(1, len(patients) + 1):
        table_array.append({"prescription_id": prescriptions_ids[-i],
                            "inventory_item_id": inventory_items_ids[-i]
                            })

    fast_insert(cur, conn, "medical_data.prescription_allowances", fields, table_array)

    fields = [
        "item_id",
        "requested_by",
        "approved_by",
        "quantity",
        "status"
    ]

    table_array = []
    for i in range(len(patients)):
        status = fake.item_request_status()
        table_array.append({"item_id": inventory_items_ids[i],
                            "quantity": random.randint(1, 50),
                            "status": status,
                            "approved_by": inventory_managers[
                                i % len(inventory_managers)] if status != "Pending" else None,
                            "requested_by": pharmacists[i % len(pharmacists)]
                            })

    fast_insert(cur, conn, "inventory.inventory_items_requests", fields, table_array)

    invoices = [{"text": "item sale", "amount": random.randint(100, 1000), "paid_by": patient} for patient in
                patients]

    invoices_ids = create_invoices(cur, conn, invoices)

    fields = [
        "item_id",
        "quantity",
        "cost_per_unit",
        "sold_by",
        "invoice_id"
    ]

    table_array = []
    for i in range(len(patients)):
        table_array.append({"item_id": inventory_items_ids[i],
                            "quantity": random.randint(1, 100),
                            "cost_per_unit": random.randint(1, 100),
                            "sold_by": pharmacists[i % len(pharmacists)],
                            "invoice_id": invoices_ids[i],
                            })

    fast_insert(cur, conn, "inventory.item_sales", fields, table_array)

    cur.close()
    conn.close()


def appointments(doctors, patients):
    table_array = []

    mult = 40

    cur, conn = get_connection()

    invoices = [{"text": "doctor appointment", "amount": random.randint(100, 1000), "paid_by": patient} for patient
                in
                patients * (mult + 1)]

    invoices_ids = create_invoices(cur, conn, invoices)

    fields = [
        "doctor_id",
        "patient_id",
        "datetime",
        "location",
        "invoice_id"
    ]

    dates = set()

    for ind, patient in enumerate(patients * mult):
        date = Staff().employment_start
        while date in dates:
            date = Staff().employment_start

        dates.add(date)

        table_array.append({"location": random.randint(100, 400),
                            "patient_id": patient,
                            "doctor_id": random.choice(doctors),
                            "datetime": date,
                            "invoice_id": invoices_ids[ind]
                            })

    fast_insert(cur, conn, "meeting.appointments", fields, table_array)

    mult = 15

    invoices = [{"text": "doctor appointment", "amount": random.randint(100, 1000), "paid_by": patient} for patient
                in
                patients * mult]

    invoices_ids = create_invoices(cur, conn, invoices)

    fields = [
        "doctor_id",
        "patient_id",
        "datetime",
        "location",
        "invoice_id"
    ]

    table_array = []
    for ind, patient in enumerate(patients * mult):
        date = Message().datetime
        while date in dates:
            date = Message().datetime
        dates.add(date)
        table_array.append({"location": random.randint(100, 400),
                            "patient_id": patient,
                            "doctor_id": random.choice(doctors),
                            "datetime": date,
                            "invoice_id": invoices_ids[ind]
                            })

    fast_insert(cur, conn, "meeting.appointments", fields, table_array)

    cur.close()
    conn.close()


def analyses(patients, lab_technicians):
    table_array = []

    cur, conn = get_connection()

    invoices = [{"text": "analyses", "amount": random.randint(100, 1000), "paid_by": patient} for patient
                in
                patients]

    invoices_ids = create_invoices(cur, conn, invoices)

    fields = [
        "type",
        "status",
        "result",
        "assigned_invoice",
        "datetime_proceeded",
        "datetime_collected",
        "proceeded_by",
        "requested_by",
    ]

    for ind, patient in enumerate(patients):
        date = fake.date_time_between(start_date="-9d", end_date="-1d", tzinfo=None) if random.choice(
            [True, False]) else None
        date_collected = fake.date_time_between(start_date="-30d", end_date="-10d", tzinfo=None)
        table_array.append({"type": fake.analysis_type(),
                            "status": 'Proceeded' if date else 'Collected',
                            "result": 'Good' if date else None,
                            "assigned_invoice": invoices_ids[ind],
                            "requested_by": patients[ind],
                            "datetime_proceeded": date,
                            "datetime_collected": date_collected,
                            "proceeded_by": lab_technicians[ind % len(lab_technicians)],
                            })

    fast_insert(cur, conn, "medical_data.analyses", fields, table_array)

    cur.close()
    conn.close()


def ipc(patients):
    cur, conn = get_connection()

    table_array = [
        {
            "service_name": f"service{i}",
            "amount": random.randint(100, 10_000)
        } for i in range(5)
    ]

    fields = [
        "service_name",
        "amount"
    ]

    fast_insert(cur, conn, "ipc.in_patient_clinic_services", fields, table_array)

    if ONLY_PRODUCE_SQL:
        in_patient_clinic_services_ids = [i for i in range(COUNTERS["ipc.in_patient_clinic_services"])]
    else:
        cur.execute(f"SELECT * FROM ipc.in_patient_clinic_services;")
        in_patient_clinic_services_entries = cur.fetchall()
        in_patient_clinic_services_ids = [item[0] for item in in_patient_clinic_services_entries]

    table_array = [
        {
            "room": f"{random.randint(100, 400)}",
            "amount_per_day": random.randint(100, 10_000)
        } for i in range(10)
    ]

    fields = [
        "room",
        "amount_per_day"
    ]

    fast_insert(cur, conn, "ipc.in_patient_clinic_places", fields, table_array)

    if ONLY_PRODUCE_SQL:
        in_patient_clinic_places_ids = [i for i in range(COUNTERS["ipc.in_patient_clinic_places"])]
    else:
        cur.execute(f"SELECT * FROM ipc.in_patient_clinic_places;")
        in_patient_clinic_places_entries = cur.fetchall()
        in_patient_clinic_places_ids = [item[0] for item in in_patient_clinic_places_entries]

    fields = [
        "name",
        "cost_per_unit",
        "quantity",
        "units",
        "is_consumable",
        "category",
        "need_prescription",
        "belongs_to_place"
    ]

    table_array = []
    for i in range(10):
        table_array.append({"name": f"bed {i}",
                            "cost_per_unit": random.randint(1, 100),
                            "quantity": random.randint(50, 100),
                            "units": "Items",
                            "is_consumable": False,
                            "category": "In-patient clinic inventory",
                            "need_prescription": False,
                            "belongs_to_place": in_patient_clinic_places_ids[i]
                            })

    fast_insert(cur, conn, "inventory.inventory_items", fields, table_array)

    invoices = [{"text": "in patient clinic", "amount": random.randint(100, 1000), "paid_by": patient} for patient in
                patients]

    invoices_ids = create_invoices(cur, conn, invoices)

    fields = [
        "place_id",
        "occupied_by",
        "invoice_id",
        "amount_per_day",
    ]

    table_array = []
    for i in range(7):
        table_array.append({"place_id": in_patient_clinic_places_ids[i % len(in_patient_clinic_places_ids)],
                            "occupied_by": patients[i % len(patients)],
                            "invoice_id": invoices_ids[i],
                            "amount_per_day": random.randint(50, 100),
                            })

    fast_insert(cur, conn, "ipc.in_patient_clinic_stay", fields, table_array)

    if ONLY_PRODUCE_SQL:
        in_patient_clinic_stay_ids = [i for i in range(COUNTERS["ipc.in_patient_clinic_stay"])]
    else:
        cur.execute(f"SELECT * FROM ipc.in_patient_clinic_stay;")
        in_patient_clinic_stay_entries = cur.fetchall()
        in_patient_clinic_stay_ids = [item[0] for item in in_patient_clinic_stay_entries]

    fields = [
        "stay_id",
        "service",
        "amount"
    ]

    table_array = []
    for i in range(len(in_patient_clinic_places_ids)):
        table_array.append({"stay_id": in_patient_clinic_stay_ids[i % len(in_patient_clinic_stay_ids)],
                            "service": in_patient_clinic_services_ids[i % len(in_patient_clinic_services_ids)],
                            "amount": random.randint(100, 300)
                            })

    fast_insert(cur, conn, "ipc.in_patient_clinic_provided_services", fields, table_array)

    cur.close()
    conn.close()


def create_messages(messages_count, chat_participants):
    cur, conn = get_connection()
    fields = [
        "content_type",
        "content",
        "datetime",
        "sent_by",
        "sent_to"
    ]

    messages = []
    chat_names = list(chat_participants.keys())
    for i in range(messages_count):
        to = random.choice(chat_names)
        by = random.choice(chat_participants[to])
        message_item = Message()
        message_item.sent_by = by
        message_item.sent_to = to
        messages.append(message_item)

    fast_insert(cur, conn, "msg.messages", fields, messages)

    cur.close()
    conn.close()


def split_people_ids(on):
    slices = [slice(on[0])]
    last = on[0]
    for elem in on[1:]:
        slices.append(slice(last, last + elem))
        last = elem + last

    return slices


def run_and_wait_threads(threads):
    for thread in threads:
        if not thread._started.is_set():
            thread.start()

    jobs = len(threads)
    for ind, thread in enumerate(threads):
        print(f"completed {ind + 1} / {jobs} thread")
        thread.join()

    threads.clear()


def main(
        users: int = 150,
        hr: int = 4,
        doctors: int = 23,
        receptionists: int = 2,
        lab_technicians: int = 4,
        inventory_managers: int = 2,
        admin: int = 1,
        nurses: int = 10,
        paramedics: int = 5,
        patients: int = 50,
        pharmacists: int = 2,
        paramedics_groups: int = 3,
        chats: int = 5,
        chat_messages: int = 20,
        notice_board_messages: int = 10,
        execute_queries: bool = False,
        truncate_tables: bool = False) -> None:

    global ONLY_PRODUCE_SQL
    ONLY_PRODUCE_SQL = not execute_queries

    cur, conn = get_connection()

    if truncate_tables:
        cur.execute('truncate table usr.users cascade;')
        cur.execute('truncate table msg.chats cascade;')
        cur.execute('truncate table board.messages cascade;')
        cur.execute('truncate table meeting.redirections cascade;')
        cur.execute('truncate table finance.invoices cascade;')
        cur.execute('truncate table medical_data.prescriptions cascade;')
        cur.execute('truncate table inventory.inventory_items cascade;')
        cur.execute('truncate table ipc.in_patient_clinic_provided_services cascade;')
        cur.execute('truncate table ipc.in_patient_clinic_places cascade;')
        cur.execute('truncate table medical_data.medical_records cascade;')

    # separate users to different staff and patients
    slices = split_people_ids([
        hr, doctors, receptionists, lab_technicians, inventory_managers, admin,
        nurses, paramedics, patients, paramedics, pharmacists
    ])

    # get people array split for different roles
    hr_slice, doctors_slice, receptionists_slice, lab_technicians_slice, inventory_managers_slice, \
    admins_slice, nurses_slice, paramedics_slice, patients_slice, paramedics_slice, pharmacists_slice = slices

    # populate users and hrs as further staff depends on them
    people = populate_users(users, cur, conn)
    populate_one_field_id('hrs', people[hr_slice])
    # populate paramedics and tables connected with them
    populate_one_field_id('paramedics', people[paramedics_slice], hrs=people[hr_slice], is_paramedic=True)
    paramedics_groups_ids = create_and_populate_paramedic_group_and_divisions(people[paramedics_slice],
                                                                              paramedics_groups)

    # populate specific staff
    threads = [
        Thread(target=populate_one_field_id, args=('patients', people[patients_slice]), kwargs={"staff": False}),
        Thread(target=populate_one_field_id, args=('doctors', people[doctors_slice]),
               kwargs={"hrs": people[hr_slice], "is_doctor": True})]

    threads[0].start()  # speedup

    # populate one field staff
    for name, name_slice in zip([
        "receptionists",
        "lab_technicians",
        "inventory_managers",
        "admins",
        "nurses",
        "pharmacists"
    ], [
        receptionists_slice,
        lab_technicians_slice,
        inventory_managers_slice,
        admins_slice,
        nurses_slice,
        pharmacists_slice
    ]):
        threads.append(Thread(target=populate_one_field_id, args=(name, people[name_slice]),
                              kwargs={"hrs": people[hr_slice]}))

    # sync threads
    run_and_wait_threads(threads)
    print("populated staff")

    threads.append(
        Thread(target=populate_prescription_dependant_tables, args=(people[patients_slice], people[pharmacists_slice],
                                                                    people[inventory_managers_slice])))
    threads[0].start()  # speedup

    # appointments
    threads.append(Thread(target=appointments, args=(people[doctors_slice], people[patients_slice])))

    # create and populate medical records
    threads.append(Thread(target=create_and_populate_medical_records_and_modifications,
                          args=(people[patients_slice], people[doctors_slice])))

    # ipc
    threads.append(Thread(target=ipc, args=(people[patients_slice],)))

    # analyses
    threads.append(Thread(target=analyses, args=(people[patients_slice], people[lab_technicians_slice])))

    # redirections
    threads.append(Thread(target=create_directions, args=(people[doctors_slice], people[patients_slice])))

    # create and populate chats with messages
    chat_participants = create_chats_and_populate_chat_participants(chats, people)
    threads.append(Thread(target=create_messages, args=(chat_messages, chat_participants)))

    # doctors and nurses
    threads.append(Thread(target=doctors_nurses, args=(people[doctors_slice], people[nurses_slice])))

    # in patient directions
    threads.append(Thread(target=in_patient_directions, args=(people[patients_slice], people[doctors_slice])))

    # ambulance call
    threads.append(Thread(target=ambulance_calls_and_payment,
                          args=(people[patients_slice], paramedics_groups_ids, people[receptionists_slice])))

    # notice_board
    threads.append(Thread(target=create_and_populate_messages_and_modifications, args=(
        people[doctors_slice] + people[nurses_slice] + people[receptionists_slice] + people[paramedics_slice],
        notice_board_messages)))

    # sync threads
    run_and_wait_threads(threads)
