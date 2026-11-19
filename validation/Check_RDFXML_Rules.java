import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.InferenceType;
import com.clarkparsia.pellet.owlapiv3.PelletReasoner;
import com.clarkparsia.pellet.owlapiv3.PelletReasonerFactory;

/**
 * Checks parsed SWRL content, consistency, and all relevant precomputations.
 * Compatible with the OWLAPI 3 and OWLAPI 4 interfaces used in this investigation.
 * Does not alter the supplied ontology.
 *
 * Arguments:
 *   ontology.rdf [--expected expected_rule_atom_counts.tsv]
 *                [--write-expected expected_rule_atom_counts.tsv] [--roundtrip]
 *
 * Compile/run using separately installed OWLAPI and Pellet dependencies.
 * A machine-readable JSON object is printed after the VALIDATION_JSON= marker.
 * Exit 0 means all requested checks passed; exit 1 means failure.
 * The round-trip option saves a temporary RDF/XML copy, reloads it with a new
 * manager, checks its rule content and consistency, and then deletes the copy.
 */
public class Check_RDFXML_Rules {
    static class RuleCounts {
        int body;
        int head;
        String bodyKinds;
        String headKinds;
        RuleCounts(int b, int h, String bk, String hk) {
            body = b; head = h; bodyKinds = bk; headKinds = hk;
        }
        String tsv(String label) {
            return label + "\t" + body + "\t" + head + "\t" + bodyKinds + "\t" + headKinds;
        }
        Map<String,Object> json() {
            Map<String,Object> m = new TreeMap<String,Object>();
            m.put("body_atoms", body); m.put("head_atoms", head);
            m.put("body_atom_kinds", bodyKinds); m.put("head_atom_kinds", headKinds);
            return m;
        }
        boolean same(RuleCounts other) {
            return other != null && body == other.body && head == other.head
                && bodyKinds.equals(other.bodyKinds) && headKinds.equals(other.headKinds);
        }
    }

    static String kinds(Iterable<SWRLAtom> atoms) {
        Map<String,Integer> counts = new TreeMap<String,Integer>();
        for (SWRLAtom atom : atoms) {
            String kind;
            if (atom instanceof SWRLBuiltInAtom) {
                SWRLBuiltInAtom b = (SWRLBuiltInAtom) atom;
                kind = "builtin|" + b.getPredicate().toString() + "|arguments=" + b.getArguments().size();
            } else if (atom instanceof SWRLClassAtom) kind = "class";
            else if (atom instanceof SWRLDataPropertyAtom) kind = "data_property";
            else if (atom instanceof SWRLObjectPropertyAtom) kind = "object_property";
            else if (atom instanceof SWRLDifferentIndividualsAtom) kind = "different_individuals";
            else if (atom instanceof SWRLSameIndividualAtom) kind = "same_individual";
            else if (atom instanceof SWRLDataRangeAtom) kind = "data_range";
            else kind = atom.getClass().getName();
            counts.put(kind, counts.containsKey(kind) ? counts.get(kind) + 1 : 1);
        }
        StringBuilder result = new StringBuilder();
        for (Map.Entry<String,Integer> entry : counts.entrySet()) {
            if (result.length() > 0) result.append(";");
            result.append(entry.getKey()).append("=").append(entry.getValue());
        }
        return result.toString();
    }

    static Map<String,RuleCounts> rules(OWLOntology ontology) {
        Map<String,RuleCounts> result = new TreeMap<String,RuleCounts>();
        int unnamed = 0;
        for (SWRLRule rule : ontology.getAxioms(AxiomType.SWRL_RULE)) {
            // OWLAPI 3 can discard rule annotations while OWLAPI 4 retains them.
            // Match these rules by their unique head predicate, not by labels.
            List<String> heads = new ArrayList<String>();
            for (SWRLAtom atom : rule.getHead()) {
                if (atom instanceof SWRLObjectPropertyAtom)
                    heads.add(((SWRLObjectPropertyAtom) atom).getPredicate().toString());
                else if (atom instanceof SWRLDataPropertyAtom)
                    heads.add(((SWRLDataPropertyAtom) atom).getPredicate().toString());
                else if (atom instanceof SWRLClassAtom)
                    heads.add(((SWRLClassAtom) atom).getPredicate().toString());
                else heads.add(atom.toString());
            }
            Collections.sort(heads);
            String label = heads.isEmpty() ? "Empty_Head_Rule_" + (++unnamed) : heads.toString();
            if (result.containsKey(label)) label += "_Duplicate_" + (++unnamed);
            result.put(label, new RuleCounts(rule.getBody().size(), rule.getHead().size(),
                kinds(rule.getBody()), kinds(rule.getHead())));
        }
        return result;
    }

    static Map<String,RuleCounts> readExpected(Path path) throws Exception {
        Map<String,RuleCounts> result = new TreeMap<String,RuleCounts>();
        for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {
            if (line.trim().length() == 0 || line.startsWith("#")) continue;
            String[] columns = line.split("\t", -1);
            if (columns.length != 5) throw new IllegalArgumentException("Expected five TSV columns: " + line);
            result.put(columns[0], new RuleCounts(Integer.parseInt(columns[1]),
                Integer.parseInt(columns[2]), columns[3], columns[4]));
        }
        return result;
    }

    static List<String> compare(Map<String,RuleCounts> actual, Map<String,RuleCounts> expected) {
        List<String> failures = new ArrayList<String>();
        for (Map.Entry<String,RuleCounts> entry : expected.entrySet()) {
            if (!entry.getValue().same(actual.get(entry.getKey()))) failures.add("Changed or missing rule: " + entry.getKey());
        }
        for (String key : actual.keySet()) if (!expected.containsKey(key)) failures.add("Unexpected rule: " + key);
        return failures;
    }

    static Map<String,Object> assess(OWLOntology ontology, Map<String,RuleCounts> expected) {
        Map<String,Object> report = new TreeMap<String,Object>();
        Map<String,RuleCounts> actual = rules(ontology);
        Map<String,Object> ruleDetails = new TreeMap<String,Object>();
        List<String> errors = new ArrayList<String>();
        for (Map.Entry<String,RuleCounts> entry : actual.entrySet()) {
            ruleDetails.put(entry.getKey(), entry.getValue().json());
            if (entry.getValue().body == 0 || entry.getValue().head == 0)
                errors.add("Empty body or head: " + entry.getKey());
        }
        if (expected != null) errors.addAll(compare(actual, expected));
        report.put("axioms", ontology.getAxiomCount());
        report.put("logical_axioms", ontology.getLogicalAxiomCount());
        report.put("rule_count", actual.size());
        report.put("rules", ruleDetails);
        report.put("rule_content_checks_pass", errors.isEmpty());
        report.put("rule_content_errors", errors);
        PelletReasoner reasoner = null;
        try {
            reasoner = PelletReasonerFactory.getInstance().createReasoner(ontology);
            boolean consistent = reasoner.isConsistent();
            report.put("consistent", consistent);
            if (consistent) {
                reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY,
                    InferenceType.OBJECT_PROPERTY_HIERARCHY, InferenceType.DATA_PROPERTY_HIERARCHY,
                    InferenceType.CLASS_ASSERTIONS, InferenceType.OBJECT_PROPERTY_ASSERTIONS,
                    InferenceType.DATA_PROPERTY_ASSERTIONS, InferenceType.SAME_INDIVIDUAL);
                report.put("all_precomputations_pass", true);
                report.put("unsatisfiable_named_classes", reasoner.getUnsatisfiableClasses().getEntitiesMinusBottom().size());
            } else report.put("all_precomputations_pass", false);
        } catch (Throwable exception) {
            report.put("reasoner_error", exception.toString());
            report.put("all_precomputations_pass", false);
        } finally {
            if (reasoner != null) reasoner.dispose();
        }
        report.put("passed", errors.isEmpty() && Boolean.TRUE.equals(report.get("consistent"))
            && Boolean.TRUE.equals(report.get("all_precomputations_pass"))
            && Integer.valueOf(0).equals(report.get("unsatisfiable_named_classes")));
        return report;
    }

    static String json(Object value) {
        if (value == null) return "null";
        if (value instanceof Boolean || value instanceof Number) return value.toString();
        if (value instanceof Map) {
            StringBuilder out = new StringBuilder("{");
            for (Object object : ((Map<?,?>) value).entrySet()) {
                Map.Entry<?,?> entry = (Map.Entry<?,?>) object;
                if (out.length() > 1) out.append(',');
                out.append(json(entry.getKey().toString())).append(':').append(json(entry.getValue()));
            }
            return out.append('}').toString();
        }
        if (value instanceof Iterable) {
            StringBuilder out = new StringBuilder("[");
            for (Object item : (Iterable<?>) value) {
                if (out.length() > 1) out.append(',');
                out.append(json(item));
            }
            return out.append(']').toString();
        }
        String text = value.toString();
        StringBuilder out = new StringBuilder("\"");
        for (int i = 0; i < text.length(); ++i) {
            char c = text.charAt(i);
            if (c == '\\' || c == '\"') out.append('\\').append(c);
            else if (c == '\n') out.append("\\n");
            else if (c == '\r') out.append("\\r");
            else if (c == '\t') out.append("\\t");
            else if (c < 0x20) out.append(String.format("\\u%04x", (int)c));
            else out.append(c);
        }
        return out.append('\"').toString();
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) throw new IllegalArgumentException("Supply an RDF/XML ontology file.");
        Path expectedPath = null;
        Path writeExpectedPath = null;
        boolean roundTrip = false;
        for (int i = 1; i < args.length; ++i) {
            if (args[i].equals("--expected")) expectedPath = Paths.get(args[++i]);
            else if (args[i].equals("--write-expected")) writeExpectedPath = Paths.get(args[++i]);
            else if (args[i].equals("--roundtrip")) roundTrip = true;
            else throw new IllegalArgumentException("Unknown option: " + args[i]);
        }
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(new File(args[0]));
        Map<String,RuleCounts> expected = expectedPath == null ? null : readExpected(expectedPath);
        Map<String,Object> report = new TreeMap<String,Object>();
        report.put("input_file", new File(args[0]).getName());
        report.put("expected_rule_counts_supplied", expected != null);
        Map<String,Object> initial = assess(ontology, expected);
        report.put("initial_load", initial);
        boolean passed = Boolean.TRUE.equals(initial.get("passed"));
        if (writeExpectedPath != null) {
            if (!passed) throw new IllegalStateException("Cannot establish expected counts from a failed check.");
            List<String> lines = new ArrayList<String>();
            lines.add("# head_predicate_key\tbody_atoms\thead_atoms\tbody_atom_kinds\thead_atom_kinds");
            for (Map.Entry<String,RuleCounts> entry : rules(ontology).entrySet()) lines.add(entry.getValue().tsv(entry.getKey()));
            Files.write(writeExpectedPath, lines, StandardCharsets.UTF_8);
        }
        if (roundTrip) {
            File temporary = File.createTempFile("process-model-rdfxml-roundtrip-", ".rdf");
            try {
                manager.saveOntology(ontology, IRI.create(temporary));
                OWLOntologyManager secondManager = OWLManager.createOWLOntologyManager();
                OWLOntology reloaded = secondManager.loadOntologyFromOntologyDocument(temporary);
                Map<String,Object> again = assess(reloaded, rules(ontology));
                report.put("save_reload", again);
                boolean equalLogical = ontology.getLogicalAxioms().equals(reloaded.getLogicalAxioms());
                report.put("save_reload_logical_axioms_equal", equalLogical);
                passed = passed && Boolean.TRUE.equals(again.get("passed")) && equalLogical;
            } finally {
                Files.deleteIfExists(temporary.toPath());
            }
        }
        report.put("passed", passed);
        System.out.println("VALIDATION_JSON=" + json(report));
        if (!passed) System.exit(1);
    }
}
