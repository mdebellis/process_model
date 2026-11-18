# Process model

An ontology for process modeling that combines P-Plan, PROV, OWL-Time, and SWRL rules for Allen interval relations. The combined source includes a collaborative tendering plan, a synthetic execution with timestamps, and the Method Omega methodology example.

## Open the ontology

Open [ontologies/process_model_with_examples.rdf](ontologies/process_model_with_examples.rdf) in Protégé, or import it into AllegroGraph. This self-contained RDF/XML file is the **single ontology source**: 4,942 asserted triples, including ten complete SWRL rules. Existing ontology, vocabulary, and individual IRIs are preserved.

**Keep the source in RDF/XML.** Opening and saving its named-rule Turtle representation in the affected Protégé/OWLAPI installation deleted SWRL rule content. The tested RDF/XML route preserved it; see the [execution notes](docs/figure8_execution.md#open-the-rdfxml-file-in-protégé).

## Examples and queries

| Example | Documentation | SPARQL queries |
|---|---|---|
| Figure 8 collaborative tendering plan | [Model notes](docs/figure8_model_notes.md) | Included in the model notes |
| Synthetic tender execution and temporal reasoning | [Execution notes](docs/figure8_execution.md) | [Execution queries](queries/figure8_execution/) |
| Method Omega hierarchy, conditions, and rework | [Method Omega notes](docs/method_omega_notes.md) | [Method Omega queries](queries/method_omega/) |

The plan examples describe possible work. The tender execution is synthetic demonstration data. Queries generally operate on asserted data; the execution query for Allen relations requires reasoner results made available to the query engine. Loading SWRL rule definitions alone does not execute them.

[Validation records](validation/README.md) distinguish current cleanup checks from historical reasoning and parser checks. Screenshots and the illustrative tender timeline are in [images](images/).
