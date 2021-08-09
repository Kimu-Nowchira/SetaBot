import psycopg2
import sqlite3
from config import Config

from . import logger


class SetaSQL:
    dbtype: str = None
    path: str = None

    def __init__(self, sqlite_path: str = False, table: str = None):
        if not sqlite_path:
            # sqlite_path 미입력시 지정된 pgSQL Database로 연결
            self.conn = psycopg2.connect(
                dbname=Config.DBNAME,
                user=Config.USERNAME,
                password=Config.PASSWORD,
                port=Config.PORT
            )
            self.dbtype = 'pgsql'
        else:
            self.conn = sqlite3.connect(
                sqlite_path,
                check_same_thread=False
            )
            self.dbtype = 'sqlite/' + sqlite_path
            self.path = sqlite_path
        self.cur = self.conn.cursor()
        self.table = table

    def __str__(self) -> str:
        return self.dbtype

    def select(self, table: str = None, rec: list = [], **kwargs) -> list:
        '''
        < EXAMPLE >  db.select('table', 'col1, col2', order_by='col1')
        < RETURN >  [{'col1': 'val1', 'col2': 'val2'}, ...]
        '''

        # 테이블이 지정되지 않은 경우
        if table is None:
            if self.table is not None:
                table = self.table
            else:
                raise NotDesignatedData
        if not rec:
            raise NotDesignatedData

        recs = ', '.join(rec)
        rule = ''
        for col in kwargs.keys():
            rule += col.upper().replace('_', ' ') + \
                ' ' + str(kwargs[col]) + ' '
        data = self.query(
            f'SELECT {recs} FROM {table} {rule}', reading=True, commit=False)
        # logger.debug(data)

        result = []
        for row in data:
            row_data = {}
            for idx, val in enumerate(rec):
                row_data[val] = row[idx]
            result.append(row_data)

        return result

    def selectone(self, table: str = None, rec: list = [], **kwargs):
        res = self.select(table=table, rec=rec, **kwargs, limit=1)
        if not res:
            return None
        else:
            return res[0]

    def insert(self, table: str = None, commit: bool = True, **kwargs):
        '''
        < EXAMPLE >  db.insert('table', col1='val1', col2='val2')
        '''
        # 테이블이 지정되지 않은 경우
        if table is None:
            if self.table is not None:
                table = self.table
            else:
                raise NotDesignatedData

        vals = []
        for val in kwargs.values():
            if isinstance(val, int):
                vals.append(str(val))
            else:
                rval = str(val)
                rval = rval.replace("'", "''")
                rval = rval.replace("\"", "\"\"")
                vals.append(f"'{rval}'")

        cols = ', '.join(kwargs.keys())
        vals = ', '.join(vals)

        self.query(
            f'INSERT INTO {table} ({cols}) VALUES ({vals})', commit=commit)

    def update(self, table: str = None, commit: bool = True, **kwargs):
        '''
        < EXAMPLE >  db.update('table', col1='val1', col2='val2')
        '''
        # TODO where이 문제가 있음
        # 테이블이 지정되지 않은 경우
        if table is None:
            if self.table is not None:
                table = self.table
            else:
                raise NotDesignatedData

        where = kwargs['where']
        del kwargs['where']

        vals = []
        for val in kwargs.values():
            if isinstance(val, int):
                vals.append(str(val))
            else:
                rval = str(val)
                rval = rval.replace("'", "''")
                rval = rval.replace("\"", "\"\"")
                vals.append(f"'{rval}'")

        cols = list(kwargs.keys())
        cols = ', '.join(cols)
        vals = ', '.join(vals)

        self.query(
            f"UPDATE {table} SET ({cols}) = ({vals}) WHERE {where}", commit=commit)

    def delete(self, table: str, rule: str):
        # 테이블이 지정되지 않은 경우
        if table is None:
            if self.table is not None:
                table = self.table
            else:
                raise NotDesignatedData
        self.query(f"DELETE FROM {table} WHERE {rule}")

    def exists(self, table: str, rule: str = ''):
        '''
        설명 : 조건에 맞는 행이 있는 지의 여부(True, False)를 반환함
        is_sql(테이블명, 조건, DB 경로)

        ---- EXAMPLE ----
        > seta_sqlite.is_sql('테이블', "WHERE kimu=1", '키뮤.sql')
        '''
        return self.query(f'select exists(select * from {table} WHERE {rule})', True)[0][0]

    def query(self, qur, reading=False, commit=True):
        '''
        설명 : SQL문을 사용함
        sql(SQL쿼리, DB 경로, writing)

        ※ reading
        reading True이면 fetchall로 결과를 반환
        reading False이면 결과를 반환하지 않고 commit함.
        '''
        logger.debug(qur)
        try:
            self.cur.execute(qur)
        except Exception as e:
            print(f'[오류] {e}')
            # logger.err(e)

        if reading:
            return self.cur.fetchall()
        elif commit:
            self.conn.commit()

    def commit(self):
        self.conn.commit()


class NotDesignatedData(Exception):
    def __init__(self):
        super().__init__('필요한 값이 지정되지 않았습니다.')
