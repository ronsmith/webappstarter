import os
import logging
import json
from .db import DatabaseError
from flask.sessions import SessionInterface, SessionMixin

_DEFAULT_SESSION_DURATION = '30 MINUTES'

_logger = logging.getLogger(__name__)


class Session(dict, SessionMixin):

    def __init__(self, id, expires, userid=None, key_vals=None):
        super().__init__()
        self.id = id
        self.expires = expires
        self.userid = userid
        if key_vals:
            self.update(key_vals)

    def replace_key_vals(self, new_key_vals):
        self.clear()
        self.update(new_key_vals)


class DBSessionInterface(SessionInterface):

    def open_session(self, app, request) -> Session | None:
        if request.path.startswith('/static') or request.path.startswith('/favicon'):
            return None

        session_id = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        _logger.debug(f'got request cookie {app.config['SESSION_COOKIE_NAME']}={session_id}')

        s = None
        conn = None

        try:
            conn = app.db_pool.getconn()
            clean_expired_sessions(conn)  # could be run out of band in a separate process
            with conn:
                with conn.cursor() as cursor:
                    if session_id:
                        cursor.execute("""
                            SELECT expires, userid, key_vals 
                            FROM sessions 
                            WHERE id = %s
                        """, (session_id,))
                        row = cursor.fetchone()
                        if row:
                            s = Session(session_id, expires=row[0], userid=row[1])
                            s.replace_key_vals(row[2])
                            _logger.debug(f'opening existing session ID {s.id}')
                        else:
                            _logger.debug(f'No session found for ID {session_id}')

                    # s will be None if no session_id or session_id returns no rows
                    # Must use "is None" because "not s" returns true when the dict is empty
                    if s is None:
                        sesdur = os.environ.get(app.config['SESSION_COOKIE_NAME'], _DEFAULT_SESSION_DURATION)
                        cursor.execute("""
                            INSERT INTO sessions (expires) 
                                VALUES (now() + INTERVAL %s) 
                                RETURNING id, expires
                        """, (sesdur,))
                        row = cursor.fetchone()
                        if row:
                            s = Session(id=row[0], expires=row[1])
                            _logger.debug(f'opening new session with ID {s.id}')
                        else:
                            raise DatabaseError("No row returned from execute")
        finally:
            if conn:
                app.db_pool.putconn(conn)

        _logger.debug(f'open_session returning session ID {s.id}')
        return s

    def save_session(self, app, session: Session, response):
        conn = None
        params = {
            'id': session.id,
            'sesdur': os.environ.get(app.config['SESSION_COOKIE_NAME'], _DEFAULT_SESSION_DURATION),
            'userid': session.userid,
            'key_vals': json.dumps(session)
        }
        try:
            with app.db_pool.getconn() as conn:
                with conn.cursor() as cursor:

                    if session.id:
                        cursor.execute("""
                            INSERT INTO sessions (id, expires, userid, key_vals)
                                VALUES (%(id)s, now() + %(sesdur)s, %(userid)s, %(key_vals)s)
                            ON CONFLICT (id) DO UPDATE SET
                                expires = now() + INTERVAL %(sesdur)s,
                                userid = %(userid)s,
                                key_vals = %(key_vals)s
                            RETURNING expires
                        """, params)
                        row = cursor.fetchone()
                        if row:
                            session.expires = row[0]
                            _logger.debug(f'saved existing session ID {session.id}')
                        else:
                            raise DatabaseError('No row returned from execute')

                    else:  # session doesn't have an id (unlikely)
                        cursor.execute("""
                            INSERT INTO sessions (expires, userid, key_vals)
                                VALUES (now() + INTERVAL %(sesdur)s, %(userid)s, %(key_vals)s)
                                RETURNING id, expires
                        """, params)
                        row = cursor.fetchone()
                        if row:
                            session.id = row[0]
                            session.expires = row[1]
                            _logger.debug(f'saved new session ID {session.id}')
                        else:
                            raise DatabaseError('No row returned from execute')

            # Always set the session cookie with the updated epiration if we made it this far
            response.set_cookie(
                key=app.config['SESSION_COOKIE_NAME'],
                value=session.id,
                httponly=True,
                secure=False,   # should be secure in production
                samesite='Lax')
            _logger.debug(f'set response cookie {app.config['SESSION_COOKIE_NAME']}={session.id}')

        finally:
            if conn:
                app.db_pool.putconn(conn)


def clean_expired_sessions(conn):
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM sessions WHERE now() > expires")
