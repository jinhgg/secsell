class Config:
    DEBUG = False
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ljh:123@148.70.210.16:3306/secsell'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
