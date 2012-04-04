from __future__ import absolute_import

import whooshalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text, DateTime
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from unittest import TestCase
import datetime
import shutil


class Tests(TestCase):

  def setUp(self):

    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    self.session = Session()

    Base = declarative_base()

    class ObjectA(Base):
      __tablename__ = 'objectA'
      __searchable__ = ['title']

      id = Column(Integer, primary_key=True)
      title = Column(Text)
      created = Column(DateTime, default=datetime.datetime.utcnow())

      def __repr__(self):
        return '{0}(title={1})'.format(self.__class__.__name__, self.title)

    self.ObjectA = ObjectA
    Base.metadata.create_all(engine)

    self.index_manager = whooshalchemy.IndexService(self.session)
    self.index_manager.register_class(ObjectA)

  def tearDown(self):
      try:
          shutil.rmtree(self.index_manager.whoosh_base)
      except OSError, e:
          if e.errno != 2:  # code 2 - no such file or directory
              raise


  def test_main(self):
      def add(title):
          item = self.ObjectA(title=title)
          self.session.add(item)
          self.session.commit()
          return item

      a = add(u'good times were had by all')
      res = list(self.ObjectA.search_query(u'good'))
      self.assertEqual(len(res), 1)
      self.assertEqual(res[0].id, a.id)

      b = add(u'good natured people are fun')
      res = list(self.ObjectA.search_query(u'good'))
      self.assertEqual(len(res), 2)
      self.assertEqual(res[0].id, a.id)
      self.assertEqual(res[1].id, b.id)

      res = list(self.ObjectA.search_query(u'people'))
      self.assertEqual(len(res), 1)
      self.assertEqual(res[0].id, b.id)

      a = self.session.query(self.ObjectA).get(1)
      self.session.delete(a)
      self.session.commit()

      res = list(self.ObjectA.search_query(u'good'))
      self.assertEqual(len(res), 1)
      self.assertEqual(res[0].id, b.id)

      a = self.ObjectA(title=u'good old post', created=datetime.date.today() - datetime.timedelta(2))
      self.session.add(a)
      self.session.commit()
      res = list(self.ObjectA.search_query(u'good'))
      self.assertEqual(len(res), 2)

      recent = list(self.ObjectA.search_query(u'good').filter(self.ObjectA.created >= datetime.date.today() - datetime.timedelta(1)))
      self.assertEqual(len(recent), 1)
      self.assertEqual(recent[0].title, b.title)

      old = list(self.ObjectA.search_query(u'good').filter(self.ObjectA.created <= datetime.date.today() - datetime.timedelta(1)))
      self.assertEqual(len(old), 1)
      self.assertEqual(old[0].title, a.title)
