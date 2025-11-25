package com.port.service;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.regex.Pattern;

/**
 * UserService with safe XPath handling to prevent XPath injection.
 * This implementation avoids direct concatenation of untrusted input into XPath queries
 * by strictly validating inputs and safely escaping string literals used in XPath.
 */
public class UserService {
    // Allow only reasonable username/password characters; adjust as needed
    private static final Pattern SAFE_INPUT = Pattern.compile("^[a-zA-Z0-9._@-]{1,128}$");

    /**
     * Authenticate user against users.xml resource using safe XPath.
     * Returns true if a matching user element is found.
     */
    public boolean authenticate(String username, String password) throws Exception {
        if (!isSafe(username) || !isSafe(password)) {
            // Reject potentially dangerous input early
            return false;
        }

        Document doc = loadUsersXml();
        XPath xpath = XPathFactory.newInstance().newXPath();

        // Safely embed literals by escaping quotes for XPath
        String u = xpathStringLiteral(username);
        String p = xpathStringLiteral(password);

        String expr = "//user[username=" + u + " and password=" + p + "]";
        XPathExpression compiled = xpath.compile(expr);
        NodeList nodes = (NodeList) compiled.evaluate(doc, XPathConstants.NODESET);
        return nodes != null && nodes.getLength() > 0;
    }

    private boolean isSafe(String s) {
        return s != null && SAFE_INPUT.matcher(s).matches();
    }

    /**
     * Load users.xml with XXE protections enabled.
     */
    private Document loadUsersXml() throws Exception {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        // Prevent XXE
        dbf.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        dbf.setAttribute("http://apache.org/xml/features/disallow-doctype-decl", true);
        dbf.setExpandEntityReferences(false);
        dbf.setXIncludeAware(false);

        DocumentBuilder builder = dbf.newDocumentBuilder();
        try (InputStream is = getClass().getClassLoader().getResourceAsStream("users.xml")) {
            if (is == null) {
                throw new IllegalStateException("users.xml not found on classpath");
            }
            return builder.parse(is);
        }
    }

    /**
     * Escape a Java string into a safe XPath string literal.
     * If it contains single quotes, use concat to build the literal safely.
     * See: https://www.w3.org/TR/xpath-31/#id-string-literals
     */
    private String xpathStringLiteral(String value) {
        if (value.indexOf('\'') == -1) {
            return "'" + value + "'"; // simple quoted literal
        }
        // Split on single quotes and use concat with embedded quote token
        String[] parts = value.split("'");
        StringBuilder sb = new StringBuilder("concat(");
        for (int i = 0; i < parts.length; i++) {
            if (i > 0) sb.append(", '\'', ");
            sb.append("'" + parts[i] + "'");
        }
        sb.append(")");
        return sb.toString();
    }
}

