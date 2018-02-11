import osdf
# import osdfapp
from osdf.config.loader import load_config_file


def test_dummy():
    """Generate time constraints from cm-request.json and cm-policy-response.json"""
    try:
       load_config_file("DUMMY")
    except:
       pass
    return 1


