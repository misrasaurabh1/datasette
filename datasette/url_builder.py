from .utils import tilde_encode, path_with_format, PrefixedUrlString
import urllib


class Urls:
    def __init__(self, ds):
        self.ds = ds
        # Cache base_url for faster repeated access
        self._base_url = ds.setting("base_url")

    def path(self, path, format=None):
        # Fast path for PrefixedUrlString -- avoids unnecessary processing
        if isinstance(path, PrefixedUrlString):
            result_path = path
        else:
            # Strip only first "/" if present (avoid slice if not needed)
            if path and path[0] == "/":
                path = path[1:]
            result_path = self._base_url + path

        # Only call path_with_format when format is provided and not None
        if format is not None:
            # Only convert to string if needed
            if not isinstance(result_path, str):
                result_path = str(result_path)
            result_path = path_with_format(path=result_path, format=format)
        # Ensure we only ever call PrefixedUrlString if it's not already the right type
        if not isinstance(result_path, PrefixedUrlString):
            result_path = PrefixedUrlString(result_path)
        return result_path

    def instance(self, format=None):
        return self.path("", format=format)

    def static(self, path):
        return self.path(f"-/static/{path}")

    def static_plugins(self, plugin, path):
        return self.path(f"-/static-plugins/{plugin}/{path}")

    def logout(self):
        return self.path("-/logout")

    def database(self, database, format=None):
        db = self.ds.get_database(database)
        # tilde_encode always returns str
        encoded_route = tilde_encode(db.route)
        return self.path(encoded_route, format=format)

    def database_query(self, database, sql, format=None):
        db_path = self.database(database)
        # Avoid string concatenation in Python by formatting only once
        path = f"{db_path}/-/query?sql={urllib.parse.quote_plus(sql)}"
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
