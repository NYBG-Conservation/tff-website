INTERNAL_SUPERADMIN_GROUP = "internal_superadmin"
INTERNAL_ADMIN_GROUP = "internal_admin"
EXTERNAL_SUPERADMIN_GROUP = "external_superadmin"
EXTERNAL_ADMIN_GROUP = "external_admin"

# Legacy group name (pre-4-role model).
EXTERNAL_PARTNER_ADMIN_GROUP = "external_partner_admin"

ROLE_TO_GROUP = {
    "internal_superadmin": INTERNAL_SUPERADMIN_GROUP,
    "internal_admin": INTERNAL_ADMIN_GROUP,
    "external_superadmin": EXTERNAL_SUPERADMIN_GROUP,
    "external_admin": EXTERNAL_ADMIN_GROUP,
    "external_partner_admin": EXTERNAL_ADMIN_GROUP,
}

ALL_ROLE_GROUPS = (
    INTERNAL_SUPERADMIN_GROUP,
    INTERNAL_ADMIN_GROUP,
    EXTERNAL_SUPERADMIN_GROUP,
    EXTERNAL_ADMIN_GROUP,
    EXTERNAL_PARTNER_ADMIN_GROUP,
)
