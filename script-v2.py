import xmltodict
from py2neo import Graph, Node, Relationship
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def validate_data(dict_object, key):
    if key in dict_object.keys():
        return dict_object[key]
    return None


def ingest_data():
    # Open the XML file and load its contents to Dict so it's easier to deal with
    print('running', flush=True)
    with open('data/Q9Y261.xml') as fd:
        data = xmltodict.parse(fd.read())
        data = data['uniprot']['entry']
    # Connect to the Neo4j graph database

    graph = Graph('bolt://localhost:7687', auth=('neo4j', 'weavebio'), name='neo4j')

    # Delete all nodes and relationships in the graph
    graph.delete_all()


    for accession in data['accession']:
        protein_node = Node('Protein', accession=accession, name=data['name'])
        graph.create(protein_node)

        for name in data['protein']['recommendedName']['shortName']:
            fullname_node = Node('FullName', name=name)
            graph.create(fullname_node)
            rel = Relationship(protein_node, 'HAS_FULLNAME', fullname_node)
            graph.create(rel)

        fullname_node = Node('FullName', name=data['protein']['recommendedName']['fullName'])
        graph.create(fullname_node)
        rel = Relationship(protein_node, 'HAS_FULLNAME', fullname_node)
        graph.create(rel)

        for alt_name in data['protein']['alternativeName']:
            if 'fullName' in alt_name:
                fullname_node = Node('FullName', name=alt_name['fullName'])
                graph.create(fullname_node)
                rel = Relationship(protein_node, 'HAS_FULLNAME', fullname_node)
                graph.create(rel)

    # Create nodes and relationships for the features
    for feature in data['feature']:
        feature_node = Node('Features', name=feature['@type'])
        graph.create(feature_node)
        rel = Relationship(protein_node, 'HAS_FEATURE', feature_node)
        graph.create(rel)

    # Create nodes and relationships for the genes
    for gene_name in data['gene']['name']:
        gene_node = Node('Gene', name=gene_name['#text'], type=gene_name['@type'])
        graph.create(gene_node)

        rel = Relationship(protein_node, 'ENCODES', gene_node)
        graph.create(rel)

    # Create nodes and relationships for the organisms
    for organism in data['organism']['name']:
        organism_node = Node('Organism', name=organism['#text'])
        graph.create(organism_node)
        rel = Relationship(protein_node, 'IN_ORGANISM', organism_node)
        graph.create(rel)
        for lineage in data['organism']['lineage']['taxon']:
            lineage_node = Node('Lineage', name=lineage)
            graph.create(lineage_node)
            rel = Relationship(organism_node, 'HAS_LINEAGE', lineage_node)
            graph.create(rel)

    # Create nodes and relationships for the references
    for reference in data['reference']:
        reference_node = Node('Reference', key=reference['@key'])
        graph.create(reference_node)

        rel = Relationship(protein_node, 'HAS_REFERENCE', reference_node)
        graph.create(rel)

        citation = reference['citation']
        citation_node = Node('Citation', type=citation['@type'], name=validate_data(citation, '@name'), volume=citation.get('@volume'), date=citation.get('@date'), first=citation.get('@first'), last=citation.get('@last'), title=citation['title'])
        graph.create(citation_node)
        rel = Relationship(reference_node, 'HAS_CITATION', citation_node)
        graph.create(rel)

        if 'authorList' in citation:
            if 'person' in citation['authorList'].keys():
                for author in citation['authorList']['person']:
                    author_node = Node('Author', name=author['@name'])
                    graph.create(author_node)
                    rel = Relationship(citation_node, 'HAS_AUTHOR', author_node)
                    graph.create(rel)

        if 'dbReference' in citation:
            for db_ref in citation['dbReference']:
                db_ref_node = Node('DBReference', type=db_ref['@type'], id=db_ref['@id'])

    print('done')
                
# Set up scheduler to run ingest_data function every hour
dag = DAG(
    'my_dag',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False
)

ingest_data_task = PythonOperator(
    task_id='ingest_data_task',
    python_callable=ingest_data,
    dag=dag
)

ingest_data_task
