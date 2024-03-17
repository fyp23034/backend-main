import universal.logic as logic
import pytest

testUser = "654279c91f4bb5264eb7303d"

def test_integration():
    assert logic.health() == "OK"

def test_categorise(emailIdStr):
    logic.regUser(testUser)
    result = logic.emailCategory(emailIdStr)
    assert isinstance(result, int)

def test_NLR():
    logic.regUser(testUser)
    assert logic.userNLR("abc") == True

def test_whitelist():
    logic.regUser(testUser)
    assert logic.addToWhiteList("abc@gmail.com") == True