from surf import *
from surf.rdf import ClosedNamespace, Namespace, RDF, RDFS

store = Store(  reader='rdflib',
            writer='rdflib',
            rdflib_store = 'IOMemory')

session = Session(store)

CEL = Namespace('http://lied.inf.ufes.br/ontologies/birds#')

print 'Load RDF data'
store.load_triples(source='ontologia.owl')

print CEL.Teste
Teste = session.get_class(CEL.Teste)

all_birds = Teste.all()

print 'Found %d birds'%(len(all_birds))
for bird in all_birds:
    print bird.rdfs_label
