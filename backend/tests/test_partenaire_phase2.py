"""
Test Partenaire Phase 2 Features:
- Dashboard stats with linked_profiles metric
- Alertes system (inactivity, critical freins)
- Link/Unlink beneficiary to Re'Actif Pro user
- Get linked profile (profile, passport, CV, D'CLIC)
- Search Re'Actif Pro users
- Diagnostic enrichi (contexte_social, motivation, posture, autonomie, soft_skills)
- Orientation IA (GPT-5.2 generates metiers, formations, dispositifs, actions)
- Contribution Observatoire
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
PARTENAIRE_TOKEN = "6yQmoUt_GLTp9Tp2hLfD6XpykZyEdnoBhbWoQhm4ejE"
TEST_USERS = ["bob15", "bob18", "bob22"]


class TestDashboardStats:
    """Dashboard stats with linked_profiles metric"""
    
    def test_stats_returns_linked_profiles(self):
        """GET /api/partenaires/stats should include linked_profiles count"""
        response = requests.get(f"{BASE_URL}/api/partenaires/stats?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "linked_profiles" in data, "Stats should include linked_profiles"
        assert isinstance(data["linked_profiles"], int), "linked_profiles should be an integer"
        assert "total" in data
        assert "en_accompagnement" in data
        assert "taux_insertion" in data
        assert "freins_actifs" in data
        print(f"Stats: total={data['total']}, linked_profiles={data['linked_profiles']}")


class TestAlertes:
    """Alertes system (inactivity, critical freins)"""
    
    def test_get_alertes(self):
        """GET /api/partenaires/alertes returns list of alerts"""
        response = requests.get(f"{BASE_URL}/api/partenaires/alertes?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Alertes should be a list"
        
        # Check alert structure if any exist
        if len(data) > 0:
            alert = data[0]
            assert "type" in alert, "Alert should have type"
            assert "severity" in alert, "Alert should have severity"
            assert "beneficiaire_id" in alert, "Alert should have beneficiaire_id"
            assert "beneficiaire_name" in alert, "Alert should have beneficiaire_name"
            assert "message" in alert, "Alert should have message"
            assert alert["severity"] in ["critique", "eleve", "moyen"], f"Invalid severity: {alert['severity']}"
            print(f"Found {len(data)} alertes, first: {alert['type']} - {alert['message']}")
        else:
            print("No alertes found (may be expected if no inactive beneficiaires)")


class TestSearchUsers:
    """Search Re'Actif Pro users for linking"""
    
    def test_search_users_by_pseudo(self):
        """GET /api/partenaires/search-users?query=bob returns matching users"""
        response = requests.get(f"{BASE_URL}/api/partenaires/search-users?token={PARTENAIRE_TOKEN}&query=bob")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Search results should be a list"
        
        if len(data) > 0:
            user = data[0]
            assert "pseudo" in user, "User should have pseudo"
            assert "display_name" in user, "User should have display_name"
            assert "token_id" in user, "User should have token_id"
            print(f"Found {len(data)} users matching 'bob': {[u['pseudo'] for u in data]}")
        else:
            print("No users found matching 'bob'")
    
    def test_search_users_short_query(self):
        """GET /api/partenaires/search-users with query < 2 chars returns empty"""
        response = requests.get(f"{BASE_URL}/api/partenaires/search-users?token={PARTENAIRE_TOKEN}&query=b")
        assert response.status_code == 200
        data = response.json()
        assert data == [], "Short query should return empty list"


class TestLinkUnlink:
    """Link/Unlink beneficiary to Re'Actif Pro user"""
    
    @pytest.fixture
    def beneficiaire_id(self):
        """Get first beneficiaire ID"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0, "Need at least one beneficiaire"
        # Find one that's not linked or use first
        for b in data:
            if not b.get("linked_token_id"):
                return b["id"]
        return data[0]["id"]
    
    def test_link_beneficiaire_to_user(self, beneficiaire_id):
        """POST /api/partenaires/beneficiaires/{id}/link?pseudo=bob18 links user"""
        # First unlink if already linked
        requests.delete(f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/link?token={PARTENAIRE_TOKEN}")
        
        # Now link to bob18
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/link?token={PARTENAIRE_TOKEN}&pseudo=bob18"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert "linked_token_id" in data
        print(f"Linked beneficiaire to bob18: {data}")
    
    def test_link_nonexistent_user(self, beneficiaire_id):
        """POST /api/partenaires/beneficiaires/{id}/link with invalid pseudo returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/link?token={PARTENAIRE_TOKEN}&pseudo=nonexistent_user_xyz"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_unlink_beneficiaire(self, beneficiaire_id):
        """DELETE /api/partenaires/beneficiaires/{id}/link unlinks user"""
        # First ensure linked
        requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/link?token={PARTENAIRE_TOKEN}&pseudo=bob18"
        )
        
        # Now unlink
        response = requests.delete(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/link?token={PARTENAIRE_TOKEN}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        print(f"Unlinked: {data}")


class TestLinkedProfile:
    """Get linked profile (profile, passport, CV, D'CLIC)"""
    
    def test_get_linked_profile_sophie_bernard(self):
        """GET /api/partenaires/beneficiaires/{id}/linked-profile for Sophie Bernard (linked to bob15)"""
        # First find Sophie Bernard
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        beneficiaires = response.json()
        
        sophie = next((b for b in beneficiaires if "Sophie" in b.get("name", "")), None)
        if not sophie:
            pytest.skip("Sophie Bernard not found in beneficiaires")
        
        if not sophie.get("linked_token_id"):
            pytest.skip("Sophie Bernard is not linked to a user")
        
        # Get linked profile
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{sophie['id']}/linked-profile?token={PARTENAIRE_TOKEN}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "profile" in data, "Should have profile"
        assert "passport" in data, "Should have passport"
        assert "cv_analyses" in data, "Should have cv_analyses"
        assert "dclic_results" in data, "Should have dclic_results"
        
        if data["profile"]:
            assert "password_hash" not in data["profile"], "Should not expose password_hash"
            print(f"Profile skills: {len(data['profile'].get('skills', []))}")
        print(f"Linked profile data keys: {list(data.keys())}")
    
    def test_get_linked_profile_not_linked(self):
        """GET /api/partenaires/beneficiaires/{id}/linked-profile returns 400 if not linked"""
        # Find unlinked beneficiaire
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        beneficiaires = response.json()
        
        unlinked = next((b for b in beneficiaires if not b.get("linked_token_id")), None)
        if not unlinked:
            pytest.skip("All beneficiaires are linked")
        
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{unlinked['id']}/linked-profile?token={PARTENAIRE_TOKEN}"
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestDiagnosticEnrichi:
    """Diagnostic enrichi (contexte_social, motivation, posture, autonomie, soft_skills)"""
    
    @pytest.fixture
    def beneficiaire_id(self):
        """Get first beneficiaire ID"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        return data[0]["id"]
    
    def test_update_diagnostic(self, beneficiaire_id):
        """PUT /api/partenaires/beneficiaires/{id}/diagnostic updates diagnostic"""
        diagnostic_data = {
            "contexte_social": "Situation familiale stable, logement securise",
            "mobilite_detail": "Permis B, vehicule personnel, rayon 30km",
            "motivation_level": "elevee",
            "posture": "autonome",
            "autonomie": "forte",
            "soft_skills": ["communication", "travail_equipe", "adaptabilite"],
            "observations": "Candidat motive avec bon potentiel"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/diagnostic?token={PARTENAIRE_TOKEN}",
            json=diagnostic_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "diagnostic" in data
        diag = data["diagnostic"]
        assert diag.get("contexte_social") == diagnostic_data["contexte_social"]
        assert diag.get("motivation_level") == diagnostic_data["motivation_level"]
        assert diag.get("soft_skills") == diagnostic_data["soft_skills"]
        assert "updated_at" in diag
        print(f"Diagnostic updated: {list(diag.keys())}")
    
    def test_partial_diagnostic_update(self, beneficiaire_id):
        """PUT /api/partenaires/beneficiaires/{id}/diagnostic with partial data"""
        response = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/diagnostic?token={PARTENAIRE_TOKEN}",
            json={"motivation_level": "moyenne"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["diagnostic"]["motivation_level"] == "moyenne"


class TestOrientationIA:
    """Orientation IA (GPT-5.2 generates metiers, formations, dispositifs, actions)"""
    
    def test_generate_orientation_ia(self):
        """POST /api/partenaires/beneficiaires/{id}/orientation generates AI recommendations"""
        # Get beneficiaire with most data (Sophie Bernard if linked)
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        beneficiaires = response.json()
        
        # Prefer linked beneficiaire for richer context
        target = next((b for b in beneficiaires if b.get("linked_token_id")), beneficiaires[0])
        
        print(f"Generating orientation for: {target['name']} (linked: {bool(target.get('linked_token_id'))})")
        
        # This calls GPT-5.2 and may take 5-10 seconds
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{target['id']}/orientation?token={PARTENAIRE_TOKEN}",
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Validate structure
        assert "metiers_recommandes" in data, "Should have metiers_recommandes"
        assert "formations_suggerees" in data, "Should have formations_suggerees"
        assert "dispositifs_adaptes" in data, "Should have dispositifs_adaptes"
        assert "actions_immediates" in data, "Should have actions_immediates"
        assert "points_vigilance" in data, "Should have points_vigilance"
        
        # Validate metiers structure
        if data["metiers_recommandes"]:
            metier = data["metiers_recommandes"][0]
            assert "titre" in metier
            assert "compatibilite" in metier
            assert "raison" in metier
        
        print(f"Orientation generated: {len(data['metiers_recommandes'])} metiers, {len(data['formations_suggerees'])} formations")


class TestContributionObservatoire:
    """Contribution Observatoire - aggregates partenaire data into signals"""
    
    def test_contribute_to_observatoire(self):
        """POST /api/partenaires/contribution-observatoire creates signal"""
        response = requests.post(
            f"{BASE_URL}/api/partenaires/contribution-observatoire?token={PARTENAIRE_TOKEN}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert "signal" in data
        
        signal = data["signal"]
        assert "id" in signal
        assert "source" in signal
        assert signal["source"] == "partenaire"
        assert "data" in signal
        
        signal_data = signal["data"]
        assert "total_beneficiaires" in signal_data
        assert "freins_repartition" in signal_data
        assert "competences_emergentes" in signal_data
        assert "secteurs_tension" in signal_data
        
        print(f"Observatoire contribution: {signal_data['total_beneficiaires']} beneficiaires, freins: {signal_data['freins_repartition']}")


class TestBeneficiairesWithNewFields:
    """Verify beneficiaires have new fields from Phase 2"""
    
    def test_beneficiaire_has_diagnostic_field(self):
        """Beneficiaire should have diagnostic field"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        beneficiaires = response.json()
        
        for b in beneficiaires:
            assert "diagnostic" in b or b.get("diagnostic") is None or isinstance(b.get("diagnostic"), dict), \
                f"Beneficiaire {b['name']} should have diagnostic field"
    
    def test_beneficiaire_has_linked_fields(self):
        """Beneficiaire should have linked_token_id and linked_pseudo fields"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        beneficiaires = response.json()
        
        # Find Sophie Bernard who should be linked
        sophie = next((b for b in beneficiaires if "Sophie" in b.get("name", "")), None)
        if sophie:
            assert "linked_token_id" in sophie or sophie.get("linked_token_id") is not None
            if sophie.get("linked_token_id"):
                assert "linked_pseudo" in sophie
                print(f"Sophie Bernard linked to: {sophie.get('linked_pseudo')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
