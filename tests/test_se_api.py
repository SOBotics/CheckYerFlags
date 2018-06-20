from flagbot import se_api

def test_se_api():
    api = se_api.se_api("K8pani4F)SeUn0QlbHQsbA((")
    assert api.get_user(1) is not None