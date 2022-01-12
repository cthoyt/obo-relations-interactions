"""Generate OWL based on new relations."""

from pathlib import Path

import funowl
import pandas as pd
from funowl import (
    AnnotationAssertion,
    Class,
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

molecular_helper_property = obo["RO_0002564"]
molecularly_interacts_with = obo["RO_0002436"]
capable_of = obo["RO_0002215"]
has_direct_input = obo["RO_0002400"]
alternative_term = obo["IAO_0000118"]
opposite_of = obo["RO_0002604"]

DESCRIPTION_FORMAT = (
    "An interaction relation between x and y in which x catalyzes"
    " a reaction in which a {} is added to y."
)
REMOVE_DESCRIPTION_FORMAT = (
    "An interaction relation between x and y in which x catalyzes"
    " a reaction in which a {} is removed from y."
)


def main():
    df = pd.read_csv(TSV_PATH, sep="\t")
    df = df[df["add_go_id"].notna()]
    for k in [
        "add_helper_id",
        "add_id",
        "remove_helper_id",
        "remove_id",
        "add_go_id",
        "remove_go_id",
        "group_chebi_id",
    ]:
        df[k] = df[k].map(lambda s: s.replace(":", "_"), na_action="ignore")

    ontology = funowl.Ontology()
    ontology.annotations.extend(
        [
            AnnotationAssertion(
                RDFS.label, molecular_helper_property, "molecular helper property"
            ),
            AnnotationAssertion(
                RDFS.label, molecularly_interacts_with, "molecularly interacts with"
            ),
            AnnotationAssertion(RDFS.label, capable_of, "capable of"),
            AnnotationAssertion(RDFS.label, has_direct_input, "has direct input"),
            AnnotationAssertion(RDFS.label, alternative_term, "alternative term"),
            AnnotationAssertion(RDFS.label, opposite_of, "opposite of"),
            AnnotationAssertion(
                RDFS.label, orcid["0000-0003-4423-4370"], "Charles Tapley Hoyt"
            ),
        ]
    )
    for (
        add_helper_id,
        add_id,
        remove_helper_id,
        remove_id,
        add_name,
        group_chebi_id,
        group_chebi_name,
        add_go_id,
        add_go_name,
        remove_go_id,
        remove_go_name,
        orcid_id,
    ) in df.values:
        add_helper = obo[add_helper_id]
        add_relation = obo[add_id]
        add_go = obo[add_go_id] if pd.notna(add_go_id) else None
        remove_go = obo[remove_go_id] if pd.notna(remove_go_id) else None
        remove_helper = obo[remove_helper_id]
        remove_relation = obo[remove_id]
        group = obo[group_chebi_id] if pd.notna(group_chebi_id) else None
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

        # for parent_ns, parent_id in bio_ontology.get_parents("GO", add_go_id):
        #     parent = obo[f"{parent_ns}_{parent_id}"]
        #     ontology.declarations(Class(parent))
        #     ontology.annotations.append(
        #         AnnotationAssertion(RDFS.label, parent, bio_ontology.get_name(parent_ns, parent_id)))

        ontology.annotations.extend(
            [
                # Labels
                AnnotationAssertion(RDFS.label, add_relation, add_name),
                AnnotationAssertion(RDFS.label, add_helper, f"is {add_go_name}"),
                AnnotationAssertion(RDFS.label, remove_relation, f"de{add_name}"),
                # Contributors
                AnnotationAssertion(DC.contributor, add_helper, contributor),
                AnnotationAssertion(DC.contributor, add_relation, contributor),
                AnnotationAssertion(DC.contributor, remove_helper, contributor),
                AnnotationAssertion(DC.contributor, remove_relation, contributor),
                # Descriptions
                AnnotationAssertion(
                    alternative_term,
                    add_relation,
                    DESCRIPTION_FORMAT.format(group_chebi_name),
                ),
                AnnotationAssertion(
                    alternative_term,
                    remove_relation,
                    REMOVE_DESCRIPTION_FORMAT.format(group_chebi_name),
                ),
                # Everything is connected to everything, Brian
                AnnotationAssertion(opposite_of, add_relation, remove_relation),
                AnnotationAssertion(opposite_of, remove_relation, add_relation),
                AnnotationAssertion(opposite_of, add_helper, remove_helper),
                AnnotationAssertion(opposite_of, remove_helper, add_helper),
            ]
        )
        if group is not None:
            ontology.declarations(
                Class(group),
            )
            ontology.annotations.extend(
                [
                    AnnotationAssertion(RDFS.label, group, group_chebi_name),
                    AnnotationAssertion(RDFS.seeAlso, add_relation, group),
                    AnnotationAssertion(RDFS.seeAlso, add_helper, group),
                    AnnotationAssertion(RDFS.seeAlso, remove_relation, group),
                    AnnotationAssertion(RDFS.seeAlso, remove_helper, group),
                ]
            )

        if pd.notna(remove_go_name):
            ontology.annotations.append(
                AnnotationAssertion(RDFS.label, remove_helper, f"is {remove_go_name}")
            )
        elif pd.notna(add_go_name):
            ontology.annotations.append(
                AnnotationAssertion(
                    RDFS.label,
                    remove_helper,
                    f"is de{add_go_name}",
                )
            )

        if add_go is not None:
            ontology.annotations.append(
                AnnotationAssertion(RDFS.label, add_go, add_go_name),
            )
            ontology.subClassOf(
                add_go, ObjectHasSelf(ObjectPropertyExpression(add_helper))
            )
        # Most relations don't already have a GO relation for the reverse process
        if remove_go is not None:
            ontology.subClassOf(
                remove_go, ObjectHasSelf(ObjectPropertyExpression(add_helper))
            )
            ontology.annotations.append(
                AnnotationAssertion(RDFS.label, remove_go, remove_go_name),
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
