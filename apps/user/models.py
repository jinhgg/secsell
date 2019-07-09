from flask_login import UserMixin
from sqlalchemy import Column, DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT, TINYINT
from werkzeug.security import check_password_hash

from apps import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(INTEGER(11), primary_key=True)
    email = Column(String(64), unique=True, index=True)
    password_hash = Column(String(128))

    def verify_password(self, password):
        t = check_password_hash(self.password_hash, password)
        return t

    def __repr__(self):
        return '<User {}>'.format(self.email)


class BlackUser(db.Model):
    __tablename__ = 'blackuser'
    user_id = Column(INTEGER(11), index=True, primary_key=True)
    status = Column(String(1), nullable=False, index=True, default='1')
    lockdate = Column(DateTime)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
