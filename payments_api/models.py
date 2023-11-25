from payments_api import db
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import relationship
from datetime import datetime
import datetime

class PaymentUser(db.Model):
    __tablename__ = 'paymentuser'

    id = db.Column(db.Integer, primary_key=True)
    client_reference_id = db.Column(db.String(64))
    stripe_user_id = db.Column(db.String(64))
    email = db.Column(db.String(64))
    creation_time = db.Column(db.String(64))
    currency = db.Column(db.String(64))
    delinquent = db.Column(db.String(64))
    description = db.Column(db.String(64))
    account_balance = db.Column(db.String(64))
    paid_type = db.Column(db.String(64))
    company_id = db.Column(db.Integer)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
          "id": self.id,
          "stripe_user_id": self.stripe_user_id,
          "email": self.email,
          "creation_time": self.creation_time,
          "currency": self.currency,
          "delinquent": self.delinquent,
          "description": self.description,
          "account_balance" : self.account_balance,
          "paid_type" : self.paid_type,
          "company_id": self.company_id,
          "client_reference_id" : self.client_reference_id

        }

