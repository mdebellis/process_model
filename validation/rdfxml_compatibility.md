# RDF/XML compatibility correction

Verified 18 November 2026 against GitHub commit
`a7cf5b4ba2659c21381899ad5ed4e6738c30bfe3`.

## Diagnosis

The GitHub ontology was byte-identical to the state/goal draft supplied for
upload. The upload did not cause the error. The draft's RDFLib RDF/XML export
had moved some `rdf:type` elements after other properties in their
`rdf:Description` elements.

With OWLAPI 4.5.29, that ordering caused named SWRL rules to be interpreted with
missing bodies or heads. The parser reported 4,108 axioms and 1,296 logical
axioms, matching the reported Protégé metrics. Pellet 2.3.0, from the official
Protégé Pellet plug-in, reported the resulting ontology as inconsistent. Its
explanation included a temporal rule whose body survived but whose head was
empty. Such a rule can make a matching body entail a contradiction.

This explains why the earlier OWLAPI 3 validation passed while Protégé failed.
An RDF graph comparison and a rule-count check alone do not detect this parser
behavior: the graph contained the full rules and both parsers counted ten rules.

## Correction

Place each description's `rdf:type` elements before its other property elements.
This is a serialization compatibility measure, not a change to RDF semantics.
The corrected file is RDF-graph-isomorphic to the uploaded draft: **5,294 triples
in both files**, with no changed axioms, IRIs, literal values or example data.
No rule was disabled or deleted, and no ontology metadata was changed.

The earlier input file already followed this ordering; regenerating it without
preserving that convention introduced the regression.

## Validation

- The failing file reproduces inconsistency with OWLAPI 4.5.29 and the official
  Protégé Pellet plug-in (bundle 2.2.0, embedded Pellet 2.3.0).
- The corrected file loads all ten rules with their complete bodies and heads.
- The corrected file passes consistency and all requested precomputation types,
  including class/property hierarchies, class/property assertions and same
  individuals. There are no named unsatisfiable classes.
- The corrected parser output contains 3,869 axioms and 1,296 logical axioms.
  The lower total reflects correct interpretation of the SWRL structures;
  it is not deletion of RDF triples.
- An OWLAPI 4 save/reload of the corrected ontology preserves its logical
  axioms exactly and remains consistent.
- All 26 state/query/invocation checks pass on the corrected file.
- The nine pre-existing example queries matched their pre-extension results
  during the GitHub audit. The correction preserves their entire RDF graph.

These checks use the parser and reasoner libraries directly. They reproduce
and resolve the reported failure without claiming a test on the user's Windows
installation. See [machine-readable results](rdfxml_compatibility.json) and the
[rule regression harness](Check_RDFXML_Rules.java).

## Opening the correction

Close the failed import in Protégé without saving its damaged parsed rule
structures over the source. Replace `ontologies/process_model_with_examples.rdf`
with the corrected file, reopen it and start Pellet again.

For future programmatic edits, preserve the type-first RDF/XML ordering and
validate **every parsed SWRL body and head**, not just the RDF triples or the
number of rules. Keep the original CLI validation reports as historical records;
this parser-specific check supplies the coverage they lacked.
