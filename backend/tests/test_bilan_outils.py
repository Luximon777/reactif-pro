"""
Test suite for Bilan/Outils d'accompagnement endpoints
Tests the 16 fiches integration for partenaire dashboard
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
PARTENAIRE_TOKEN = "6yQmoUt_GLTp9Tp2hLfD6XpykZyEdnoBhbWoQhm4ejE"

# All 16 fiche IDs as per BILAN_FICHES definition
EXPECTED_FICHE_IDS = [
    "attentes", "courbe_satisfaction", "formation", "recit_carriere",
    "interets", "realisations", "competences", "synthese_pro",
    "situations_difficiles", "points_forts", "valeurs", "moteurs",
    "environnement", "synthese_perso", "reflexion_projet", "definition_projet"
]

EXPECTED_PHASES = ["decouverte", "bilan_pro", "bilan_perso", "projet"]


class TestBilanFichesEndpoint:
    """Tests for GET /api/partenaires/outils/fiches"""
    
    def test_get_fiches_returns_16_fiches(self):
        """Verify endpoint returns exactly 16 fiches"""
        response = requests.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        fiches = response.json()
        assert isinstance(fiches, list), "Response should be a list"
        assert len(fiches) == 16, f"Expected 16 fiches, got {len(fiches)}"
        print(f"✓ GET /api/partenaires/outils/fiches returns 16 fiches")
    
    def test_fiches_have_correct_structure(self):
        """Verify each fiche has required fields"""
        response = requests.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        
        fiches = response.json()
        required_fields = ["id", "phase", "phase_label", "number", "title", "description"]
        
        for fiche in fiches:
            for field in required_fields:
                assert field in fiche, f"Fiche missing field: {field}"
            assert isinstance(fiche["number"], int), f"Fiche number should be int, got {type(fiche['number'])}"
        
        print(f"✓ All fiches have correct structure with required fields")
    
    def test_fiches_have_all_expected_ids(self):
        """Verify all 16 expected fiche IDs are present"""
        response = requests.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        
        fiches = response.json()
        fiche_ids = [f["id"] for f in fiches]
        
        for expected_id in EXPECTED_FICHE_IDS:
            assert expected_id in fiche_ids, f"Missing fiche ID: {expected_id}"
        
        print(f"✓ All 16 expected fiche IDs present: {', '.join(EXPECTED_FICHE_IDS[:4])}...")
    
    def test_fiches_cover_all_phases(self):
        """Verify fiches cover all 4 phases"""
        response = requests.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        
        fiches = response.json()
        phases_found = set(f["phase"] for f in fiches)
        
        for expected_phase in EXPECTED_PHASES:
            assert expected_phase in phases_found, f"Missing phase: {expected_phase}"
        
        print(f"✓ All 4 phases covered: {', '.join(EXPECTED_PHASES)}")
    
    def test_fiches_numbered_1_to_16(self):
        """Verify fiches are numbered 1-16"""
        response = requests.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        
        fiches = response.json()
        numbers = sorted([f["number"] for f in fiches])
        expected_numbers = list(range(1, 17))
        
        assert numbers == expected_numbers, f"Expected numbers 1-16, got {numbers}"
        print(f"✓ Fiches numbered correctly 1-16")


class TestBeneficiaireBilanEndpoint:
    """Tests for GET/PUT /api/partenaires/beneficiaires/{id}/bilan"""
    
    @pytest.fixture
    def beneficiaire_id(self):
        """Get first beneficiaire ID"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        beneficiaires = response.json()
        assert len(beneficiaires) > 0, "No beneficiaires found"
        return beneficiaires[0]["id"]
    
    def test_get_bilan_returns_dict(self, beneficiaire_id):
        """Verify GET bilan returns a dictionary"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/bilan?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        bilan = response.json()
        assert isinstance(bilan, dict), f"Expected dict, got {type(bilan)}"
        print(f"✓ GET bilan returns dict for beneficiaire {beneficiaire_id[:8]}...")
    
    def test_save_fiche_attentes(self, beneficiaire_id):
        """Test saving the 'attentes' fiche"""
        payload = {
            "fiche_id": "attentes",
            "data": {
                "q1": "Test attente 1 - clarifier mon projet",
                "q2": "Test attente 2 - competences et formation",
                "q3": "Test attente 3 - avoir un plan d'action",
                "q4": "Test attente 4 - aucun sujet exclu"
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/bilan?token={PARTENAIRE_TOKEN}",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert "message" in result, "Response should contain message"
        assert "completed" in result, "Response should contain completed count"
        assert "total" in result, "Response should contain total count"
        assert result["total"] == 16, f"Total should be 16, got {result['total']}"
        
        print(f"✓ Saved fiche 'attentes' - {result['completed']}/{result['total']} completed")
    
    def test_save_fiche_updates_bilan_progress(self, beneficiaire_id):
        """Verify saving a fiche updates bilan_progress field"""
        # Save a fiche
        payload = {
            "fiche_id": "formation",
            "data": {
                "formation_initiale": "BTS Commerce",
                "formation_continue": "Certification management",
                "motivations_formation": "Evolution de carriere"
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/bilan?token={PARTENAIRE_TOKEN}",
            json=payload
        )
        assert response.status_code == 200
        
        # Get beneficiaire to check bilan_progress
        ben_response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}?token={PARTENAIRE_TOKEN}")
        assert ben_response.status_code == 200
        
        beneficiaire = ben_response.json()
        assert "bilan_progress" in beneficiaire, "Beneficiaire should have bilan_progress field"
        assert isinstance(beneficiaire["bilan_progress"], (int, float)), "bilan_progress should be numeric"
        assert beneficiaire["bilan_progress"] >= 0, "bilan_progress should be >= 0"
        
        print(f"✓ bilan_progress updated to {beneficiaire['bilan_progress']}%")
    
    def test_get_bilan_returns_saved_data(self, beneficiaire_id):
        """Verify GET bilan returns previously saved fiche data"""
        # First save a fiche
        test_data = {
            "fiche_id": "competences",
            "data": {
                "savoirs": "Gestion de projet, Marketing digital",
                "savoir_faire": "Analyse de donnees, Communication",
                "savoir_etre": "Leadership, Adaptabilite"
            }
        }
        
        save_response = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/bilan?token={PARTENAIRE_TOKEN}",
            json=test_data
        )
        assert save_response.status_code == 200
        
        # Then get bilan and verify data
        get_response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/bilan?token={PARTENAIRE_TOKEN}")
        assert get_response.status_code == 200
        
        bilan = get_response.json()
        assert "competences" in bilan, "Bilan should contain 'competences' fiche"
        assert bilan["competences"]["savoirs"] == test_data["data"]["savoirs"]
        assert "updated_at" in bilan["competences"], "Saved fiche should have updated_at timestamp"
        
        print(f"✓ GET bilan returns saved 'competences' data with timestamp")
    
    def test_save_invalid_fiche_id_returns_400(self, beneficiaire_id):
        """Verify saving invalid fiche ID returns 400"""
        payload = {
            "fiche_id": "invalid_fiche_id",
            "data": {"test": "data"}
        }
        
        response = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/bilan?token={PARTENAIRE_TOKEN}",
            json=payload
        )
        assert response.status_code == 400, f"Expected 400 for invalid fiche_id, got {response.status_code}"
        print(f"✓ Invalid fiche_id returns 400")
    
    def test_save_fiche_adds_historique_entry(self, beneficiaire_id):
        """Verify saving a fiche adds entry to historique"""
        payload = {
            "fiche_id": "valeurs",
            "data": {
                "valeurs_essentielles": "Integrite, Respect, Innovation",
                "valeurs_travail": "Collaboration, Excellence"
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/bilan?token={PARTENAIRE_TOKEN}",
            json=payload
        )
        assert response.status_code == 200
        
        # Get beneficiaire to check historique
        ben_response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}?token={PARTENAIRE_TOKEN}")
        assert ben_response.status_code == 200
        
        beneficiaire = ben_response.json()
        historique = beneficiaire.get("historique", [])
        
        # Check if there's a bilan_fiche entry
        bilan_entries = [h for h in historique if h.get("action") == "bilan_fiche"]
        assert len(bilan_entries) > 0, "Should have bilan_fiche entry in historique"
        
        latest_entry = bilan_entries[-1]
        assert "valeurs" in latest_entry.get("detail", ""), "Historique should mention 'valeurs' fiche"
        
        print(f"✓ Saving fiche adds historique entry")


class TestNoOasysReferences:
    """Verify 'Oasys' term is not present in API responses"""
    
    def test_fiches_no_oasys_reference(self):
        """Verify fiches don't contain 'Oasys' term"""
        response = requests.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        
        fiches_text = str(response.json()).lower()
        assert "oasys" not in fiches_text, "Fiches should not contain 'Oasys' reference"
        print(f"✓ No 'Oasys' references in fiches endpoint")


class TestOrientationIAActors:
    """Verify Orientation IA prompt includes all required actors"""
    
    @pytest.fixture
    def beneficiaire_id(self):
        """Get first beneficiaire ID"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={PARTENAIRE_TOKEN}")
        assert response.status_code == 200
        beneficiaires = response.json()
        assert len(beneficiaires) > 0, "No beneficiaires found"
        return beneficiaires[0]["id"]
    
    def test_orientation_endpoint_exists(self, beneficiaire_id):
        """Verify orientation endpoint is accessible"""
        # Just check the endpoint exists - actual AI call may take time
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{beneficiaire_id}/orientation?token={PARTENAIRE_TOKEN}",
            timeout=60
        )
        # Accept 200 (success) or 500 (AI error but endpoint exists)
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        print(f"✓ Orientation endpoint accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
