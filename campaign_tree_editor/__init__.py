from campaign_tree_editor import config, campaign_tree, views

MARA_CONFIG_MODULES = [config]

MARA_CLICK_COMMANDS = []

MARA_AUTOMIGRATE_SQLALCHEMY_MODELS = [campaign_tree.CampaignTree]

MARA_FLASK_BLUEPRINTS = [views.blueprint]

MARA_NAVIGATION_ENTRY_FNS = [views.navigation_entry]

MARA_ACL_RESOURCES = [views.acl_resource]