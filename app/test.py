from omegaconf import OmegaConf
from datetime import datetime
from app.model import Account, User, Bank
from app.infrastructure import Producer

conf = OmegaConf.load("config.yaml")
kafka = Producer.from_conf("test", conf.kafka, conf.logs)

acc = Account(
    user_id="usrID",
    bank_id="bnkID",
    account_type="accTYPE",
    balance=2)
acc.submit(kafka, conf.entities[2].source.topics[0])

usr = User(
    name = "usrNAME",
    email = "usrEMAIL",
    ssn = "usrSSN",
    birthdate = datetime.now().date(),
    registration_date = datetime.now().date()
)
usr.submit(kafka, conf.entities[1].source.topics[0])

bnk = Bank(
    name = "bnkNAME",
    phone = "bnkPHONE",
    address = "bnkADDRESS"
)
bnk.submit(kafka, conf.entities[0].source.topics[0])
