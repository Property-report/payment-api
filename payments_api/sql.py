from payments_api import db
from sqlalchemy import create_engine
from payments_api.models import PaymentUser
from sqlalchemy.orm import sessionmaker
from payments_api import config


class Sql:

    # create a Session
    session = db.session


#start of search sql statements
    def get_user(params):
        variable= Sql.session.query(PaymentUser).filter_by(**params).all()
        Sql.session.commit()
        return variable

#start of insert sql statments
    def new_user(params):
        new_user = PaymentUser(**params)
        Sql.session.add(new_user)
        Sql.session.commit()
        return Sql.get_user(new_user.to_dict())

#start of update sql statments
    def update_user(id, params):
        updating = Sql.session.query(PaymentUser).get(id)
        for key, value in params.items():
            setattr(updating, key, value)
        Sql.session.commit()
        return Sql.get_user({'id':id})

    def delete_user(id):
        Sql.session.query(PaymentUser).filter(PaymentUser.id == id).delete()
        Sql.session.commit()
        return "deleted"

db.engine.dispose()
