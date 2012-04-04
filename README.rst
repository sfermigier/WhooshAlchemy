WhooshAlchemy
=============

ALPHA but actively developed.

Supports the easy text-indexing of SQLAlchemy model fields.

BSD license.


Quick start example
-------------------

Import this library:

>>> from whooshalchemy import IndexService

Standard SQLAlchemy imports:

>>> from sqlalchemy.ext.declarative import declarative_base
>>> from sqlalchemy.schema import Column
>>> from sqlalchemy.types import Integer, Text, DateTime
>>> from sqlalchemy.engine import create_engine
>>> from sqlalchemy.orm.session import sessionmaker

Setup SQLAlchemy:

>>> engine = create_engine('sqlite:///:memory:')
>>> Session = sessionmaker(bind=engine)
>>> session = Session()
>>> Base = declarative_base()

Our model:

>>> class BlogPost(Base):
...   __tablename__ = 'blogpost'
...   __searchable__ = ['title', 'content']  # these fields will be indexed by whoosh
...
...   id = Column(Integer, primary_key=True)
...   title = Column(Text)
...   content = Column(Text)
...
...   def __repr__(self):
...       return '{0}(title={1})'.format(self.__class__.__name__, self.title)
...
>>> Base.metadata.create_all(engine)

Create and init indexing service:

>>> config = {"WHOOSH_BASE": "/tmp/whoosh"}
>>> index_service = IndexService(config=config, session=session)
>>> index_service.register_class(BlogPost)
FileIndex(FileStorage('/tmp/whoosh/BlogPost'), 'MAIN')

Create a blog post:

>>> m = BlogPost(title=u'My cool title', content=u'This is the first post.')
>>> session.add(m); session.commit()

Perform a few searches:

>>> list(BlogPost.search_query(u'cool'))
[BlogPost(title=My cool title)]
>>> list(BlogPost.search_query(u'first'))
[BlogPost(title=My cool title)]

Note: the response is a ``BaseQuery`` object, so you can append other SQL operations:

>>> list(BlogPost.search_query(u'first').filter(BlogPost.id >= 0))
[BlogPost(title=My cool title)]

Using with Flask
----------------

Setup you Flask app, create the ``db`` object (``db = SQLAlchemy(app)``), import your models.

Set ``WHOOSH_BASE`` to your Whoosh index directory in your Flask , then create the index service
and register your models:

>>> index_service = IndexService(config=app.config)
>>> index_service.register_class(MyFirstModel)
>>> index_service.register_class(MySecondModel)

Etc.