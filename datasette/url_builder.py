from .utils import tilde_encode, path_with_format, PrefixedUrlString
import urllib


class Urls:
    def __init__(self, ds):
        self.ds = ds
        self._base_url = ds.setting("base_url")

    def path(self, path, format=None):
        # Optimize: Avoid unnecessary instance checks/string concatenations
        if not isinstance(path, PrefixedUrlString):
            # lstrip is faster and avoids always checking `startswith`
            path = path.lstrip("/")
            path = self._base_url + path
        if format is not None:
            # Avoids unnecessary keyword arguments
            path = path_with_format(path=path, format=format)
        return PrefixedUrlString(path)

    def instance(self, format=None):
        return self.path("", format=format)

    def static(self, path):
        return self.path(f"-/static/{path}")

    def static_plugins(self, plugin, path):
        # Optimize: f-strings are already fast, but avoid extra str concatenations by combining inline
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
