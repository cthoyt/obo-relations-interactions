# Relation Ontology Extension Demo

This repository demonstrates auto-generation of new molecular interaction
relationships as a follow-up to https://github.com/oborel/obo-relations/pull/522
.

## Artifacts

| File                             | Description             |
|----------------------------------|-------------------------|
| [`relations.tsv`](relations.tsv) | The input curation file |
| [`relations.owl`](relations.owl) | The output OWL file     |

Fields in the input file:

1. `id` the integer for the first RO local unique identifier. Four identifiers
   will be minted for each row
2. `add_name` the name of the addition relationship, e.g., *myristoylates*
3. `group_name` the name of the group that's added, e.g., *myristoyl*
4. `group_chebi_id` the CHEBI identifier (as a CURIE) for the group that's
   added, e.g., `CHEBI:25456`
5. `add_go_id` the GO identifier (as a CURIE) for the corresponding molecular
   function related to adding the group
6. `add_go_name` the GO name for above
7. `remove_go_id` the GO identifier (as a CURIE) for the corresponding molecular
   function related to removing the group
8. `remove_go_name` th GO name for above

## How to Build

Run with `tox` like:

```shell
$ pip install tox
$ tox
```


