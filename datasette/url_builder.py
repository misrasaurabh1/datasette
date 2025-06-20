from .utils import tilde_encode, path_with_format, PrefixedUrlString
import urllib


class Urls:
    def __init__(self, ds):
        self.ds = ds
        # Cache base_url to avoid repeated dict lookups.
        self._base_url = ds.setting("base_url")

    def path(self, path, format=None):
        is_prefixed = isinstance(path, PrefixedUrlString)
        if not is_prefixed:
            # Fast-path: remove leading slash if present and prepend base_url
            if path and path[0] == "/":
                path = path[1:]
            # Reuse cached base_url string
            path = f"{self._base_url}{path}"

        if format is not None:
            # Avoid passing arguments that are None (for slightly faster function calls)
            path = path_with_format(path=path, format=format)

        # Only wrap if not already
        if not is_prefixed:
            return PrefixedUrlString(path)
        return path

    def instance(self, format=None):
        return self.path("", format=format)

    def static(self, path):
        # Inline the string formatting to avoid function call overhead
        return self.path(f"-/static/{path}")

    def static_plugins(self, plugin, path):
        return self.path(f"-/static-plugins/{plugin}/{path}")

    def logout(self):
        return self.path("-/logout")

    def database(self, database, format=None):
        db = self.ds.get_database(database)
        return self.path(tilde_encode(db.route), format=format)

    def database_query(self, database, sql, format=None):
        path = f"{self.database(database)}/-/query?" + urllib.parse.urlencode({"sql": sql})
        return self.path(path, format=format)

    def table(self, database, table, format=None):
        path = f"{self.database(database)}/{tilde_encode(table)}"
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def query(self, database, query, format=None):
        path = f"{self.database(database)}/{tilde_encode(query)}"
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def row(self, database, table, row_path, format=None):
        path = f"{self.table(database, table)}/{row_path}"
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def row_blob(self, database, table, row_path, column):
        return self.table(database, table) + "/{}.blob?_blob_column={}".format(row_path, urllib.parse.quote_plus(column))
