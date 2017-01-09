"""

WhooshAlchemy
~~~~~~~~~~~~~

Adds Whoosh indexing capabilities to SQLAlchemy models.

Based on Flask-whooshalchemy by Karl Gyllstrom (Flask is still supported, but not mandatory).

:copyright: (c) 2012 by Stefane Fermigier
:copyright: (c) 2012 by Karl Gyllstrom
:license: BSD (see LICENSE.txt)
"""

from __future__ import absolute_import, print_function, unicode_literals

import os

from six import text_type

import sqlalchemy
import whoosh.index
from sqlalchemy import event
from sqlalchemy.orm.session import Session
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema
from whoosh.qparser import MultifieldParser


class IndexService(object):

    def __init__(self, config=None, session=None, whoosh_base=None):
        self.session = session
        if not whoosh_base and config:
            whoosh_base = config.get("WHOOSH_BASE")
        if not whoosh_base:
            whoosh_base = "whoosh_indexes"  # Default value
        self.whoosh_base = whoosh_base
        self.indexes = {}

        event.listen(Session, "before_commit", self.before_commit)
        event.listen(Session, "after_commit", self.after_commit)

    def register_class(self, model_class):
        """
        Registers a model class, by creating the necessary Whoosh index if needed.
        """

        index_path = os.path.join(self.whoosh_base, model_class.__name__)

        schema, primary = self._get_whoosh_schema_and_primary(model_class)

        if whoosh.index.exists_in(index_path):
            index = whoosh.index.open_dir(index_path)
        else:
            if not os.path.exists(index_path):
                os.makedirs(index_path)
            index = whoosh.index.create_in(index_path, schema)

        self.indexes[model_class.__name__] = index
        model_class.search_query = Searcher(model_class, primary, index,
                                            self.session)
        return index

    def index_for_model_class(self, model_class):
        """
        Gets the whoosh index for this model, creating one if it does not exist.
        in creating one, a schema is created based on the fields of the model.
        Currently we only support primary key -> whoosh.ID, and sqlalchemy.TEXT
        -> whoosh.TEXT, but can add more later. A dict of model -> whoosh index
        is added to the ``app`` variable.
        """
        index = self.indexes.get(model_class.__name__)
        if index is None:
            index = self.register_class(model_class)
        return index

    def _get_whoosh_schema_and_primary(self, model_class):
        schema = {}
        primary = None
        for field in model_class.__table__.columns:
            if field.primary_key:
                schema[field.name] = whoosh.fields.ID(stored=True, unique=True)
                primary = field.name
            if field.name in model_class.__searchable__:
                if type(field.type) in (sqlalchemy.types.Text,
                                        sqlalchemy.types.UnicodeText):
                    schema[field.name] = whoosh.fields.TEXT(
                        analyzer=StemmingAnalyzer())

        return Schema(**schema), primary

    def before_commit(self, session):
        self.to_update = {}

        for model in session.new:
            model_class = model.__class__
            if hasattr(model_class, '__searchable__'):
                self.to_update.setdefault(model_class.__name__, []).append(
                    ("new", model))

        for model in session.deleted:
            model_class = model.__class__
            if hasattr(model_class, '__searchable__'):
                self.to_update.setdefault(model_class.__name__, []).append(
                    ("deleted", model))

        for model in session.dirty:
            model_class = model.__class__
            if hasattr(model_class, '__searchable__'):
                self.to_update.setdefault(model_class.__name__, []).append(
                    ("changed", model))

    def after_commit(self, session):
        """
        Any db updates go through here. We check if any of these models have
        ``__searchable__`` fields, indicating they need to be indexed. With these
        we update the whoosh index for the model. If no index exists, it will be
        created here; this could impose a penalty on the initial commit of a model.
        """

        for typ, values in self.to_update.items():
            model_class = values[0][1].__class__
            index = self.index_for_model_class(model_class)
            with index.writer() as writer:
                primary_field = model_class.search_query.primary
                searchable = model_class.__searchable__

                for change_type, model in values:
                    # delete everything. stuff that's updated or inserted will get
                    # added as a new doc. Could probably replace this with a whoosh
                    # update.

                    writer.delete_by_term(
                        primary_field, text_type(getattr(model, primary_field)))

                    if change_type in ("new", "changed"):
                        attrs = dict((key, getattr(model, key))
                                     for key in searchable)
                        attrs[primary_field] = text_type(
                            getattr(model, primary_field))
                        writer.add_document(**attrs)

        self.to_update = {}


class Searcher(object):
    """
    Assigned to a Model class as ``search_query``, which enables text-querying.
    """

    def __init__(self, model_class, primary, index, session=None):
        self.model_class = model_class
        self.primary = primary
        self.index = index
        self.session = session
        self.searcher = index.searcher()
        fields = set(index.schema._fields.keys()) - set([self.primary])
        self.parser = MultifieldParser(list(fields), index.schema)

    def __call__(self, query, limit=None):
        session = self.session
        # When using Flask, get the session from the query attached to the model class.
        if not session:
            session = self.model_class.query.session

        results = self.index.searcher().search(
            self.parser.parse(query), limit=limit)
        keys = [x[self.primary] for x in results]
        primary_column = getattr(self.model_class, self.primary)
        return session.query(self.model_class).filter(primary_column.in_(keys))
