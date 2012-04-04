from __future__ import absolute_import

import whooshalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text, DateTime, UnicodeText
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

    class Post(Base):
      __tablename__ = 'objectA'
      __searchable__ = ['title', 'body']

      id = Column(Integer, primary_key=True)
      title = Column(Text)
      body = Column(UnicodeText)
      created = Column(DateTime, default=datetime.datetime.utcnow())

      def __repr__(self):
        return '{0}(title={1})'.format(self.__class__.__name__, self.title)

    self.Post = Post
    Base.metadata.create_all(engine)

    self.index_manager = whooshalchemy.IndexService(session=self.session)
    self.index_manager.register_class(Post)

  def tearDown(self):
      try:
          shutil.rmtree(self.index_manager.whoosh_base)
      except OSError, e:
          if e.errno != 2:  # code 2 - no such file or directory
              raise


  def test_title(self):
      def add(title):
          item = self.Post(title=title)
          self.session.add(item)
          self.session.commit()
          return item

      a = add(u'good times were had by all')
      res = list(self.Post.search_query(u'good'))
      self.assertEqual(len(res), 1)
      self.assertEqual(res[0].id, a.id)

      b = add(u'good natured people are fun')
      res = list(self.Post.search_query(u'good'))
      self.assertEqual(len(res), 2)
      self.assertEqual(res[0].id, a.id)
      self.assertEqual(res[1].id, b.id)

      res = list(self.Post.search_query(u'people'))
      self.assertEqual(len(res), 1)
      self.assertEqual(res[0].id, b.id)

      a = self.session.query(self.Post).get(1)
      self.session.delete(a)
      self.session.commit()

      res = list(self.Post.search_query(u'good'))
      self.assertEqual(len(res), 1)
      self.assertEqual(res[0].id, b.id)

      a = self.Post(title=u'good old post', created=datetime.date.today() - datetime.timedelta(2))
      self.session.add(a)
      self.session.commit()
      res = list(self.Post.search_query(u'good'))
      self.assertEqual(len(res), 2)

      recent = list(self.Post.search_query(u'good').filter(self.Post.created >= datetime.date.today() - datetime.timedelta(1)))
      self.assertEqual(len(recent), 1)
      self.assertEqual(recent[0].title, b.title)

      old = list(self.Post.search_query(u'good').filter(self.Post.created <= datetime.date.today() - datetime.timedelta(1)))
      self.assertEqual(len(old), 1)
      self.assertEqual(old[0].title, a.title)

  def test_body(self):
    def add(title, body):
      item = self.Post(title=title, body=body)
      self.session.add(item)
      self.session.commit()
      return item

    a = add(u'my title', u'my body')
    res = list(self.Post.search_query(u'title'))
    self.assertEqual(len(res), 1)
    self.assertEqual(res[0].id, a.id)

    res = list(self.Post.search_query(u'body'))
    self.assertEqual(len(res), 1)
    self.assertEqual(res[0].id, a.id)

    res = list(self.Post.search_query(u'something'))
    self.assertEqual(len(res), 0)
