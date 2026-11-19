import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Set;
import java.util.TreeSet;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.InferenceType;
import com.clarkparsia.pellet.owlapiv3.PelletReasoner;
import com.clarkparsia.pellet.owlapiv3.PelletReasonerFactory;

/**
 * Read-only Pellet check followed by extraction of the thirteen Allen relations.
 * Usage: Extract_Allen_Relations input.rdf output.nt
 * Requires separately installed OWLAPI 4 and Pellet; no libraries are vendored.
 * Output contains named interval-to-interval assertions, not Activity links.
 */
public class Extract_Allen_Relations {
    private static final String TIME = "http://www.w3.org/2006/time#";
    private static final String[] RELATIONS = {
        "intervalBefore", "intervalAfter", "intervalMeets", "intervalMetBy",
        "intervalOverlaps", "intervalOverlappedBy", "intervalStarts", "intervalStartedBy",
        "intervalDuring", "intervalContains", "intervalFinishes", "intervalFinishedBy",
        "intervalEquals"
    };

    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Expected input.rdf output.nt");
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(new File(args[0]));
        PelletReasoner reasoner = PelletReasonerFactory.getInstance().createReasoner(ontology);
        try {
            if (!reasoner.isConsistent()) throw new IllegalStateException("Ontology is inconsistent");
            reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY,
                InferenceType.OBJECT_PROPERTY_HIERARCHY, InferenceType.DATA_PROPERTY_HIERARCHY,
                InferenceType.CLASS_ASSERTIONS, InferenceType.OBJECT_PROPERTY_ASSERTIONS,
                InferenceType.DATA_PROPERTY_ASSERTIONS, InferenceType.SAME_INDIVIDUAL);
            Set<String> triples = new TreeSet<String>();
            OWLDataFactory factory = manager.getOWLDataFactory();
            for (String relation : RELATIONS) {
                OWLObjectProperty property = factory.getOWLObjectProperty(IRI.create(TIME + relation));
                for (OWLNamedIndividual subject : ontology.getIndividualsInSignature()) {
                    for (OWLNamedIndividual object : reasoner.getObjectPropertyValues(subject, property).getFlattened()) {
                        triples.add("<" + subject.getIRI() + "> <" + property.getIRI()
                            + "> <" + object.getIRI() + "> .");
                    }
                }
            }
            Files.write(Paths.get(args[1]), new ArrayList<String>(triples), StandardCharsets.UTF_8);
            System.out.println("ALLEN_ASSERTIONS=" + triples.size());
            System.out.println("SWRL_RULES=" + ontology.getAxioms(AxiomType.SWRL_RULE).size());
            System.out.println("LOGICAL_AXIOMS=" + ontology.getLogicalAxiomCount());
            System.out.println("CONSISTENT=true");
            System.out.println("PRECOMPUTE=PASS");
        } finally {
            reasoner.dispose();
        }
    }
}
