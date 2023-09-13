from app.calculations import add, subtract, multiply, divide, BankAccount
import pytest

@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(50)

@pytest.mark.parametrize("x, y, z", [
    (3,2,5),
    (5,4,9),
    (12,4,16)
])
def test_add(x, y, z):
    assert add(x, y) == z

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(5, 3) == 15

def test_divide():
    assert divide(5, 5) == 1

def test_bank_set_initial_amount():
    bank_account = BankAccount(50)
    assert bank_account.balance == 50

def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0

def test_bank_acount_withdraw(bank_account):
    bank_account.withdraw(20)
    assert bank_account.balance == 30

def test_bank_acount_deposit(bank_account):
    bank_account.deposit(20)
    assert bank_account.balance == 70

def test_bank_acount_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance, 5) == 55


@pytest.mark.parametrize("deposited, withdrew, balance", [
    (30,20,10),
    (500,40,460),
    (120,40,80)
])
def test_bank_transaction(zero_bank_account, deposited, withdrew, balance):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == balance