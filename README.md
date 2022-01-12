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

1. `add_helper_id` the RO identifier for the helper identifier for the add
   relationship
2. `add_id` the RO identifier for the add relationship
3. `remove_helper_id` the RO identifier for the helper identifier for the remove
   relationship
4. `remove_id` the RO identifier for the remove relationship
5. `add_name` the name of the addition relationship, e.g., *myristoylates*
6. `group_name` the name of the group that's added, e.g., *myristoyl*
7. `group_chebi_id` the CHEBI identifier (as a CURIE) for the group that's
   added, e.g., `CHEBI:25456`
8. `add_go_id` the GO identifier (as a CURIE) for the corresponding molecular
   function related to adding the group
9. `add_go_name` the GO name for above
10. `remove_go_id` the GO identifier (as a CURIE) for the corresponding
    molecular function related to removing the group
11. `remove_go_name` th GO name for above

## How to Build

Run with `tox` like:

```shell
$ pip install tox
$ tox
```


