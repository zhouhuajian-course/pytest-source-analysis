import pytest

class_students = ['xiaoming', 'xiaohong', 'xiaohei']


def test_xiaoming_in_class():
    assert 'xiaoming' in class_students


class Fruit:
    def __init__(self, name):
        self.name = name
        self.cubed = False

    def cube(self):
        self.cubed = True


class FruitSalad:
    def __init__(self, *fruit_bowl):
        self.fruit = fruit_bowl
        self._cube_fruit()

    def _cube_fruit(self):
        for fruit in self.fruit:
            fruit.cube()


@pytest.fixture
def fruit_bowl():
    return [Fruit("apple"), Fruit("banana")]


def test_fruit_salad(fruit_bowl):
    fruit_salad = FruitSalad(*fruit_bowl)
    assert all(fruit.cubed for fruit in fruit_salad.fruit)


@pytest.fixture
def first_entry():
    return "a"


@pytest.fixture
def order(first_entry):
    return [first_entry]


def test_string(order):
    order.append("b")
    assert order == ["a", "b"]


def test_int(order):
    order.append(2)
    assert order == ["a", 2]


@pytest.fixture
def second_entry():
    return 2


@pytest.fixture
def order2(first_entry, second_entry):
    return [first_entry, second_entry]


@pytest.fixture
def expected_list():
    return ["a", 2, 3.0]


def test_string2(order2, expected_list):
    order2.append(3.0)
    assert order2 == expected_list


@pytest.fixture
def order3():
    return []


@pytest.fixture
def append_first(order3, first_entry):
    return order3.append(first_entry)


def test_string_only(append_first, order3, first_entry):
    assert order3 == [first_entry]


@pytest.fixture
def order4(first_entry):
    return []


@pytest.fixture(autouse=True)
def append_first4(order4, first_entry):
    return order4.append(first_entry)


def test_string_only4(order4, first_entry):
    assert order4 == [first_entry]


def test_string_and_int(order4, first_entry):
    order4.append(2)
    assert order4 == [first_entry, 2]


def determine_scope(fixture_name, config):
    if config.getoption("--keep-containers", None):
        return "session"
    return "function"


def spawn_container():
    pass


@pytest.fixture(scope=determine_scope)
def docker_container():
    yield spawn_container()


class MailAdminClient:
    def create_user(self):
        return MailUser()

    def delete_user(self, user):
        # do some cleanup
        pass


class MailUser:
    def __init__(self):
        self.inbox = []

    def send_email(self, email, other):
        other.inbox.append(email)

    def clear_mailbox(self):
        self.inbox.clear()


class Email:
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body


@pytest.fixture
def mail_admin():
    return MailAdminClient()


@pytest.fixture
def sending_user(mail_admin):
    user = mail_admin.create_user()
    yield user
    mail_admin.delete_user(user)


@pytest.fixture
def receiving_user(mail_admin):
    user = mail_admin.create_user()
    yield user
    user.clear_mailbox()
    mail_admin.delete_user(user)


def test_email_received(sending_user, receiving_user):
    email = Email(subject="Hey!", body="How's it going?")
    sending_user.send_email(email, receiving_user)
    assert email in receiving_user.inbox





@pytest.fixture
def receiving_user2(mail_admin, request):
    user = mail_admin.create_user()

    def delete_user():
        mail_admin.delete_user(user)

    request.addfinalizer(delete_user)
    return user


@pytest.fixture
def email2(sending_user, receiving_user2, request):
    _email = Email(subject="Hey!", body="How's it going?")
    sending_user.send_email(_email, receiving_user2)

    def empty_mailbox():
        receiving_user2.clear_mailbox()

    request.addfinalizer(empty_mailbox)
    return _email


def test_email_received(receiving_user2, email2):
    assert email2 in receiving_user2.inbox


if __name__ == '__main__':
    # pytest.main()
    pytest.main(['-q'])
