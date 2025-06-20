from .utils import tilde_encode, path_with_format, PrefixedUrlString
import urllib


class Urls:
    def __init__(self, ds):
        self.ds = ds
        # Cache base_url to avoid repeated .setting() lookups
        self._base_url = ds.setting("base_url")

    def path(self, path, format=None):
        # Fast-path for most cases
        if not isinstance(path, PrefixedUrlString):
            # Only slice if leading "/" is present
            if path and path[0] == "/":
                path = path[1:]
            path = self._base_url + path
        if format is not None:
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def instance(self, format=None):
        # No optimization possible; required to call self.path
        return self.path("", format=format)

    def static(self, path):
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
