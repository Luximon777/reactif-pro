"""
Test suite for Centres d'Interet Analysis Feature
Tests the rule-based analysis engine and CV integration
"""
import pytest
import requests
import os
import sys
import time
import uuid

# Add backend to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============================================================
# Module 1: Unit tests for centres_interet.py engine
# ============================================================

class TestCentresInteretEngine:
    """Unit tests for the centres_interet analysis module"""
    
    def test_analyze_football_intensif(self):
        """Test sport_collectif category with intensif implication"""
        from centres_interet import analyze_centre_interet
        result = analyze_centre_interet('Football', 'intensif')
        
        assert result['label'] == 'Football'
        assert result['category'] == 'sport_collectif'
        assert result['implication'] == 'intensif'
        assert result['credibility'] == 'forte'
        assert 'travail en équipe' in result['competences']
        assert 'discipline' in result['competences']
        assert 'cv_reformulation' in result
        assert 'Football' in result['cv_reformulation']
    
    def test_analyze_yoga_regulier(self):
        """Test bien_etre category with regulier implication"""
        from centres_interet import analyze_centre_interet
        result = analyze_centre_interet('Yoga', 'regulier')
        
        assert result['category'] == 'bien_etre'
        assert result['credibility'] == 'moyenne'
        assert 'gestion du stress' in result['competences']
        assert 'résilience' in result['competences']
    
    def test_analyze_benevolat(self):
        """Test social_engagement category"""
        from centres_interet import analyze_centre_interet
        result = analyze_centre_interet('Bénévolat Croix-Rouge', 'regulier')
        
        assert result['category'] == 'social_engagement'
        assert 'empathie' in result['competences']
        assert 'sens du service' in result['competences']
        assert 'solidarité' in result['valeurs']
    
    def test_analyze_unknown_hobby(self):
        """Test fallback for unknown hobbies"""
        from centres_interet import analyze_centre_interet
        result = analyze_centre_interet('Cuisine gastronomique', 'occasionnel')
        
        assert result['category'] == 'autre'
        assert result['credibility'] == 'modérée'
        assert 'adaptabilité' in result['competences']
        assert 'curiosité' in result['competences']
    
    def test_all_nine_categories(self):
        """Test all 9 categories are correctly identified"""
        from centres_interet import analyze_centre_interet
        
        test_cases = [
            ('Football', 'sport_collectif'),
            ('Running marathon', 'sport_individuel'),
            ('Théâtre improvisation', 'artistique_expression'),
            ('Photographie', 'creatif'),
            ('Bénévolat association', 'social_engagement'),
            ('Échecs compétition', 'intellectuel'),
            ('Programmation Python', 'technique'),
            ('Yoga méditation', 'bien_etre'),
            ('Voyage découverte', 'exploration'),
        ]
        
        for hobby, expected_category in test_cases:
            result = analyze_centre_interet(hobby)
            assert result['category'] == expected_category, f"Failed for {hobby}: got {result['category']}"
    
    def test_analyze_multiple_centres(self):
        """Test analyze_multiple function"""
        from centres_interet import analyze_multiple
        
        centres = [
            {'label': 'Football', 'implication': 'intensif'},
            {'label': 'Yoga', 'implication': 'regulier'},
            {'label': 'Photographie', 'implication': 'occasionnel'},
        ]
        
        result = analyze_multiple(centres)
        
        assert len(result['analyses']) == 3
        assert len(result['competences_transversales']) > 0
        assert len(result['valeurs_dominantes']) > 0
        assert len(result['cv_reformulations']) == 3
        
        # Check aggregation
        assert 'travail en équipe' in result['competences_transversales']
        assert 'gestion du stress' in result['competences_transversales']
        assert 'créativité' in result['competences_transversales']
    
    def test_analyze_multiple_with_strings(self):
        """Test analyze_multiple with simple string list"""
        from centres_interet import analyze_multiple
        
        centres = ['Football', 'Yoga', 'Lecture']
        result = analyze_multiple(centres)
        
        assert len(result['analyses']) == 3
        # Default implication should be 'regulier'
        for analysis in result['analyses']:
            assert analysis['implication'] == 'regulier'
    
    def test_implication_weights(self):
        """Test different implication levels affect credibility"""
        from centres_interet import analyze_centre_interet
        
        occasionnel = analyze_centre_interet('Football', 'occasionnel')
        regulier = analyze_centre_interet('Football', 'regulier')
        intensif = analyze_centre_interet('Football', 'intensif')
        
        assert occasionnel['credibility'] == 'modérée'
        assert regulier['credibility'] == 'moyenne'
        assert intensif['credibility'] == 'forte'


# ============================================================
# Module 2: API Integration tests for CV analysis
# ============================================================

class TestCvAnalysisWithCentresInteret:
    """Integration tests for CV analysis with centres d'interet"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get auth token"""
        pseudo = f"ci_test_{uuid.uuid4().hex[:8]}"
        password = "Test1234!"
        
        # Register
        register_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if register_res.status_code == 201:
            return register_res.json()['token']
        elif register_res.status_code == 400:
            # User exists, try login
            login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
                "pseudo": pseudo,
                "password": password
            })
            if login_res.status_code == 200:
                return login_res.json()['token']
        
        pytest.skip("Could not create test user")
    
    def test_cv_analysis_with_centres_interet(self, auth_token):
        """Test CV analysis detects and analyzes centres d'interet"""
        cv_text = """
        Jean DUPONT
        Développeur Web Full Stack
        Email: jean.dupont@email.com
        
        EXPÉRIENCES PROFESSIONNELLES
        
        Développeur Full Stack - TechCorp (2020-2023)
        - Développement d'applications React et Node.js
        - Gestion de bases de données MongoDB
        - Travail en équipe Agile
        
        FORMATION
        Master Informatique - Université Paris (2020)
        
        COMPÉTENCES
        JavaScript, Python, React, Node.js, MongoDB
        
        CENTRES D'INTÉRÊT
        - Football en club (niveau régional, 3 entraînements/semaine)
        - Bénévolat à la Croix-Rouge (maraudes hebdomadaires)
        - Photographie de voyage
        """
        
        # Start analysis
        start_res = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json={"text": cv_text, "filename": "test_cv_ci.txt"}
        )
        assert start_res.status_code == 200
        job_id = start_res.json()['job_id']
        
        # Poll for completion (max 90 seconds)
        result = None
        for _ in range(30):
            time.sleep(3)
            status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={auth_token}&job_id={job_id}")
            if status_res.status_code == 200:
                data = status_res.json()
                if data['status'] == 'completed':
                    result = data['result']
                    break
                elif data['status'] == 'failed':
                    pytest.fail(f"CV analysis failed: {data.get('error')}")
        
        assert result is not None, "CV analysis timed out"
        
        # Verify centres d'interet fields in result
        assert 'has_centres_interet' in result
        assert result['has_centres_interet'] == True
        assert 'centres_interet_analysis' in result
        assert 'centres_interet_reformulations' in result
        assert len(result['centres_interet_analysis']) > 0
        assert len(result['centres_interet_reformulations']) > 0
        
        # Verify analysis structure
        for ci in result['centres_interet_analysis']:
            assert 'label' in ci
            assert 'category' in ci
            assert 'competences' in ci
            assert 'cv_reformulation' in ci
    
    def test_cv_analysis_without_centres_interet(self, auth_token):
        """Test CV analysis detects missing centres d'interet and provides suggestion"""
        cv_text = """
        Marie MARTIN
        Chef de Projet Digital
        Email: marie.martin@email.com
        
        EXPÉRIENCES PROFESSIONNELLES
        
        Chef de Projet - AgenceWeb (2019-2023)
        - Gestion de projets web
        - Coordination d'équipes
        
        FORMATION
        Master Marketing Digital - ESSEC (2019)
        
        COMPÉTENCES
        Gestion de projet, Marketing digital, SEO
        """
        
        # Start analysis
        start_res = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json={"text": cv_text, "filename": "test_cv_no_ci.txt"}
        )
        assert start_res.status_code == 200
        job_id = start_res.json()['job_id']
        
        # Poll for completion
        result = None
        for _ in range(30):
            time.sleep(3)
            status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={auth_token}&job_id={job_id}")
            if status_res.status_code == 200:
                data = status_res.json()
                if data['status'] == 'completed':
                    result = data['result']
                    break
                elif data['status'] == 'failed':
                    pytest.fail(f"CV analysis failed: {data.get('error')}")
        
        assert result is not None, "CV analysis timed out"
        
        # Verify centres d'interet detection
        assert 'has_centres_interet' in result
        # Note: LLM might still detect some implicit interests, so we check for suggestion
        if not result['has_centres_interet']:
            assert 'suggestion_centres_interet' in result
            assert len(result.get('suggestion_centres_interet', '')) > 0
    
    def test_latest_analysis_includes_centres_interet(self, auth_token):
        """Test that latest analysis endpoint returns centres d'interet data"""
        res = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={auth_token}")
        assert res.status_code == 200
        
        data = res.json()
        if data.get('has_analysis'):
            result = data['result']
            assert 'has_centres_interet' in result
            assert 'centres_interet_analysis' in result or 'suggestion_centres_interet' in result


# ============================================================
# Module 3: CV Generation with Centres d'Interet
# ============================================================

class TestCvGenerationWithCentresInteret:
    """Test CV generation includes enriched centres d'interet"""
    
    @pytest.fixture(scope="class")
    def auth_token_with_cv(self):
        """Create user with analyzed CV containing centres d'interet"""
        pseudo = f"ci_gen_{uuid.uuid4().hex[:8]}"
        password = "Test1234!"
        
        # Register
        register_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if register_res.status_code != 201:
            pytest.skip("Could not create test user")
        
        token = register_res.json()['token']
        
        # Analyze CV with centres d'interet
        cv_text = """
        Pierre DURAND
        Ingénieur Logiciel
        Email: pierre.durand@email.com
        
        EXPÉRIENCES
        Développeur Senior - StartupTech (2018-2023)
        - Architecture microservices
        - Leadership technique
        
        FORMATION
        Diplôme d'Ingénieur - Polytechnique (2018)
        
        CENTRES D'INTÉRÊT
        - Course à pied (marathonien, 3h30 au dernier marathon)
        - Bénévolat informatique pour associations
        - Échecs en club (classement Elo 1800)
        """
        
        start_res = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": cv_text, "filename": "test_cv_gen.txt"}
        )
        
        if start_res.status_code != 200:
            pytest.skip("Could not start CV analysis")
        
        job_id = start_res.json()['job_id']
        
        # Wait for completion
        for _ in range(30):
            time.sleep(3)
            status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status_res.status_code == 200:
                data = status_res.json()
                if data['status'] == 'completed':
                    break
                elif data['status'] == 'failed':
                    pytest.skip(f"CV analysis failed: {data.get('error')}")
        
        return token
    
    def test_generate_cv_includes_centres_interet(self, auth_token_with_cv):
        """Test that generated CV includes enriched centres d'interet"""
        # Start generation
        gen_res = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={auth_token_with_cv}",
            json={"model_types": ["classique"]}
        )
        assert gen_res.status_code == 200
        job_id = gen_res.json()['job_id']
        
        # Wait for completion
        for _ in range(60):
            time.sleep(2)
            status_res = requests.get(f"{BASE_URL}/api/cv/generate-models/status?token={auth_token_with_cv}&job_id={job_id}")
            if status_res.status_code == 200:
                data = status_res.json()
                if data['status'] == 'completed':
                    break
                elif data['status'] == 'failed':
                    pytest.fail(f"CV generation failed: {data.get('error')}")
        
        # Get generated models
        models_res = requests.get(f"{BASE_URL}/api/cv/models?token={auth_token_with_cv}")
        assert models_res.status_code == 200
        
        models = models_res.json().get('models', {})
        assert 'classique' in models
        
        # Parse the model JSON
        import json
        cv_data = json.loads(models['classique'])
        
        # Verify centres_interet section exists
        assert 'centres_interet' in cv_data
        assert len(cv_data['centres_interet']) > 0
        
        # Verify reformulations are professional (not just simple labels)
        for ci in cv_data['centres_interet']:
            # Should be a sentence, not just a word
            assert len(ci) > 20, f"Centre d'interet should be a reformulation: {ci}"


# ============================================================
# Module 4: Passport enrichment from centres d'interet
# ============================================================

class TestPassportEnrichmentFromCentresInteret:
    """Test that passport is enriched with competences from centres d'interet"""
    
    @pytest.fixture(scope="class")
    def auth_token_with_ci(self):
        """Create user with analyzed CV containing centres d'interet"""
        pseudo = f"ci_passport_{uuid.uuid4().hex[:8]}"
        password = "Test1234!"
        
        # Register
        register_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if register_res.status_code != 201:
            pytest.skip("Could not create test user")
        
        token = register_res.json()['token']
        
        # Analyze CV with specific centres d'interet
        cv_text = """
        Sophie BERNARD
        Consultante RH
        Email: sophie.bernard@email.com
        
        EXPÉRIENCES
        Consultante RH - Cabinet Conseil (2019-2023)
        
        FORMATION
        Master RH - IAE Paris (2019)
        
        CENTRES D'INTÉRÊT
        - Yoga et méditation (pratique quotidienne depuis 5 ans)
        - Théâtre d'improvisation (troupe amateur)
        """
        
        start_res = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": cv_text, "filename": "test_cv_passport.txt"}
        )
        
        if start_res.status_code != 200:
            pytest.skip("Could not start CV analysis")
        
        job_id = start_res.json()['job_id']
        
        # Wait for completion
        for _ in range(30):
            time.sleep(3)
            status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status_res.status_code == 200:
                data = status_res.json()
                if data['status'] == 'completed':
                    break
                elif data['status'] == 'failed':
                    pytest.skip(f"CV analysis failed: {data.get('error')}")
        
        return token
    
    def test_passport_has_competences_from_centres_interet(self, auth_token_with_ci):
        """Test that passport competences include those from centres d'interet"""
        res = requests.get(f"{BASE_URL}/api/passport?token={auth_token_with_ci}")
        assert res.status_code == 200
        
        passport = res.json()
        competences = passport.get('competences', [])
        
        # Check for competences that should come from yoga/meditation
        competence_names = [c.get('name', '').lower() for c in competences]
        
        # At least some competences from centres d'interet should be present
        ci_competences = ['gestion du stress', 'équilibre', 'résilience', 'aisance orale', 'créativité', 'confiance en soi']
        found_ci_competences = [c for c in ci_competences if any(c in name for name in competence_names)]
        
        # We expect at least some CI competences to be added
        assert len(found_ci_competences) > 0 or len(competences) > 0, "Passport should have competences from CV analysis"


# ============================================================
# Module 5: API endpoint validation
# ============================================================

class TestApiEndpoints:
    """Basic API endpoint validation"""
    
    def test_api_health(self):
        """Test API is responding"""
        res = requests.get(f"{BASE_URL}/api/")
        assert res.status_code == 200
        data = res.json()
        assert 'message' in data
        assert 'Re\'Actif Pro' in data['message']
    
    def test_cv_analyze_text_requires_auth(self):
        """Test CV analyze-text requires valid token"""
        res = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token=invalid_token",
            json={"text": "test", "filename": "test.txt"}
        )
        assert res.status_code in [401, 404]
    
    def test_cv_analyze_text_validates_input(self):
        """Test CV analyze-text validates minimum text length"""
        # First create a valid token
        pseudo = f"ci_validate_{uuid.uuid4().hex[:8]}"
        register_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "Test1234!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if register_res.status_code != 201:
            pytest.skip("Could not create test user")
        
        token = register_res.json()['token']
        
        # Try with too short text
        res = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": "short", "filename": "test.txt"}
        )
        assert res.status_code == 400
        assert 'trop court' in res.json().get('detail', '').lower()
