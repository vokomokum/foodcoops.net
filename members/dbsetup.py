#!/usr/bin/env python
import os
import sys
from sqlalchemy import create_engine
from subprocess import Popen
import random
import datetime
import transaction
import ConfigParser

from members import models
from members.models.member import Member
from members.models.applicant import Applicant

from members.models.workgroups import Workgroup
from members.models.shift import Shift, shift_states
from members.models.transactions import Transaction
from members.models.transactions import TransactionType
#from members.models.orders import Order

from members.utils.md5crypt import md5crypt
from members.utils.misc import month_info

default_pwd = 'notsecret'
fakenames = 'scripts/fakenames.txt'

def addAdmin():
    '''
    after old names are added, he has ID 3
    '''
    admin = Member(fname=u'Adalbert', lname='Adminovic')
    admin.mem_email = 'admin@vokomokum.nl'
    admin.mem_mobile = "06" + unicode(random.randint(10000000, 100000000))
    admin.household_size = 1
    salt = md5crypt('notsecret', '') 
    admin.mem_enc_pwd = md5crypt('notsecret', salt)
    admin.mem_admin = True
    admin.mem_active = True
    DBSession.add(admin)
    DBSession.flush()
    wgs = DBSession.query(Workgroup).filter(Workgroup.name==u'Systems').first()
    wgs.members.append(admin)
    wgm = DBSession.query(Workgroup).filter(Workgroup.name==u'Membership').first()
    wgm.members.append(admin)
    

"""Ensure the backwards compatibility, these settings are used in unit tests"""
def addOldNames():
    m1 = Member(fname=u'Peter', prefix=u'de', lname='Pan')
    m1.mem_email = 'peter@gmail.com'
    m1.mem_enc_pwd = md5crypt('notsecret', 'notsecret')
    DBSession.add(m1)
    m2 = Member(fname=u'Hans', prefix=u'de', lname='Wit')
    m1.mem_email = 'hans@gmail.com'
    DBSession.add(m2)
    wg1 = Workgroup(name=u'Systems', desc=u'IT stuff')
    DBSession.add(wg1)
    wg2 = Workgroup(name=u'Besteling', desc=u'Besteling at wholesale')
    DBSession.add(wg2)
    DBSession.flush() # flush now to get member and workgroup IDs
    wg1.members.append(m1)
    wg1.leaders.append(m1)
    wg2.members.append(m1)
    wg2.members.append(m2)
    wg2.leaders.append(m2)
    DBSession.flush()
    s = Shift(wg2.id, 'do stuff', 2012, 6, member=m1)
    DBSession.add(s)
    DBSession.flush()
    

def createWGs():
    wgs = []
    wgs.append(Workgroup(name=u'Systems2', desc=u'IT stuff', required_members=3))
    wgs.append(Workgroup(name=u'Besteling2', desc=u'Besteling at wholesale', required_members=8))
    wgs.append(Workgroup(name=u'Cafe', desc=u'Cakes and coffee', required_members=14))
    wgs.append(Workgroup(name=u'Finance', desc=u'Making sure money is where it is supposed to be', required_members=8))
    wgs.append(Workgroup(name=u'Vers', desc=u'Fresh food!', required_members=14))
    wgs.append(Workgroup(name=u'Membership', desc=u'Human resources', required_members=4))
    for wg in wgs:
        DBSession.add(wg)
    DBSession.flush()
    return wgs
    

def fillDBRandomly(seed, workgroups):
    global default_pwd, fakenames
    if seed: random.seed(seed)
    now = datetime.datetime.now()
    mi = month_info(now.date())
    # read in the fakenames
    names = {}
    for l in file(fakenames, 'r'):
        fname,lname = l.strip().split()
        names[fname] = lname
    namelist = sorted(list(names.keys()))
    # 20% of the people are applicants
    members = []
    for l in namelist[int(len(namelist) * 0.2):]:
        m = Applicant(fname=l, lname=names[l])
        m.email = "%s-app@gmail.com"%(l)
        m.household_size = random.randint(1, 5)
        m.telnr = "06" + unicode(random.randint(10000000, 100000000))
        DBSession.add(m)
        # randomly select a number of workgroups m can be a member of
        DBSession.flush()
    # and the rest are members
    for l in namelist[:int(len(namelist) * 0.8)]:
        prefix = random.choice([u"de", u"van", u"voor", u"van den", u"te"])
        m = Member(fname=l, prefix=prefix, lname=names[l])
        m.mem_email = "%s@gmail.com" % (l)
        m.mem_enc_pwd = md5crypt(default_pwd, default_pwd)
        m.mem_mobile = "06" + unicode(random.randint(10000000, 100000000))
        m.household_size = random.randint(1, 5)
        m.mem_membership_paid = True
        if random.random() < 0.01:
            m.mem_membership_paid = False
        m.mem_active = True
        if random.random() < 0.05:
            m.mem_active = False
        m.mem_street = random.choice(namelist) + "street"
        m.mem_house = random.randint(1, 200)
        m.mem_postcode = "1000AB"
        m.city = "Amsterdam"
        DBSession.add(m)
        # randomly select a number of workgroups m can be a member of
        for wg in random.sample(workgroups, random.randint(1, len(workgroups))):
            wg.members.append(m)
            # randomly select if m is a leader of the workgroup: only 10 % of all members are leaders
            if random.random() < 0.1:
                wg.leaders.append(m)
        members.append(m)
        DBSession.flush()
    
    months = [(mi.prev_month, mi.prev_year), (now.month, now.year),
              (mi.next_month, mi.next_year)]
    # next step: create 50 new shifts in each wg with random state/description
    for wg in workgroups:
        for i in range(50):
            task = random.choice(["clean", "buy", "feed", "fill", "write",
                                  "do", "play", "sleep"])
            month = random.choice(months)
            s = Shift(wg.id, task, month[1], month[0], day=random.randint(1,30))    
            s.state = random.choice(shift_states)
            if not s.state == 'open':
                s.member = random.choice(wg.members)
            DBSession.add(s)
        DBSession.flush()
                
    # Finally: create 20 transactions per member
    #ttype = DBSession.query(TransactionType).filter(TransactionType.name=='Order Charge').first()
    #orders = DBSession.query(Order).all()
    #for m in members:
    #    for i in range(20):
    #        month = random.choice(months)
    #        t = Transaction(ttype_id=ttype.id, amount=random.random() * 150,
    #                        date=datetime.datetime(month[1], month[0],
    #                              random.randint(1, 28)), mem_id=m.mem_id)
    #        t.ttype = ttype
    #        t.member = m
    #        if ttype.pos_neg == 'neg':
    #            t.amount *= -1
    #        if ttype.name == 'Order Charge':
    #            o = random.choice(orders)
    #            t.ord_no = o.id
    #            t.order = o 
    #        t.validate()
    #        DBSession.add(t)
    #    DBSession.flush()


def main():
    global DBSession

    # initalise database with some external data the members app relies on
    password = os.getenv('MEMBERS_DB_PASSWORD')
    Popen('mysql -h mariadb -u members --password="{}" -D members <dbsetup.sql'.format(password), shell=True).wait()
    # then add members tables
    config = ConfigParser.ConfigParser()
    config.read('production.ini')
    engine = create_engine(config.get('app:main', 'sqlalchemy.url'))
    DBSession = models.base.configure_session(engine)
    # create the database model from models/ via CREATE statements
    models.base.Base.metadata.bind = engine
    models.base.Base.metadata.create_all(engine)
    # reserved transaction types
    DBSession.add(TransactionType(name='Membership Fee', mem_sup='memb', pos_neg='neg'))
    DBSession.add(TransactionType(name='Order Charge', mem_sup='memb', pos_neg='neg'))
    # others
    DBSession.add(TransactionType(name='Pay Wholesaler', mem_sup='whol', pos_neg='pos'))
    DBSession.add(TransactionType(name='Pay Vers supplier', mem_sup='vers', pos_neg='neg'))
    DBSession.add(TransactionType(name='Payment to Member', mem_sup='memb', pos_neg='pos'))
    DBSession.add(TransactionType(name='Late order change', mem_sup='memb', pos_neg='---'))

    workgroups = createWGs()
    # add old names, used in base.py and in testing (ask Nic what to do with it)
    addOldNames()
    # add a default admin
    addAdmin()
    # this applicants, members, shifts and transactions
    fillDBRandomly(None, workgroups)

    DBSession.flush()
    transaction.commit()

    print('Created database')


if __name__ == '__main__':
    main()
