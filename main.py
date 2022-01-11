"""Generate OWL based on new relations."""

from pathlib import Path

import funowl
import pandas as pd
from funowl import (
    AnnotationAssertion,
    ObjectHasSelf,
    ObjectProperty,
    ObjectPropertyChain,
    ObjectPropertyExpression,
)
from rdflib import DC, RDFS, Namespace

HERE = Path(__file__).parent.resolve()
TSV_PATH = HERE / "relations.tsv"
OWL_PATH = HERE / "relations.owl"

obo = Namespace("http://purl.obolibrary.org/obo/")
orcid = Namespace("https://orcid.org/")
iao = Namespace("https://orcid.org/")

molecular_helper_property = obo["RO_0002564"]
molecularly_interacts_with = obo["RO_0002436"]
capable_of = obo["RO_0002215"]
has_direct_input = obo["RO_0002400"]
alternative_term = obo["IAO_0000118"]
opposite_of = obo["RO_0002604"]

DESCRIPTION_FORMAT = (
    "An interaction relation between x and y in which x catalyzes"
    " a reaction in which a {} group is added to y."
)
REMOVE_DESCRIPTION_FORMAT = (
    "An interaction relation between x and y in which x catalyzes"
    " a reaction in which a {} group is removed from y."
)


def main():
    df = pd.read_csv(TSV_PATH, sep="\t")
    for k in "add_go_id", "remove_go_id", "group_chebi_id":
        df[k] = df[k].map(lambda s: s.replace(":", "_"), na_action="ignore")

    ontology = funowl.Ontology()
    for (
        start_ro_id,
        add_name,
        group_name,
        group_chebi_id,
        add_go_id,
        add_go_name,
        remove_go_id,
        remove_go_name,
        orcid_id,
    ) in df.values:
        add_helper = obo[f"RO_{start_ro_id + 0:07}"]
        add_relation = obo[f"RO_{start_ro_id + 1:07}"]
        add_go = obo[add_go_id]
        remove_go = obo[remove_go_id] if pd.notna(remove_go_id) else None
        remove_helper = obo[f"RO_{start_ro_id + 2:07}"]
        remove_relation = obo[f"RO_{start_ro_id + 3:07}"]
        contributor = orcid[orcid_id]

        ontology.declarations(
            ObjectProperty(add_helper),
            ObjectProperty(add_relation),
            ObjectProperty(remove_helper),
            ObjectProperty(remove_relation),
        )
        ontology.subObjectPropertyOf(add_helper, molecular_helper_property)
        ontology.subObjectPropertyOf(add_relation, molecularly_interacts_with)
        ontology.subObjectPropertyOf(remove_helper, molecular_helper_property)
        ontology.subObjectPropertyOf(remove_relation, molecularly_interacts_with)

        ontology.annotations.extend(
            [
                # Labels
                AnnotationAssertion(RDFS.label, add_relation, add_name),
                AnnotationAssertion(RDFS.label, add_helper, f"is {add_go_name}"),
                AnnotationAssertion(RDFS.label, remove_relation, f"de{add_name}"),
                AnnotationAssertion(
                    RDFS.label,
                    remove_helper,
                    f"is de{add_go_name}"
                    if pd.isna(remove_go_name)
                    else f"is {remove_go_name}",
                ),
                # Contributors
                AnnotationAssertion(DC.contributor, add_helper, contributor),
                AnnotationAssertion(DC.contributor, add_relation, contributor),
                AnnotationAssertion(DC.contributor, remove_helper, contributor),
                AnnotationAssertion(DC.contributor, remove_relation, contributor),
                # Descriptions
                AnnotationAssertion(
                    alternative_term,
                    add_relation,
                    DESCRIPTION_FORMAT.format(group_name),
                ),
                AnnotationAssertion(
                    alternative_term,
                    remove_relation,
                    REMOVE_DESCRIPTION_FORMAT.format(group_name),
                ),
                # Everything is connected to everything, Brian
                AnnotationAssertion(opposite_of, add_relation, remove_relation),
                AnnotationAssertion(opposite_of, remove_relation, add_relation),
            ]
        )

        ontology.subClassOf(add_go, ObjectHasSelf(ObjectPropertyExpression(add_helper)))
        # Most relations don't already have a GO relation for the reverse process
        if remove_go is not None:
            ontology.subClassOf(
                remove_go, ObjectHasSelf(ObjectPropertyExpression(add_helper))
            )

        ontology.subObjectPropertyOf(
            ObjectPropertyChain(
                ObjectPropertyExpression(capable_of),
                ObjectPropertyExpression(add_helper),
                ObjectPropertyExpression(has_direct_input),
            ),
            ObjectProperty(add_relation),
        )
        ontology.subObjectPropertyOf(
            ObjectPropertyChain(
                ObjectPropertyExpression(capable_of),
                ObjectPropertyExpression(remove_helper),
                ObjectPropertyExpression(has_direct_input),
            ),
            ObjectProperty(remove_relation),
        )

    doc = funowl.OntologyDocument(ontology=ontology, obo=obo, orcid=orcid, dce=DC)
    s = str(doc)
    print(s)
    with open(OWL_PATH, "w") as file:
        print(s, file=file)


if __name__ == "__main__":
    main()
