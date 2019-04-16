
def MARA_CONFIG_MODULES():
    from . import config
    return [config]

def MARA_CLICK_COMMANDS():
    return []

def MARA_AUTOMIGRATE_SQLALCHEMY_MODELS():
    from . import campaign_tree
    return [campaign_tree.CampaignTree]


def MARA_FLASK_BLUEPRINTS():
    from . import views
    return [views.blueprint]


def MARA_NAVIGATION_ENTRIES():
    from . import views
    return [views.navigation_entry()]


def MARA_ACL_RESOURCES():
    from . import views
    return [views.acl_resource]
