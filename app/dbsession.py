import os
from db import DatabaseError
from flask.sessions import SessionInterface, SessionMixin

_DEFAULT_SESSION_DURATION = '30 MINUTES'


class Session(dict, SessionMixin):

    def __init__(self, id, expires, userid=None, key_vals=None):
        super().__init__()
        self.id = id
        self.expires = expires
        self.userid = userid
        if key_vals:
            self.update(key_vals)


class DBSessionInterface(SessionInterface):

    def open_session(self, app, request) -> Session:
        session_id = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        s = None
        conn = None
        try:
            conn = app.db_pool.getconn()
            clean_expired_sessions(conn)  # could be run out of band in a separate process
            with conn.cursor() as cursor:
                if session_id:
                    cursor.execute("SELECT userid, expires, key_vals FROM sessions WHERE id = %s", (session_id,))
                    row = cursor.fetchone()
                    if row:
                        s = Session(session_id, row[0], row[1], row[2])

                if not s:  # no session_id or session_id returns no rows
                    sesdur = os.environ.get(app.config['SESSION_COOKIE_NAME'], _DEFAULT_SESSION_DURATION)
                    cursor.execute("INSERT INTO sessions (expires) VALUES (now() + %s) RETURNING id, expires", (sesdur,))
                    row = cursor.fetchone()
                    if row:
                        s = Session(row[0], row[1])
        finally:
            if conn:
                app.db_pool.putconn(conn)
        return s

    def save_session(self, app, session: Session, response):
        conn = None
        params = {
            'id': session.id,
            'sesdur': os.environ.get(app.config['SESSION_COOKIE_NAME'], _DEFAULT_SESSION_DURATION),
            'userid': session.userid,
            'key_vals': session.items()
        }
        try:
            conn = app.db_pool.getconn()
            with conn.cursor() as cursor:

                if session.id:
                    cursor.execute("""
                        INSERT INTO sessions (id, expires, userid, key_vals)
                            VALUES (%(id)s, now() + %(sesdur)s, %(userid)s, %(key_vals)s)
                        ON CONFLICT DO UPDATE SET
                            expires = now() + %(sesdur)s,
                            userid = %(userid)s,
                            key_vals = %(key_vals)s
                            WHERE id = %(id)s
                        RETURNING expires
                    """, params)
                    row = cursor.fetchone()
                    if row:
                        session.expires = row[0]
                    else:
                        raise DatabaseError('No row returned from execute')

                else:  # session doesn't have an id (unlikely)
                    cursor.execute("""
                        INSERT INTO sessions (expires, userid, key_vals)
                            VALUES (now() + %(sesdur)s, %(userid)s, %(key_vals)s)
                            RETURNING id, expires
                    """, params)
                    row = cursor.fetchone()
                    if row:
                        session.id = row[0]
                        session.expires = row[1]
                    else:
                        raise DatabaseError('No row returned from execute')

            # Always set the session cookie with the updated epiration if we made it this far
            response.set_cookie(app.config['SESSION_COOKIE_NAME'], session.id, expires=session.expires, httponly=True)

        finally:
            if conn:
                app.db_pool.putconn(conn)


def clean_expired_sessions(conn):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM sessions WHERE expires > now()")
