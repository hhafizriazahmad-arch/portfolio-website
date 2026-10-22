import os
import sys
import unittest
import json
import xml.etree.ElementTree as ET

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app, seed_projects, seed_settings

class PortfolioSEOTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_projects()
        seed_settings()
        cls.client = TestClient(app)

    def test_homepage_status_and_headers(self):
        """Test homepage returns 200 OK with correct content type and caching header."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("public", response.headers.get("Cache-Control", ""))

    def test_homepage_seo_title_and_description(self):
        """Test homepage contains the required exact title and meta description."""
        response = self.client.get("/")
        html = response.text

        # Title check
        expected_title = "<title>Riaz Ahmad | AI Automation Engineer & Developer</title>"
        self.assertIn(expected_title, html)

        # Meta description check
        expected_desc = 'content="Build practical AI automation systems, lead-generation workflows, API integrations, and Python backend solutions for growing businesses."'
        self.assertIn(expected_desc, html)

    def test_canonical_and_open_graph(self):
        """Test canonical link and Open Graph tags point to verified production URL."""
        response = self.client.get("/")
        html = response.text

        # Canonical tag
        expected_canonical = '<link rel="canonical" href="https://portfolio-website-ten-lyart-11.vercel.app/">'
        self.assertIn(expected_canonical, html)

        # OG URL
        self.assertIn('<meta property="og:url" content="https://portfolio-website-ten-lyart-11.vercel.app/">', html)
        self.assertIn('<meta property="og:title" content="Riaz Ahmad | AI Automation Engineer & Developer">', html)
        self.assertIn('meta property="og:image"', html)

        # Twitter card
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
        self.assertIn('<meta name="twitter:title" content="Riaz Ahmad | AI Automation Engineer & Developer">', html)

    def test_structured_data_json_ld(self):
        """Validate JSON-LD schema syntax and schema graph nodes."""
        response = self.client.get("/")
        html = response.text

        # Extract JSON-LD
        start_tag = '<script type="application/ld+json">'
        end_tag = '</script>'
        self.assertIn(start_tag, html)
        start_idx = html.find(start_tag) + len(start_tag)
        end_idx = html.find(end_tag, start_idx)
        raw_json = html[start_idx:end_idx].strip()

        schema_data = json.loads(raw_json)
        self.assertEqual(schema_data.get("@context"), "https://schema.org")
        graph = schema_data.get("@graph", [])
        types = [item.get("@type") for item in graph]

        self.assertIn("WebSite", types)
        self.assertIn("Person", types)
        self.assertIn("ProfessionalService", types)

        person = next(item for item in graph if item.get("@type") == "Person")
        self.assertEqual(person.get("name"), "Riaz Ahmad")
        self.assertEqual(person.get("jobTitle"), "AI Automation Engineer & Developer")
        self.assertIn("https://github.com/hhafizriazahmad-arch", person.get("sameAs", []))

    def test_heading_hierarchy_and_h1(self):
        """Verify presence of single appropriate primary H1 and logical H2 sections."""
        response = self.client.get("/")
        html = response.text

        # Single H1 tag check
        h1_open_count = html.count("<h1")
        h1_close_count = html.count("</h1>")
        self.assertEqual(h1_open_count, 1)
        self.assertEqual(h1_close_count, 1)
        self.assertIn("AI Automation Systems", html)

        # Semantic H2 tags
        self.assertIn("Solutions & Engineering Capabilities", html)
        self.assertIn("Core Automation Specializations", html)
        self.assertIn("Case Studies & Deployed Systems", html)
        self.assertIn("About Riaz Ahmad", html)
        self.assertIn("Discuss Your Automation Project", html)

    def test_prerendered_case_studies(self):
        """Verify all 4 case studies are statically rendered and visible without dynamic JS delay."""
        response = self.client.get("/")
        html = response.text

        # The spinner text MUST NOT be present in the initial static HTML
        self.assertNotIn("Loading HR Autonomous case studies...", html)

        # All 4 project titles must be prerendered inside article tags
        self.assertIn("AI Agency Operating System", html)
        self.assertIn("AI Lead Intelligence System", html)
        self.assertIn("Digital Marketing Automation Suite", html)
        self.assertIn("Onboarding Automation Workflow", html)

    def test_robots_txt(self):
        """Test /robots.txt endpoint and directives."""
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.headers.get("content-type", ""))
        body = response.text
        self.assertIn("User-agent: *", body)
        self.assertIn("Allow: /", body)
        self.assertIn("Allow: /static/", body)
        self.assertIn("Disallow: /api/", body)
        self.assertIn("Sitemap: https://portfolio-website-ten-lyart-11.vercel.app/sitemap.xml", body)

    def test_sitemap_xml(self):
        """Test /sitemap.xml endpoint and XML structure."""
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response.headers.get("content-type", ""))
        
        # Parse XML to verify valid syntax
        root = ET.fromstring(response.text)
        namespaces = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [loc.text for loc in root.findall(".//s:loc", namespaces)]
        self.assertIn("https://portfolio-website-ten-lyart-11.vercel.app/", locs)

    def test_projects_api_endpoint(self):
        """Test /api/projects returns the 4 seeded projects with correct schemas."""
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 200)
        projects = response.json()
        self.assertIsInstance(projects, list)
        self.assertGreaterEqual(len(projects), 4)

        titles = [p.get("title") for p in projects]
        self.assertIn("AI Agency Operating System", titles)
        self.assertIn("AI Lead Intelligence System", titles)
        self.assertIn("Digital Marketing Automation Suite", titles)
        self.assertIn("Onboarding Automation Workflow", titles)

    def test_crm_status_api(self):
        """Test /api/crm/status endpoint returns online."""
        response = self.client.get("/api/crm/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("system_status"), "online")
        self.assertIn("total_projects", data)

    def test_contact_submission_api(self):
        """Test submitting the contact form via API."""
        payload = {
            "name": "Audit Verification Tester",
            "email": "tester@example.com",
            "subject": "SEO and Systems Verification",
            "message": "Validating contact form processing and audit log pipeline."
        }
        response = self.client.post("/api/contact", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data.get("name"), payload["name"])
        self.assertEqual(data.get("email"), payload["email"])

    def test_cache_control_headers_differentiation(self):
        """Test API endpoints get no-store, and static files get caching."""
        # API endpoint should not be cached
        api_resp = self.client.get("/api/projects")
        self.assertIn("no-store", api_resp.headers.get("Cache-Control", ""))

        # Static asset should be cached
        static_resp = self.client.get("/static/css/style.css")
        self.assertEqual(static_resp.status_code, 200)
        self.assertIn("public", static_resp.headers.get("Cache-Control", ""))

if __name__ == "__main__":
    unittest.main()
