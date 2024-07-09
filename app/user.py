from dataclasses import dataclass
from argon2 import PasswordHasher
from .db import DatabaseError

_hasher = PasswordHasher()


@dataclass
class User:
    """Class representing user data."""
    id: int
    email: str
    pw_hash: str
    first_name: str
    last_name: str
    active: bool

    def set_pw_hash(self, password: str):
        self.pw_hash = _hasher.hash(password)

    def password_valid(self, password: str) -> bool:
        return _hasher.verify(self.pw_hash, password)

    def reload(self, conn):
        row = _get_user_data(conn, self.id)
        if row:
            self.email = row[0]
            self.pw_hash = row[1]
            self.first_name = row[2]
            self.last_name = row[3]
            self.active = row[4]
        else:
            raise DatabaseError("No rows returned from database.")

    def save(self, conn):
        with conn:
            with conn.cursor() as cursor:
                if self.id:
                    cursor.execute("""
                        UPDATE users SET 
                            email = %(email)s, 
                            password = %(pw_hash)s, 
                            firstname = %(first_name)s, 
                            lastname = %(last_name)s, 
                            active = %(active)s
                        WHERE id = %(id)s
                    """, self)
                else:  # no id yet, must be new
                    cursor.execute("""
                        INSERT INTO users (email, password, firstname, lastname, active)
                        VALUES (%(email)s, %(pw_hash)s, %(first_name)s, %(last_name)s, %(active)s)
                        RETURNING id
                    """, self)
                    row = cursor.fetchone()
                    if row:
                        self.id = row[0]
                    else:
                        raise DatabaseError("New ID not returned from insert.")


def load_user(conn, id) -> User | None:
    row = _get_user_data(conn, id)
    if row:
        return User(id, email=row[0], pw_hash=row[1], first_name=row[2], last_name=row[3], active=row[4])
    else:
        return None


def login_user(conn, email, password) -> User | None:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id,  password, firstname, lastname, active
            FROM users
            WHERE email = %s
        """, (email,))
        row = cursor.fetchone()
        if row:
            user = User(id=row[0], email=email, pw_hash=row[1], first_name=row[2], last_name=row[3], active=row[4])
            if user.password_valid(password):
                return user
        return None


def _get_user_data(conn, id):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT email, password, firstname, lastname, active 
            FROM users 
            WHERE id = %s
        """, (id,))
        return cursor.fetchone()


