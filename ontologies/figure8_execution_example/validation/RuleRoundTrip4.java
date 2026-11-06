import java.io.File;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.formats.RDFXMLDocumentFormat;
import org.semanticweb.owlapi.formats.TurtleDocumentFormat;

public class RuleRoundTrip4 {
  public static void report(String stage, OWLOntology ontology) {
    List<String> rows = new ArrayList<>();
    for (SWRLRule rule : ontology.getAxioms(AxiomType.SWRL_RULE)) {
      rows.add(rule.getAnnotations().toString()+" body="+rule.getBody().size()+" head="+rule.getHead().size());
    }
    Collections.sort(rows);
    System.out.println(stage+" AXIOMS="+ontology.getAxiomCount()+" RULES="+rows.size());
    for(String row:rows) System.out.println(row);
  }
  public static void main(String[] args) throws Exception {
    OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
    OWLOntology ontology = manager.loadOntologyFromOntologyDocument(new File(args[0]));
    report("LOADED", ontology);
    File target = new File(args[1]);
    OWLDocumentFormat format = args[1].endsWith(".ttl") ? new TurtleDocumentFormat() : new RDFXMLDocumentFormat();
    manager.saveOntology(ontology,format,IRI.create(target));
    OWLOntologyManager manager2 = OWLManager.createOWLOntologyManager();
    OWLOntology reloaded = manager2.loadOntologyFromOntologyDocument(target);
    report("RELOADED", reloaded);
  }
}
