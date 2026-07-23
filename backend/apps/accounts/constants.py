INTERNAL_SUPERADMIN_GROUP = "internal_superadmin"
INTERNAL_ADMIN_GROUP = "internal_admin"
EXTERNAL_SUPERADMIN_GROUP = "external_superadmin"
EXTERNAL_ADMIN_GROUP = "external_admin"

ROLE_TO_GROUP = {
    "internal_superadmin": INTERNAL_SUPERADMIN_GROUP,
    "internal_admin": INTERNAL_ADMIN_GROUP,
    "external_superadmin": EXTERNAL_SUPERADMIN_GROUP,
    "external_admin": EXTERNAL_ADMIN_GROUP,
}

ALL_ROLE_GROUPS = (
    INTERNAL_SUPERADMIN_GROUP,
    INTERNAL_ADMIN_GROUP,
    EXTERNAL_SUPERADMIN_GROUP,
    EXTERNAL_ADMIN_GROUP,
)

# Removed from the product; sync_role_groups deletes these if they still exist.
LEGACY_ROLE_GROUPS_TO_DELETE = ("external_partner_admin",)
