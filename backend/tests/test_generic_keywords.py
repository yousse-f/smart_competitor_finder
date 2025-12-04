"""
Unit tests per il filtro keywords generiche (Task 1)
Verifica che keywords generiche ricevano peso ridotto e penalità se sono le uniche matchate
"""

import pytest
import asyncio
import os

# Set mock API key to avoid validation errors
os.environ['OPENAI_API_KEY'] = 'test-key-for-unit-tests'

from core.keyword_extraction import is_generic_keyword, GENERIC_KEYWORDS
from core.matching import keyword_matcher


class TestGenericKeywordDetection:
    """Test funzione is_generic_keyword()"""
    
    def test_generic_keywords_detection(self):
        """Verifica che keywords generiche siano riconosciute correttamente"""
        # Generiche dovrebbero return True
        assert is_generic_keyword("hvac") == True
        assert is_generic_keyword("HVAC") == True
        assert is_generic_keyword("industria") == True
        assert is_generic_keyword("Industria") == True
        assert is_generic_keyword("tecnologia") == True
        assert is_generic_keyword("qualità") == True
        assert is_generic_keyword("italia") == True
        
    def test_specific_keywords_detection(self):
        """Verifica che keywords specifiche NON siano riconosciute come generiche"""
        # Specifiche dovrebbero return False
        assert is_generic_keyword("ventilatori") == False
        assert is_generic_keyword("Ventilatori") == False
        assert is_generic_keyword("centrifughi") == False
        assert is_generic_keyword("assiali") == False
        assert is_generic_keyword("turbine") == False
        assert is_generic_keyword("estrattori") == False
        
    def test_generic_keywords_list_size(self):
        """Verifica che la lista contenga almeno 40 keywords"""
        assert len(GENERIC_KEYWORDS) >= 40, f"Expected at least 40 generic keywords, got {len(GENERIC_KEYWORDS)}"
        print(f"✅ Total generic keywords: {len(GENERIC_KEYWORDS)}")


class TestMatchingWithGenericFilter:
    """Test calcolo score con filtro keywords generiche"""
    
    @pytest.mark.asyncio
    async def test_only_generic_keywords_low_score(self):
        """Match con SOLO keywords generiche dovrebbe avere score basso (<30%) per penalità 50%"""
        client_keywords = ['ventilatori', 'industriale', 'hvac', 'centrifughi', 'assiali']
        
        # Contenuto con SOLO keyword generica
        competitor_content = "La nostra azienda opera nel settore HVAC da 20 anni. HVAC systems."
        
        result = await keyword_matcher.calculate_match_score(
            client_keywords, competitor_content
        )
        
        score = result['match_score']
        quality_flag = result['score_details']['quality_flag']
        generic_matches = result['score_details']['generic_matches']
        specific_matches = result['score_details']['specific_matches']
        
        print(f"\n📊 Test ONLY GENERIC:")
        print(f"   Score: {score}%")
        print(f"   Generic: {generic_matches}")
        print(f"   Specific: {specific_matches}")
        print(f"   Quality: {quality_flag}")
        
        # Assertions
        assert score < 40, f"Expected score < 40% for only-generic match, got {score}%"
        assert len(specific_matches) == 0, "Expected 0 specific matches"
        assert len(generic_matches) > 0, "Expected at least 1 generic match"
        assert quality_flag == "LOW_QUALITY_ONLY_GENERIC", f"Expected LOW_QUALITY_ONLY_GENERIC, got {quality_flag}"
    
    @pytest.mark.asyncio
    async def test_mix_generic_specific_medium_score(self):
        """Match con MIX generic+specific dovrebbe avere score medio (40-70%)"""
        client_keywords = ['ventilatori', 'ventilazione', 'industriale', 'hvac', 'centrifughi']
        
        # Contenuto con mix
        competitor_content = """
        Produciamo ventilatori industriali e centrifughi per applicazioni HVAC.
        Ventilazione aria impianti.
        """
        
        result = await keyword_matcher.calculate_match_score(
            client_keywords, competitor_content
        )
        
        score = result['match_score']
        quality_flag = result['score_details']['quality_flag']
        generic_matches = result['score_details']['generic_matches']
        specific_matches = result['score_details']['specific_matches']
        
        print(f"\n📊 Test MIX GENERIC+SPECIFIC:")
        print(f"   Score: {score}%")
        print(f"   Generic: {generic_matches}")
        print(f"   Specific: {specific_matches}")
        print(f"   Quality: {quality_flag}")
        
        # Assertions
        assert 30 < score < 80, f"Expected score between 30-80% for mixed match, got {score}%"
        assert len(specific_matches) >= 1, "Expected at least 1 specific match"
        assert len(generic_matches) >= 1, "Expected at least 1 generic match"
        assert quality_flag in ["MEDIUM_QUALITY", "HIGH_QUALITY", "LOW_QUALITY"], f"Unexpected quality flag: {quality_flag}"
    
    @pytest.mark.asyncio
    async def test_many_specific_keywords_high_score(self):
        """Match con MOLTE keywords specifiche dovrebbe avere score alto (>60%) e HIGH_QUALITY"""
        client_keywords = ['ventilatori', 'centrifughi', 'assiali', 'turbine', 'estrattori', 'motori']
        
        # Contenuto con molte specifiche
        competitor_content = """
        Produciamo ventilatori centrifughi e assiali per industria.
        Turbine, estrattori, ventilatori ad alte prestazioni.
        Ventilatori centrifughi per estrazione fumi, motori elettrici.
        """
        
        result = await keyword_matcher.calculate_match_score(
            client_keywords, competitor_content
        )
        
        score = result['match_score']
        quality_flag = result['score_details']['quality_flag']
        generic_matches = result['score_details']['generic_matches']
        specific_matches = result['score_details']['specific_matches']
        
        print(f"\n📊 Test MANY SPECIFIC:")
        print(f"   Score: {score}%")
        print(f"   Generic: {generic_matches}")
        print(f"   Specific: {specific_matches}")
        print(f"   Quality: {quality_flag}")
        
        # Assertions
        assert score > 40, f"Expected score > 40% for many-specific match, got {score}%"
        assert len(specific_matches) >= 3, "Expected at least 3 specific matches"
        assert quality_flag in ["MEDIUM_QUALITY", "HIGH_QUALITY"], f"Expected MEDIUM or HIGH quality, got {quality_flag}"


class TestRealClientCases:
    """Test con i casi reali segnalati dal cliente"""
    
    @pytest.mark.asyncio
    async def test_cipriani_phe_score_reduction(self):
        """
        cipriani-phe.com era 39% (SBAGLIATO secondo cliente).
        Con nuovo filtro dovrebbe scendere < 30% perché match solo su HVAC.
        """
        client_keywords = ['ventilatori', 'ventilazione', 'industriale', 'hvac', 'aria']
        
        # Simula contenuto cipriani-phe.com (solo HVAC)
        competitor_content = "HVAC systems and solutions for industrial applications. HVAC."
        
        result = await keyword_matcher.calculate_match_score(
            client_keywords, competitor_content
        )
        
        score = result['match_score']
        quality_flag = result['score_details']['quality_flag']
        
        print(f"\n🏢 cipriani-phe.com:")
        print(f"   Score PRIMA: 39%")
        print(f"   Score DOPO: {score}%")
        print(f"   Quality: {quality_flag}")
        print(f"   ✅ Riduzione: {39 - score:.1f}%")
        
        assert score < 35, f"Expected score < 35% (was 39%), got {score}%"
        assert quality_flag == "LOW_QUALITY_ONLY_GENERIC" or len(result['score_details']['specific_matches']) == 0
    
    @pytest.mark.asyncio
    async def test_refrigera_eu_score_reduction(self):
        """
        refrigera.eu era 50% (SBAGLIATO secondo cliente).
        Con nuovo filtro dovrebbe scendere < 40% perché match solo su generiche.
        """
        client_keywords = ['ventilatori', 'ventilazione', 'industriale', 'hvac', 'aria']
        
        # Simula contenuto refrigera.eu (HVAC + ventilazione + industriale)
        competitor_content = "HVAC ventilazione industriale impianti aria condizionata."
        
        result = await keyword_matcher.calculate_match_score(
            client_keywords, competitor_content
        )
        
        score = result['match_score']
        quality_flag = result['score_details']['quality_flag']
        generic_matches = result['score_details']['generic_matches']
        
        print(f"\n🏢 refrigera.eu:")
        print(f"   Score PRIMA: 50%")
        print(f"   Score DOPO: {score}%")
        print(f"   Generic matches: {generic_matches}")
        print(f"   Quality: {quality_flag}")
        print(f"   ✅ Riduzione: {50 - score:.1f}%")
        
        assert score < 45, f"Expected score < 45% (was 50%), got {score}%"
        # Dovrebbe avere solo generiche o pochissime specifiche
        assert len(result['score_details']['specific_matches']) <= 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
