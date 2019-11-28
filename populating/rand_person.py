from faker import Faker
from faker.providers import BaseProvider
import hashlib

fake = Faker()


class Provider(BaseProvider):
    def insurance(self):
        return self.random_element(elements=('AK-BARS', None, 'SOGAZ-MED', 'VTB STRAHOVANIE'))

    def schedule_type(self):
        return self.random_element(elements=('2/3', '0', '1'))

    def chat_type(self):
        return self.random_element(elements=('private', 'channel', 'group'))

    def specialization(self):
        return self.random_element(elements=('Traumatologist', 'Surgeon', 'Oculist', 'Therapist'))

    def position(self):
        return self.random_element(elements=('Primary', 'Secondary'))

    def change_type(self):
        return self.random_element(elements=('Addition', 'Removal', 'Modification', 'Creation'))

    def payment_type(self):
        return self.random_element(elements=('Cash', 'Card'))

    def analysis_type(self):
        return self.random_element(elements=('Blood', 'Urine', 'Fecal'))

    def medical_record_content(self):
        return self.random_element(elements=('better check him again', 'good', 'the best'))

    def item_request_status(self):
        return self.random_element(elements=('Approved', 'Rejected', 'Pending'))


fake.add_provider(Provider)


class Get:
    def __getitem__(self, item):
        return self.__dict__[item]


class Person(Get):
    def __init__(self):
        profile = fake.profile(fields=None, sex=None, )
        first, last = fake.first_name(), fake.last_name()
        self.first_name = first
        self.last_name = last
        self.email = (first.lower() + last.lower() + "@" + fake.free_email_domain()).replace(" ", "")
        self.birth_date = fake.date_time_between(start_date="-100y", end_date="-30y", tzinfo=None)
        self.hash_pass = hashlib.sha256((first + last).encode()).hexdigest()
        self.insurance_company = fake.insurance()
        self.insurance_number = profile['ssn'] if self.insurance_company else None
        self.payment_type = 'Insurance' if self.insurance_company else fake.payment_type()


class Staff(Get):
    def __init__(self):
        self.employment_start = fake.date_time_between(start_date="-10y", end_date="-10d", tzinfo=None)
        self.salary = fake.random_int(min=12000, max=42000, step=1000)
        self.schedule_type = fake.schedule_type()
        self.schedule_type = fake.schedule_type()
        self.specialization = fake.specialization()
        self.clinic_number = fake.random_int(min=100, max=400, step=11)
        self.position = fake.position()


class Chat(Get):
    def __init__(self):
        self.name = fake.word(ext_word_list=None)
        self.chat_type = fake.chat_type()


class Message(Get):
    def __init__(self):
        self.content = fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
        self.content_type = 'text'
        self.change_type = fake.change_type()
        self.datetime = fake.date_time_between(start_date="-30d", end_date="now", tzinfo=None)


if __name__ == '__main__':
    p = Person()
    for name in dir(p):
        if name.startswith("_"):
            continue
        print(name, p.__dict__[name])

    # print(dict(((key, value) for key, value in p.__dict__.items() if not key.startswith("_"))))
