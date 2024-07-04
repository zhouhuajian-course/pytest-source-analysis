import smtplib
import pytest


# @pytest.fixture(scope="function")
@pytest.fixture(scope="module")
def smtp_connection():
    # return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
    return smtplib.SMTP_SSL("smtp.126.com", 465, timeout=5)


@pytest.fixture(scope="session")
def smtp_connection2():
    # the returned fixture value will be shared for
    # all test2 requesting it
    return smtplib.SMTP_SSL("smtp.126.com", 465, timeout=5)


