import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import java.io.InputStream;
import java.util.regex.Pattern;

/**
 * Secure UserService with mitigations for XPath injection.
 * Changes:
 * - Avoid raw string concatenation in XPath queries.
 * - Escape user-supplied values into safe XPath string literals.
 * - Validate inputs and harden XML parser against XXE.
 */
public class UserService {
    private static final Pattern SAFE_INPUT = Pattern.compile("^[A-Za-z0-9_@.-]{1,128}$");

    // Validate user input to a conservative character set
    private static String validate(String s) {
        if (s == null || !SAFE_INPUT.matcher(s).matches()) {
            throw new IllegalArgumentException("Invalid input");
        }
        return s;
    }

    // Escape string as an XPath literal. If it contains single quotes, use concat with parts.
    private static String escapeXPathLiteral(String value) {
        if (value.indexOf('\'') == -1) {
            return "'" + value + "'";
        }
        StringBuilder sb = new StringBuilder("concat(");
        boolean first = true;
        for (String part : value.split("'", -1)) {
            if (!first) {
                sb.append(", '\'', ");
            }
            sb.append("'" + part + "'");
            first = false;
        }
        sb.append(")");
        return sb.toString();
    }

    // Hardened XML document builder (prevents XXE)
    private static DocumentBuilder newSecureDocumentBuilder() throws Exception {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
        dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        dbf.setExpandEntityReferences(false);
        dbf.setNamespaceAware(true);
        return dbf.newDocumentBuilder();
    }

    /**
     * Authenticate using an XML user store provided as InputStream.
     * Returns true if a single matching user exists.
     */
    public boolean authenticate(InputStream xmlUsers, String username, String password) throws Exception {
        String u = validate(username);
        String p = validate(password);

        DocumentBuilder builder = newSecureDocumentBuilder();
        Document doc = builder.parse(xmlUsers);

        XPath xpath = XPathFactory.newInstance().newXPath();
        String xUser = escapeXPathLiteral(u);
        String xPass = escapeXPathLiteral(p);
        String exprStr = "//user[username/text()=" + xUser + " and password/text()=" + xPass + "]";
        XPathExpression expr = xpath.compile(exprStr);
        NodeList result = (NodeList) expr.evaluate(doc, XPathConstants.NODESET);
        return result != null && result.getLength() == 1;
    }
}

