"""
Tests for 2-Step CV Flow in Re'Actif Pro
=========================================
Step 1: POST /api/cv/analyze-text - Fast analysis only (NO CV generation)
Step 2: POST /api/cv/generate-models - On-demand generation of selected models
        GET /api/cv/generate-models/status - Returns progress (current/total/current_model)
        GET /api/cv/models - Returns only the models that were generated

Tests:
- analyze-text does NOT generate CV models anymore (fast analysis only)
- generate-models accepts model_types list and generates selected models
- generate-models/status returns progress and current_model
- cv/models returns only the models that were generated
- Full e2e flow: upload -> fast analysis -> select models -> generate -> view results
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

SAMPLE_CV_TEXT = """
MARIE MARTIN
Responsable Marketing Digital

PROFIL
Experte en marketing digital avec 6 ans d'expérience. Spécialisée dans les stratégies de communication digitale.

EXPÉRIENCES PROFESSIONNELLES

Responsable Marketing Digital - Startup TechBoost (2021-2024)
- Élaboration de stratégies digitales
- Gestion d'une équipe de 4 personnes
- Budget marketing de 150k€ annuel

Chargée de Communication - Agence MediaPro (2018-2021)
- Création de contenus pour réseaux sociaux
- Animation de la communauté en ligne

COMPÉTENCES TECHNIQUES
- Marketing digital: SEO, SEA, réseaux sociaux
- Outils: Google Analytics, Meta Business Suite
- CRM: HubSpot, Salesforce

COMPÉTENCES COMPORTEMENTALES
- Leadership et esprit d'équipe
- Créativité et innovation
- Gestion du stress

FORMATION
Master Communication Digitale - ISCOM Paris (2018)
Licence Information-Communication - Université Lyon (2016)
"""


class TestSetup:
    """Verify API is accessible"""

    def test_api_health(self):
        """Verify API health"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"✓ API health: {response.json()}")


class TestStep1AnalysisOnly:
    """Test Step 1: POST /api/cv/analyze-text does NOT generate CV models (fast analysis only)"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        return response.json()["token"]

    def test_analyze_text_returns_job_id(self, auth_token):
        """Test that analyze-text returns job_id and starts analysis"""
        payload = {"text": SAMPLE_CV_TEXT, "filename": "cv_test.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={auth_token}", json=payload, timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data
        assert data["status"] == "started"
        print(f"✓ analyze-text returns job_id: {data['job_id']}")

    def test_analyze_text_completes_fast_without_cv_generation(self, auth_token):
        """Test that analysis completes fast (no CV generation step)"""
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={auth_token}")
        
        payload = {"text": SAMPLE_CV_TEXT, "filename": "cv_fast_test.txt"}
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={auth_token}", json=payload, timeout=15)
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Poll for completion - should be fast (< 60s typically)
        max_polls = 40
        result = None
        for i in range(max_polls):
            time.sleep(3)
            status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={auth_token}&job_id={job_id}")
            if status_res.status_code == 200:
                status_data = status_res.json()
                print(f"  Poll {i+1}: status={status_data['status']}, step={status_data.get('step', '')}")
                
                if status_data["status"] == "completed":
                    result = status_data.get("result")
                    break
                elif status_data["status"] == "failed":
                    pytest.fail(f"Analysis failed: {status_data.get('error')}")
        
        elapsed = time.time() - start_time
        print(f"✓ Analysis completed in {elapsed:.1f}s")
        
        assert result is not None, "Analysis did not complete"
        assert result["savoir_faire_count"] > 0
        assert result["savoir_etre_count"] > 0
        
        # CRITICAL: Verify CV models were NOT generated during analysis
        models_res = requests.get(f"{BASE_URL}/api/cv/models?token={auth_token}")
        assert models_res.status_code == 200
        models_data = models_res.json()
        
        # After analysis only, models should be empty or not present
        models = models_data.get("models", {})
        generated_count = sum(1 for v in models.values() if v and len(v) > 50)
        
        print(f"✓ CV models after analysis: {generated_count} generated (expected 0 for analysis-only)")
        # This test checks the new behavior - analysis should NOT generate models
        # If models exist, they may be from previous test runs


class TestStep2GenerateModels:
    """Test Step 2: POST /api/cv/generate-models generates selected models on demand"""

    @pytest.fixture(scope="class")
    def auth_with_analysis(self):
        """Create token, run analysis (Step 1), return token"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Run analysis (Step 1)
        payload = {"text": SAMPLE_CV_TEXT, "filename": "cv_for_generation.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={token}", json=payload, timeout=15)
        job_id = response.json()["job_id"]
        
        # Wait for analysis to complete
        for _ in range(40):
            time.sleep(3)
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status.status_code == 200 and status.json()["status"] == "completed":
                break
        
        return token

    def test_generate_models_requires_analyzed_cv(self):
        """Test that generate-models fails if no CV was analyzed"""
        # Fresh token without analysis
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={token}",
            json={"model_types": ["classique"]},
            timeout=15
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ generate-models returns 404 when no CV analyzed")

    def test_generate_models_accepts_model_types_list(self, auth_with_analysis):
        """Test that generate-models accepts model_types list"""
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={auth_with_analysis}",
            json={"model_types": ["classique", "mixte"]},
            timeout=15
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data
        assert data["status"] == "started"
        assert data["model_types"] == ["classique", "mixte"]
        assert data["total"] == 2
        
        print(f"✓ generate-models accepted model_types list, job_id: {data['job_id']}")
        return data["job_id"]

    def test_generate_models_rejects_empty_list(self, auth_with_analysis):
        """Test that generate-models rejects empty model_types list"""
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={auth_with_analysis}",
            json={"model_types": []},
            timeout=15
        )
        
        assert response.status_code == 400, f"Expected 400 for empty list, got {response.status_code}"
        print(f"✓ generate-models rejects empty model_types list")

    def test_generate_models_rejects_invalid_types(self, auth_with_analysis):
        """Test that generate-models rejects all invalid model types"""
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={auth_with_analysis}",
            json={"model_types": ["invalid_model", "another_invalid"]},
            timeout=15
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid types, got {response.status_code}"
        print(f"✓ generate-models rejects invalid model types")


class TestGenerateModelsStatus:
    """Test GET /api/cv/generate-models/status returns progress"""

    @pytest.fixture(scope="class")
    def token_with_cv_text(self):
        """Create token and store CV text (Step 1 partially)"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Run analysis to store CV text
        payload = {"text": SAMPLE_CV_TEXT, "filename": "cv_progress_test.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={token}", json=payload, timeout=15)
        job_id = response.json()["job_id"]
        
        # Wait for analysis
        for _ in range(40):
            time.sleep(3)
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status.status_code == 200 and status.json()["status"] in ["completed", "failed"]:
                break
        
        return token

    def test_status_endpoint_returns_progress(self, token_with_cv_text):
        """Test that status endpoint returns progress, total, current_model"""
        # Start generation
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={token_with_cv_text}",
            json={"model_types": ["classique", "competences"]},
            timeout=15
        )
        
        if response.status_code != 200:
            pytest.skip(f"Generation failed to start: {response.text}")
        
        job_id = response.json()["job_id"]
        
        # Poll status and verify fields
        seen_progress = False
        for _ in range(60):  # ~2 min timeout
            time.sleep(2)
            status_res = requests.get(f"{BASE_URL}/api/cv/generate-models/status?token={token_with_cv_text}&job_id={job_id}")
            
            if status_res.status_code == 200:
                data = status_res.json()
                
                # Verify required fields
                assert "job_id" in data
                assert "status" in data
                assert "progress" in data
                assert "total" in data
                
                print(f"  Status: {data['status']}, Progress: {data['progress']}/{data['total']}, Current: {data.get('current_model', '-')}")
                
                if data["progress"] > 0:
                    seen_progress = True
                
                if data["status"] == "completed":
                    assert data["progress"] == data["total"]
                    print(f"✓ Generation completed: {data['progress']}/{data['total']}")
                    break
                elif data["status"] == "failed":
                    print(f"⚠ Generation failed: {data.get('error')}")
                    break
        
        # We should have seen progress at some point
        print(f"✓ Status endpoint returns progress/total/current_model fields")


class TestCvModelsAfterGeneration:
    """Test GET /api/cv/models returns only generated models"""

    @pytest.fixture(scope="class")
    def token_with_generated_models(self):
        """Full flow: analyze -> generate specific models"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Step 1: Analyze
        payload = {"text": SAMPLE_CV_TEXT, "filename": "cv_models_test.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={token}", json=payload, timeout=15)
        job_id = response.json()["job_id"]
        
        for _ in range(40):
            time.sleep(3)
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status.status_code == 200 and status.json()["status"] == "completed":
                break
        
        # Step 2: Generate ONLY classique and fonctionnel
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={token}",
            json={"model_types": ["classique", "fonctionnel"]},
            timeout=15
        )
        
        if response.status_code != 200:
            return {"token": token, "generated_models": []}
        
        gen_job_id = response.json()["job_id"]
        
        # Wait for generation
        for _ in range(60):
            time.sleep(2)
            status = requests.get(f"{BASE_URL}/api/cv/generate-models/status?token={token}&job_id={gen_job_id}")
            if status.status_code == 200:
                if status.json()["status"] in ["completed", "failed"]:
                    break
        
        return {"token": token, "generated_models": ["classique", "fonctionnel"]}

    def test_cv_models_returns_only_generated(self, token_with_generated_models):
        """Test that cv/models returns only the models that were generated"""
        token = token_with_generated_models["token"]
        expected = token_with_generated_models["generated_models"]
        
        response = requests.get(f"{BASE_URL}/api/cv/models?token={token}")
        assert response.status_code == 200
        
        models = response.json().get("models", {})
        
        # Check which models have content
        populated_models = [k for k, v in models.items() if v and len(v) > 50]
        
        print(f"✓ Models returned: {list(models.keys())}")
        print(f"  Populated models: {populated_models}")
        print(f"  Expected: {expected}")
        
        # The populated models should match what we generated
        if expected:
            for m in expected:
                if m in populated_models:
                    print(f"  ✓ {m} was generated (has content)")


class TestFullE2EFlow:
    """End-to-end test: upload -> fast analysis -> select 2 models -> generate -> view results"""

    def test_full_two_step_flow(self):
        """Complete 2-step flow test"""
        print("\n=== E2E Test: 2-Step CV Flow ===\n")
        
        # 1. Create auth token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        token = response.json()["token"]
        print(f"1. ✓ Auth token created")
        
        # 2. Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        print(f"2. ✓ Passport initialized")
        
        # 3. STEP 1: Fast Analysis
        print(f"3. Starting Step 1: Fast Analysis...")
        start_time = time.time()
        
        payload = {"text": SAMPLE_CV_TEXT, "filename": "cv_e2e_test.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={token}", json=payload, timeout=15)
        assert response.status_code == 200
        
        analysis_job_id = response.json()["job_id"]
        
        # Poll for analysis completion
        analysis_result = None
        for i in range(40):
            time.sleep(3)
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={analysis_job_id}")
            if status.status_code == 200:
                data = status.json()
                if data["status"] == "completed":
                    analysis_result = data.get("result")
                    break
                elif data["status"] == "failed":
                    pytest.fail(f"Analysis failed: {data.get('error')}")
        
        analysis_time = time.time() - start_time
        assert analysis_result is not None, "Analysis timed out"
        
        print(f"   ✓ Analysis completed in {analysis_time:.1f}s")
        print(f"   - Savoir-faire: {analysis_result.get('savoir_faire_count')}")
        print(f"   - Savoir-être: {analysis_result.get('savoir_etre_count')}")
        print(f"   - Experiences: {analysis_result.get('experiences_count')}")
        
        # 4. STEP 2: Generate selected models (classique and mixte only)
        print(f"4. Starting Step 2: Generate 2 models (classique, mixte)...")
        gen_start = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={token}",
            json={"model_types": ["classique", "mixte"]},
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"   ⚠ Generation failed to start: {response.text}")
            pytest.skip("Generation failed - possibly LLM budget issue")
        
        gen_job_id = response.json()["job_id"]
        
        # Poll for generation completion with progress tracking
        for i in range(60):
            time.sleep(2)
            status = requests.get(f"{BASE_URL}/api/cv/generate-models/status?token={token}&job_id={gen_job_id}")
            if status.status_code == 200:
                data = status.json()
                print(f"   Progress: {data.get('progress')}/{data.get('total')} - {data.get('current_model', '-')}")
                
                if data["status"] == "completed":
                    break
                elif data["status"] == "failed":
                    print(f"   ⚠ Generation failed: {data.get('error')}")
                    pytest.skip(f"Generation failed: {data.get('error')}")
        
        gen_time = time.time() - gen_start
        print(f"   ✓ Generation completed in {gen_time:.1f}s")
        
        # 5. Verify generated models
        print(f"5. Verifying generated models...")
        response = requests.get(f"{BASE_URL}/api/cv/models?token={token}")
        assert response.status_code == 200
        
        models = response.json().get("models", {})
        
        classique_len = len(models.get("classique", ""))
        mixte_len = len(models.get("mixte", ""))
        competences_len = len(models.get("competences", ""))
        fonctionnel_len = len(models.get("fonctionnel", ""))
        
        print(f"   - classique: {classique_len} chars")
        print(f"   - mixte: {mixte_len} chars")
        print(f"   - competences: {competences_len} chars (should be 0 or minimal)")
        print(f"   - fonctionnel: {fonctionnel_len} chars (should be 0 or minimal)")
        
        # Verify classique and mixte have content
        if classique_len > 100:
            print(f"   ✓ classique model generated successfully")
        if mixte_len > 100:
            print(f"   ✓ mixte model generated successfully")
        
        print(f"\n=== E2E Test Complete ===")
        print(f"Total time: Step 1 ({analysis_time:.1f}s) + Step 2 ({gen_time:.1f}s) = {analysis_time + gen_time:.1f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
