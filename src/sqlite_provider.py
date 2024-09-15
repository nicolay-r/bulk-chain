import sqlite3


class SQLiteProvider(object):

    @staticmethod
    def __create_table(table_name, columns, id_column_name,
                       id_column_type, sqlite3_column_types, cur):

        # Provide the ID column.
        sqlite3_column_types = [id_column_type] + sqlite3_column_types

        # Compose the whole columns list.
        content = ", ".join([" ".join(item) for item in zip(columns, sqlite3_column_types)])
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name}({content})")
        cur.execute(f"CREATE INDEX IF NOT EXISTS i_id ON {table_name}({id_column_name})")

    @staticmethod
    def write_auto(data_it, target, data2col_func, table_name, id_column_name="id",
                   id_column_type="INTEGER"):
        """ NOTE: data_it is an iterator of dictionaries.
            This implementation automatically creates the table and
        """
        with sqlite3.connect(target) as con:
            cur = con.cursor()

            columns = None
            for data in data_it:
                assert(isinstance(data, dict))

                # Extracting columns from data.
                row_columns = list(data.keys())
                assert(id_column_name in row_columns)

                # Optionally create table.
                if columns is None:

                    # Setup list of columns.
                    columns = row_columns
                    # Place ID column first.
                    columns.insert(0, columns.pop(columns.index(id_column_name)))

                    SQLiteProvider.__create_table(
                        columns=columns, table_name=table_name, cur=cur,
                        id_column_name=id_column_name, id_column_type=id_column_type,
                        sqlite3_column_types=["TEXT"] * len(columns))

                # Check that each rows satisfies criteria of the first row.
                [Exception(f"{column} is expected to be in row!") for column in row_columns if column not in columns]

                uid = data[id_column_name]
                r = cur.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {id_column_name}='{uid}');")
                ans = r.fetchone()[0]
                if ans == 1:
                    continue

                params = ", ".join(tuple(['?'] * (len(columns))))
                row_columns_str = ", ".join(row_columns)
                cur.execute(f"INSERT INTO {table_name}({row_columns_str}) VALUES ({params})",
                            [data2col_func(c, data) for c in row_columns])
                con.commit()

            cur.close()

    @staticmethod
    def read(target, column_names=None, table="content"):
        with sqlite3.connect(target) as conn:
            cursor = conn.cursor()
            cols = "*" if column_names is None else ",".join(column_names)
            cursor.execute(f"SELECT {cols} FROM {table}")
            for row in cursor:
                yield row
                
    @staticmethod
    def get_columns(target, table="content"):
        with sqlite3.connect(target) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            return [row[1] for row in cursor.fetchall()]