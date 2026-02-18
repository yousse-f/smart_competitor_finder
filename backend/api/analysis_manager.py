"""
Analysis Manager - Gestisce la persistenza delle analisi su file JSON
Permette di salvare, aggiornare e recuperare analisi in corso o completate
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Percorsi delle directory
BASE_DIR = Path(__file__).parent.parent
REPORTS_DIR = BASE_DIR / "reports"
IN_PROGRESS_DIR = REPORTS_DIR / "in_progress"
COMPLETED_DIR = REPORTS_DIR / "completed"
METADATA_FILE = REPORTS_DIR / "metadata.json"

# Crea le directory se non esistono
IN_PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
COMPLETED_DIR.mkdir(parents=True, exist_ok=True)


def create_analysis_id() -> str:
    """Genera un ID univoco per l'analisi basato su timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_analysis_file(
    analysis_id: str,
    client_url: str,
    client_keywords: List[str],
    total_sites: int
) -> Dict[str, Any]:
    """
    Crea un nuovo file di analisi nella cartella in_progress
    
    Args:
        analysis_id: ID univoco dell'analisi
        client_url: URL del sito cliente
        client_keywords: Keywords estratte dal sito
        total_sites: Numero totale di competitor da analizzare
        
    Returns:
        Dict con metadata dell'analisi creata
    """
    try:
        file_path = IN_PROGRESS_DIR / f"{analysis_id}.json"
        
        analysis_data = {
            "metadata": {
                "id": analysis_id,
                "status": "in_progress",
                "client_url": client_url,
                "client_name": f"Analisi {client_url} - {datetime.now().strftime('%d/%m/%Y')}",
                "client_keywords": client_keywords,
                "total_sites": total_sites,
                "processed_sites": 0,
                "progress": 0,
                "started_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "completed_at": None
            },
            "results": [],
            "failed_sites": []  # 🆕 Track failed URLs with errors
        }
        
        # Salva il file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        # Aggiorna metadata index
        _update_metadata_index(analysis_data["metadata"])
        
        logger.info(f"✅ Analisi creata: {analysis_id}")
        return analysis_data["metadata"]
        
    except Exception as e:
        logger.error(f"❌ Errore creazione analisi {analysis_id}: {e}")
        raise


def update_analysis_progress(
    analysis_id: str,
    processed_sites: int,
    new_result: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Aggiorna il progresso di un'analisi e aggiunge un nuovo risultato
    
    Args:
        analysis_id: ID dell'analisi
        processed_sites: Numero di siti processati finora
        new_result: Nuovo risultato da aggiungere (opzionale)
        
    Returns:
        True se aggiornamento riuscito
    """
    try:
        file_path = IN_PROGRESS_DIR / f"{analysis_id}.json"
        
        if not file_path.exists():
            logger.warning(f"⚠️ File analisi non trovato: {analysis_id}")
            return False
        
        # Leggi file esistente
        with open(file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Aggiorna metadata
        total_sites = analysis_data["metadata"]["total_sites"]
        progress = int((processed_sites / total_sites) * 100) if total_sites > 0 else 0
        
        analysis_data["metadata"]["processed_sites"] = processed_sites
        analysis_data["metadata"]["progress"] = progress
        analysis_data["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Aggiungi nuovo risultato
        if new_result:
            analysis_data["results"].append(new_result)
        
        # Salva file aggiornato
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        # Aggiorna metadata index
        _update_metadata_index(analysis_data["metadata"])
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore aggiornamento analisi {analysis_id}: {e}")
        return False


def add_failed_site(
    analysis_id: str,
    failed_site_data: Dict[str, Any]
) -> bool:
    """
    Aggiunge un sito fallito alla lista failed_sites dell'analisi
    
    Args:
        analysis_id: ID dell'analisi
        failed_site_data: Dict con url, error, suggestion, timestamp
        
    Returns:
        True se aggiornamento riuscito
    """
    try:
        file_path = IN_PROGRESS_DIR / f"{analysis_id}.json"
        
        if not file_path.exists():
            logger.warning(f"⚠️ File analisi non trovato: {analysis_id}")
            return False
        
        # Leggi file esistente
        with open(file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Assicurati che failed_sites esista
        if "failed_sites" not in analysis_data:
            analysis_data["failed_sites"] = []
        
        # Aggiungi failed site
        analysis_data["failed_sites"].append(failed_site_data)
        analysis_data["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Salva file aggiornato
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore aggiunta sito fallito {analysis_id}: {e}")
        return False


def complete_analysis(analysis_id: str) -> bool:
    """
    Sposta un'analisi da in_progress a completed
    
    Args:
        analysis_id: ID dell'analisi
        
    Returns:
        True se completamento riuscito
    """
    try:
        source_path = IN_PROGRESS_DIR / f"{analysis_id}.json"
        dest_path = COMPLETED_DIR / f"{analysis_id}.json"
        
        if not source_path.exists():
            logger.warning(f"⚠️ File analisi non trovato: {analysis_id}")
            return False
        
        # Leggi e aggiorna status
        with open(source_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        analysis_data["metadata"]["status"] = "completed"
        analysis_data["metadata"]["completed_at"] = datetime.now().isoformat()
        analysis_data["metadata"]["updated_at"] = datetime.now().isoformat()
        analysis_data["metadata"]["progress"] = 100
        
        # Salva nella cartella completed
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        # Rimuovi dalla cartella in_progress
        source_path.unlink()
        
        # Aggiorna metadata index
        _update_metadata_index(analysis_data["metadata"])
        
        logger.info(f"✅ Analisi completata: {analysis_id}")
        logger.info(f"✅ File generato: {dest_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore completamento analisi {analysis_id}: {e}")
        return False


def fail_analysis(analysis_id: str, error_message: str) -> bool:
    """
    Segna un'analisi come fallita
    
    Args:
        analysis_id: ID dell'analisi
        error_message: Messaggio di errore
        
    Returns:
        True se aggiornamento riuscito
    """
    try:
        file_path = IN_PROGRESS_DIR / f"{analysis_id}.json"
        
        if not file_path.exists():
            logger.warning(f"⚠️ File analisi non trovato: {analysis_id}")
            return False
        
        # Leggi e aggiorna status
        with open(file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        analysis_data["metadata"]["status"] = "failed"
        analysis_data["metadata"]["error"] = error_message
        analysis_data["metadata"]["completed_at"] = datetime.now().isoformat()
        analysis_data["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Salva file aggiornato
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        # Aggiorna metadata index
        _update_metadata_index(analysis_data["metadata"])
        
        logger.info(f"⚠️ Analisi fallita: {analysis_id} - {error_message}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore segnalazione fallimento {analysis_id}: {e}")
        return False


def get_analysis_status(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Recupera lo stato attuale di un'analisi
    
    Args:
        analysis_id: ID dell'analisi
        
    Returns:
        Dict con dati completi dell'analisi o None se non trovata
    """
    try:
        # Cerca in in_progress
        file_path = IN_PROGRESS_DIR / f"{analysis_id}.json"
        
        # Se non trovato, cerca in completed
        if not file_path.exists():
            file_path = COMPLETED_DIR / f"{analysis_id}.json"
        
        # Se ancora non trovato, return None
        if not file_path.exists():
            logger.warning(f"⚠️ Analisi non trovata: {analysis_id}")
            return None
        
        # Leggi e restituisci
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    except Exception as e:
        logger.error(f"❌ Errore lettura analisi {analysis_id}: {e}")
        return None


def list_all_analyses(status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """
    Lista tutte le analisi con filtri opzionali
    
    Args:
        status: Filtra per status (in_progress, completed, failed)
        limit: Numero massimo di risultati
        
    Returns:
        Dict con lista analisi e statistiche
    """
    try:
        # Carica metadata index
        metadata = _load_metadata_index()
        analyses = metadata.get("analyses", [])
        
        # Filtra per status se specificato
        if status:
            analyses = [a for a in analyses if a.get("status") == status]
        
        # Ordina per data (più recenti prima)
        analyses.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        
        # Limita risultati
        analyses = analyses[:limit]
        
        # Calcola statistiche
        all_analyses = metadata.get("analyses", [])
        stats = {
            "total": len(all_analyses),
            "in_progress": len([a for a in all_analyses if a.get("status") == "in_progress"]),
            "completed": len([a for a in all_analyses if a.get("status") == "completed"]),
            "failed": len([a for a in all_analyses if a.get("status") == "failed"])
        }
        
        return {
            "analyses": analyses,
            **stats
        }
        
    except Exception as e:
        logger.error(f"❌ Errore lista analisi: {e}")
        return {
            "analyses": [],
            "total": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }


def _update_metadata_index(analysis_metadata: Dict[str, Any]) -> bool:
    """
    Aggiorna il file metadata.json con le info di un'analisi
    
    Args:
        analysis_metadata: Metadata dell'analisi da aggiornare
        
    Returns:
        True se aggiornamento riuscito
    """
    try:
        metadata = _load_metadata_index()
        analyses = metadata.get("analyses", [])
        
        # Rimuovi entry esistente (se presente)
        analyses = [a for a in analyses if a.get("id") != analysis_metadata["id"]]
        
        # Aggiungi entry aggiornata
        # Crea versione ridotta per metadata (solo campi essenziali)
        metadata_entry = {
            "id": analysis_metadata["id"],
            "status": analysis_metadata["status"],
            "client_url": analysis_metadata["client_url"],
            "client_name": analysis_metadata["client_name"],
            "total_sites": analysis_metadata["total_sites"],
            "processed_sites": analysis_metadata.get("processed_sites", 0),
            "progress": analysis_metadata.get("progress", 0),
            "started_at": analysis_metadata["started_at"],
            "completed_at": analysis_metadata.get("completed_at"),
            "file_path": f"{analysis_metadata['status'].replace('_', '-')}/{analysis_metadata['id']}.json"
        }
        
        analyses.append(metadata_entry)
        
        # Salva metadata aggiornato
        metadata["analyses"] = analyses
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore aggiornamento metadata: {e}")
        return False


def _load_metadata_index() -> Dict[str, Any]:
    """
    Carica il file metadata.json
    
    Returns:
        Dict con metadata o dict vuoto se file non esiste
    """
    try:
        if METADATA_FILE.exists():
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Crea metadata vuoto
            metadata = {
                "analyses": [],
                "last_updated": datetime.now().isoformat()
            }
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            return metadata
            
    except Exception as e:
        logger.error(f"❌ Errore caricamento metadata: {e}")
        return {"analyses": [], "last_updated": datetime.now().isoformat()}


def cleanup_old_analyses(days: int = 30) -> int:
    """
    Elimina analisi completate più vecchie di X giorni
    
    Args:
        days: Numero di giorni di retention
        
    Returns:
        Numero di analisi eliminate
    """
    try:
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        # Scansiona cartella completed
        for file_path in COMPLETED_DIR.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                completed_at = data["metadata"].get("completed_at")
                if completed_at:
                    completed_date = datetime.fromisoformat(completed_at)
                    if completed_date < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"🗑️ Eliminata analisi vecchia: {file_path.stem}")
                        
            except Exception as e:
                logger.error(f"❌ Errore eliminazione {file_path}: {e}")
        
        # Aggiorna metadata rimuovendo entry eliminate
        metadata = _load_metadata_index()
        analyses = metadata.get("analyses", [])
        original_count = len(analyses)
        
        analyses = [
            a for a in analyses
            if not (a.get("status") == "completed" and 
                   a.get("completed_at") and 
                   datetime.fromisoformat(a["completed_at"]) >= cutoff_date)
        ]
        
        metadata["analyses"] = analyses
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"🧹 Cleanup completato: {deleted_count} file eliminati, {original_count - len(analyses)} entries rimosse da metadata")
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Errore cleanup: {e}")
        return 0
