# Django config package initialization
# Ensure MySQL 8.0.x compatibility (SAD Section 3.6 with MySQL 8.0 Server)
try:
    from django.db.backends.mysql.features import DatabaseFeatures
    DatabaseFeatures.minimum_database_version = property(
        lambda self: (10, 11) if self.connection.mysql_is_mariadb else (8, 0)
    )
except ImportError:
    pass

