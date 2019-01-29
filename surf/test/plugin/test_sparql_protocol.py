# -*- coding: UTF-8 -*-
from builtins import str
import pytest
import surf
import logging
from surf.store import NO_CONTEXT
from surf.rdf import Literal, URIRef
from surf.exceptions import CardinalityException
from surf.util import error_message
from surf.query import select
from surf.plugin.sparql_protocol.reader import SparqlReaderException
from surf.plugin.sparql_protocol.writer import SparqlWriterException

from surf.namespace import RDFS, RDF

@pytest.fixture
def get_store_session():
    """
    Return initialized SuRF store and session objects.
    """

    # maybe we can mock SPARQL endpoint.
    kwargs = {"reader": "sparql_protocol",
              "writer": "sparql_protocol",
              "endpoint": "http://localhost:9999/blazegraph/sparql",
              "use_subqueries": True,
              "combine_queries": False}

    #if True:  # use_default_context:
    #    kwargs["default_context"] = "http://surf_test_graph/dummy2"

    surf.log.setup_logger()
    surf.log.set_logger_level(logging.DEBUG)

    store = surf.Store(**kwargs)
    session = surf.Session(store)

    # Fresh start!
    store.clear("http://surf_test_graph/dummy2")
    #store.clear(URIRef("http://my_context_1"))
    #store.clear(URIRef("http://other_context_1"))

    store.clear()
    

    return store, session

def test_add_triples(get_store_session):
    """Test adding triples to store
    """

    store, session = get_store_session

    store.add_triple(URIRef("http://surf_test_graph/dummy2/Test"), RDF.type, URIRef("http://surf_test_graph/dummy2/cat"), context=None )

    #store


def test_orm(get_store_session):
    """Test ORM capability"""

    store, session = get_store_session

    FoafPerson = session.get_class(surf.ns.FOAF.Person)

    john = FoafPerson()
    john.foaf_title = "Dr"
    john.foaf_name = "John Smith"

    brian = FoafPerson()
    brian.foaf_title = "Mr"
    brian.foaf_name = "Brian Jones"

    john.foaf_knows =  brian
    brian.foaf_knows = john

    john.save()
    brian.save()

    session.commit()

    store.remove(john)
    
    session.commit()

    assert john.is_present() == False
    assert brian.is_present() == True

    store.remove(brian)

    session.commit()



def test_to_table():
    """
    Test _to_table with empty bindings.
    """

    data = {'results': {'bindings': [{'c': {}}]}}

    # This should not raise exception.
    try:
        store = surf.store.Store(reader="sparql_protocol")
        store.reader._to_table(data)
    except Exception as e:
        pytest.fail(error_message(e), pytrace=True)


def test_exceptions():
    """
    Test that exceptions are raised on invalid queries.
    """

    store = surf.Store(reader="sparql_protocol", writer="sparql_protocol", endpoint="invalid")

    def try_query():
        store.execute(query)

    query = select("?a")
    with pytest.raises(SparqlReaderException):
        try_query()

    def try_add_triple():
        store.add_triple("?s", "?p", "?o")

    with pytest.raises(SparqlWriterException):
        try_add_triple()
