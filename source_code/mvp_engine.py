# import pandas as pd
# import json

# class HealthcareEngine:

#     def __init__(self):
#         # -----------------------------
#         # Load datasets
#         # -----------------------------
#         self.symptom_data = pd.read_csv("data/clean_training.csv")

#         # MasterData-style files
#         self.desc = pd.read_csv("data/symptom_description.csv")
#         self.prec = pd.read_csv("data/symptom_precaution.csv")
#         self.severity = pd.read_csv("data/symptom_severity.csv")

#         # synonyms
#         with open("data/synonyms.json") as f:
#             self.synonyms = json.load(f)

#         # Convert to usable dicts
#         self.desc_dict = dict(zip(self.desc["symptom"], self.desc["description"]))
#         self.prec_dict = {
#             row["symptom"]: [row["p1"], row["p2"], row["p3"], row["p4"]]
#             for _, row in self.prec.iterrows()
#         }
#         self.severity_dict = dict(zip(self.severity["symptom"], self.severity["severity"]))


#     # -----------------------------
#     # INTERNAL UTILS
#     # -----------------------------

#     def normalize(self, symptom_text):
#         """
#         Convert raw input text → normalized symptom list.
#         Handles synonyms + lowercase transformation.
#         """
#         raw = [s.strip().lower() for s in symptom_text.split(",") if s.strip()]

#         final_symptoms = []
#         for s in raw:
#             mapped = None

#             # Match synonyms
#             for key, group in self.synonyms.items():
#                 if s in group:
#                     mapped = key
#                     break

#             final_symptoms.append(mapped if mapped else s)

#         return final_symptoms


#     def match_symptoms(self, input_list, disease_symptoms):
#         """
#         Returns:
#             matched symptoms,
#             missing symptoms
#         """
#         matched = [s for s in input_list if s in disease_symptoms]
#         missing = [s for s in disease_symptoms if s not in input_list]
#         return matched, missing


#     # -----------------------------
#     # MAIN PREDICTION FUNCTION
#     # -----------------------------

#     def predict(self, user_symptom_text):
#         """
#         Main public method.
#         Input  → raw symptom text
#         Output → structured dict:
#             {
#               disease,
#               confidence,
#               matched,
#               missing,
#               description,
#               precautions
#             }
#         """
#         # Normalize input
#         user_symptoms = self.normalize(user_symptom_text)

#         best_disease = None
#         best_score = 0
#         best_matched = []
#         best_missing = []

#         # Iterate through dataset (each row = one disease)
#         for _, row in self.symptom_data.iterrows():

#             disease = row["prognosis"]

#             # Symptoms listed across multiple columns
#             disease_symptoms = [
#                 col for col in self.symptom_data.columns
#                 if row[col] == 1 and col != "prognosis"
#             ]

#             matched, missing = self.match_symptoms(user_symptoms, disease_symptoms)

#             if len(disease_symptoms) == 0:
#                 continue

#             score = len(matched) / len(disease_symptoms)

#             if score > best_score:
#                 best_score = score
#                 best_disease = disease
#                 best_matched = matched
#                 best_missing = missing

#         # If no match at all
#         if best_disease is None or best_score == 0:
#             return {
#                 "disease": "Unknown condition",
#                 "confidence": 0,
#                 "matched": [],
#                 "missing": [],
#                 "description": "Your symptoms do not match our database. Please consult a doctor.",
#                 "precautions": [],
#             }

#         # Precautions fallback
#         precautions = self.prec_dict.get(best_disease, ["Stay hydrated", "Rest well", "Monitor symptoms", "Consult a doctor"])

#         # Description fallback
#         description = self.desc_dict.get(best_disease, "No description available")

#         return {
#             "disease": best_disease,
#             "confidence": round(best_score, 2),
#             "matched": best_matched,
#             "missing": best_missing,
#             "description": description,
#             "precautions": precautions
#         }



import pandas as pd
import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthcareEngine:
    """
    Healthcare diagnostic engine that matches user symptoms to potential conditions.
    
    This engine uses symptom matching algorithms with confidence scoring to provide
    preliminary health assessments. NOT for medical diagnosis.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the healthcare engine with medical datasets.
        
        Args:
            data_dir: Directory containing the medical data files
            
        Raises:
            FileNotFoundError: If required data files are missing
            Exception: If data loading fails
        """
        self.data_dir = Path(data_dir)
        
        # Initialize data containers
        self.symptom_data: Optional[pd.DataFrame] = None
        self.desc_dict: Dict[str, str] = {}
        self.prec_dict: Dict[str, List[str]] = {}
        self.severity_dict: Dict[str, int] = {}
        self.synonyms: Dict[str, List[str]] = {}
        
        # Load all data
        self._load_data()
        
        # Cache for performance
        self._disease_cache: Dict[str, List[str]] = {}
        self._build_disease_cache()
        
        logger.info("HealthcareEngine initialized successfully")
    
    
    # -----------------------------
    # DATA LOADING
    # -----------------------------
    
    def _load_data(self):
        """Load all required datasets with error handling"""
        try:
            # Load main symptom training data
            symptom_file = self.data_dir / "clean_training.csv"
            if not symptom_file.exists():
                raise FileNotFoundError(f"Training data not found: {symptom_file}")
            self.symptom_data = pd.read_csv(symptom_file)
            logger.info(f"Loaded {len(self.symptom_data)} disease records")
            
            # Load descriptions
            self._load_descriptions()
            
            # Load precautions
            self._load_precautions()
            
            # Load severity data
            self._load_severity()
            
            # Load synonyms
            self._load_synonyms()
            
        except FileNotFoundError as e:
            logger.error(f"Data file missing: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    
    def _load_descriptions(self):
        """Load symptom descriptions with fallback"""
        try:
            desc_file = self.data_dir / "symptom_description.csv"
            if desc_file.exists():
                desc_df = pd.read_csv(desc_file)
                # Handle potential column name variations
                desc_cols = desc_df.columns.tolist()
                symptom_col = next((col for col in desc_cols if 'symptom' in col.lower()), desc_cols[0])
                desc_col = next((col for col in desc_cols if 'description' in col.lower()), desc_cols[1])
                
                self.desc_dict = dict(zip(desc_df[symptom_col], desc_df[desc_col]))
                logger.info(f"Loaded {len(self.desc_dict)} disease descriptions")
            else:
                logger.warning("Description file not found, using fallback")
        except Exception as e:
            logger.warning(f"Error loading descriptions: {e}")
    
    
    def _load_precautions(self):
        """Load precautions with robust handling of missing data"""
        try:
            prec_file = self.data_dir / "symptom_precaution.csv"
            if prec_file.exists():
                prec_df = pd.read_csv(prec_file)
                
                for _, row in prec_df.iterrows():
                    symptom_key = row.get("symptom", row.iloc[0])
                    
                    # Collect all precaution columns (p1, p2, p3, p4, etc.)
                    precautions = []
                    for col in row.index:
                        if col.startswith('p') and col[1:].isdigit():
                            val = row[col]
                            if pd.notna(val) and str(val).strip():
                                precautions.append(str(val).strip())
                    
                    if precautions:
                        self.prec_dict[symptom_key] = precautions
                
                logger.info(f"Loaded precautions for {len(self.prec_dict)} conditions")
            else:
                logger.warning("Precautions file not found, using fallback")
        except Exception as e:
            logger.warning(f"Error loading precautions: {e}")
    
    
    def _load_severity(self):
        """Load symptom severity ratings"""
        try:
            severity_file = self.data_dir / "symptom_severity.csv"
            if severity_file.exists():
                severity_df = pd.read_csv(severity_file)
                severity_cols = severity_df.columns.tolist()
                symptom_col = next((col for col in severity_cols if 'symptom' in col.lower()), severity_cols[0])
                severity_col = next((col for col in severity_cols if 'severity' in col.lower()), severity_cols[1])
                
                self.severity_dict = dict(zip(severity_df[symptom_col], severity_df[severity_col]))
                logger.info(f"Loaded severity data for {len(self.severity_dict)} symptoms")
            else:
                logger.warning("Severity file not found")
        except Exception as e:
            logger.warning(f"Error loading severity: {e}")
    
    
    def _load_synonyms(self):
        """Load symptom synonyms mapping"""
        try:
            synonyms_file = self.data_dir / "synonyms.json"
            if synonyms_file.exists():
                with open(synonyms_file, 'r', encoding='utf-8') as f:
                    self.synonyms = json.load(f)
                
                # Validate structure
                if not isinstance(self.synonyms, dict):
                    raise ValueError("Synonyms file must contain a JSON object")
                
                total_synonyms = sum(len(v) if isinstance(v, list) else 0 for v in self.synonyms.values())
                logger.info(f"Loaded {len(self.synonyms)} symptom groups with {total_synonyms} total synonyms")
            else:
                logger.warning("Synonyms file not found, using exact matching only")
                self.synonyms = {}
        except Exception as e:
            logger.warning(f"Error loading synonyms: {e}")
            self.synonyms = {}
    
    
    def _build_disease_cache(self):
        """Build a cache of disease->symptoms mapping for faster lookup"""
        if self.symptom_data is None:
            return
        
        for _, row in self.symptom_data.iterrows():
            disease = row["prognosis"]
            symptoms = [
                col for col in self.symptom_data.columns
                if col != "prognosis" and row[col] == 1
            ]
            self._disease_cache[disease] = symptoms
        
        logger.info(f"Built cache for {len(self._disease_cache)} diseases")
    
    
    # -----------------------------
    # SYMPTOM NORMALIZATION
    # -----------------------------
    
    def normalize(self, symptom_text: str) -> List[str]:
        """
        Convert raw input text to normalized symptom list.
        
        Handles:
        - Lowercasing
        - Whitespace normalization
        - Synonym mapping
        - Special character removal
        
        Args:
            symptom_text: Raw comma-separated symptom string
            
        Returns:
            List of normalized symptom strings
        """
        if not symptom_text or not symptom_text.strip():
            return []
        
        # Split by comma and clean
        raw_symptoms = [s.strip().lower() for s in symptom_text.split(",") if s.strip()]
        
        normalized = []
        for symptom in raw_symptoms:
            # Remove extra punctuation but keep hyphens and underscores
            cleaned = re.sub(r'[^\w\s-]', '', symptom)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            if not cleaned:
                continue
            
            # Check for synonym mapping
            mapped = self._map_synonym(cleaned)
            normalized.append(mapped)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_normalized = []
        for s in normalized:
            if s not in seen:
                seen.add(s)
                unique_normalized.append(s)
        
        return unique_normalized
    
    
    def _map_synonym(self, symptom: str) -> str:
        """
        Map a symptom to its canonical form using synonym dictionary.
        
        Args:
            symptom: Lowercase symptom string
            
        Returns:
            Canonical symptom name or original if no mapping found
        """
        # Direct check in synonym lists
        for canonical, synonyms in self.synonyms.items():
            if isinstance(synonyms, list) and symptom in synonyms:
                return canonical
            elif symptom == canonical:
                return canonical
        
        # Fuzzy matching for common variations
        symptom_normalized = symptom.replace('_', ' ').replace('-', ' ')
        
        for canonical, synonyms in self.synonyms.items():
            canonical_normalized = canonical.replace('_', ' ').replace('-', ' ')
            
            if symptom_normalized == canonical_normalized:
                return canonical
            
            if isinstance(synonyms, list):
                for syn in synonyms:
                    syn_normalized = syn.replace('_', ' ').replace('-', ' ')
                    if symptom_normalized == syn_normalized:
                        return canonical
        
        return symptom
    
    
    # -----------------------------
    # SYMPTOM MATCHING
    # -----------------------------
    
    def match_symptoms(self, input_list: List[str], disease_symptoms: List[str]) -> Tuple[List[str], List[str]]:
        """
        Match user symptoms against disease symptom profile.
        
        Args:
            input_list: User's normalized symptoms
            disease_symptoms: Known symptoms for a disease
            
        Returns:
            Tuple of (matched_symptoms, missing_symptoms)
        """
        # Case-insensitive matching with normalization
        input_normalized = {s.lower().replace('_', ' '): s for s in input_list}
        disease_normalized = {s.lower().replace('_', ' '): s for s in disease_symptoms}
        
        matched = []
        for norm_input, original_input in input_normalized.items():
            if norm_input in disease_normalized:
                matched.append(original_input)
        
        missing = []
        for norm_disease, original_disease in disease_normalized.items():
            if norm_disease not in input_normalized:
                missing.append(original_disease)
        
        return matched, missing
    
    
    def calculate_weighted_score(self, matched: List[str], total: int, user_symptoms: List[str]) -> float:
        """
        Calculate weighted confidence score considering symptom severity.
        
        Args:
            matched: List of matched symptoms
            total: Total symptoms for the disease
            user_symptoms: All user-provided symptoms
            
        Returns:
            Weighted confidence score (0.0 to 1.0)
        """
        if total == 0:
            return 0.0
        
        # Base score from match ratio
        base_score = len(matched) / total
        
        # Severity weighting (if available)
        if self.severity_dict:
            matched_severity = sum(self.severity_dict.get(s, 1) for s in matched)
            total_severity = sum(self.severity_dict.get(s, 1) for s in user_symptoms)
            
            if total_severity > 0:
                severity_ratio = matched_severity / total_severity
                # Blend base score with severity ratio (70% base, 30% severity)
                weighted_score = (base_score * 0.7) + (severity_ratio * 0.3)
                return min(weighted_score, 1.0)
        
        return base_score
    
    
    # -----------------------------
    # MAIN PREDICTION
    # -----------------------------
    
    def predict(self, user_symptom_text: str) -> Dict:
        """
        Predict most likely condition based on user symptoms.
        
        Args:
            user_symptom_text: Raw comma-separated symptom string
            
        Returns:
            Dictionary containing:
                - disease: Most likely condition name
                - confidence: Match confidence (0.0 to 1.0)
                - matched: List of matched symptoms
                - missing: List of other symptoms for this condition
                - description: Condition description
                - precautions: List of recommended precautions
                - severity_score: Overall severity estimate
        """
        # Input validation
        if not user_symptom_text or not user_symptom_text.strip():
            return self._create_error_response("No symptoms provided")
        
        # Normalize input symptoms
        try:
            user_symptoms = self.normalize(user_symptom_text)
        except Exception as e:
            logger.error(f"Error normalizing symptoms: {e}")
            return self._create_error_response("Error processing symptoms")
        
        if not user_symptoms:
            return self._create_error_response("No valid symptoms found after processing")
        
        # Find best matching disease
        best_disease = None
        best_score = 0.0
        best_matched = []
        best_missing = []
        
        try:
            # Use cached disease data for faster iteration
            for disease, disease_symptoms in self._disease_cache.items():
                if not disease_symptoms:
                    continue
                
                matched, missing = self.match_symptoms(user_symptoms, disease_symptoms)
                
                # Calculate weighted score
                score = self.calculate_weighted_score(matched, len(disease_symptoms), user_symptoms)
                
                # Update best match
                if score > best_score:
                    best_score = score
                    best_disease = disease
                    best_matched = matched
                    best_missing = missing
        
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return self._create_error_response("Error analyzing symptoms")
        
        # Handle no match
        if best_disease is None or best_score == 0:
            return self._create_no_match_response(user_symptoms)
        
        # Get additional information
        description = self.desc_dict.get(
            best_disease,
            "No detailed description available for this condition."
        )
        
        precautions = self.prec_dict.get(
            best_disease,
            [
                "Monitor your symptoms carefully",
                "Stay well hydrated",
                "Get adequate rest",
                "Consult a healthcare professional if symptoms persist or worsen"
            ]
        )
        
        # Calculate severity score
        severity_score = self._calculate_severity_score(best_matched)
        
        return {
            "disease": best_disease,
            "confidence": round(best_score, 3),
            "matched": best_matched,
            "missing": best_missing[:10],  # Limit to top 10 missing symptoms
            "description": description,
            "precautions": precautions,
            "severity_score": severity_score,
            "total_user_symptoms": len(user_symptoms),
            "unmatched_user_symptoms": [s for s in user_symptoms if s not in best_matched]
        }
    
    
    def _calculate_severity_score(self, symptoms: List[str]) -> str:
        """
        Calculate overall severity based on matched symptoms.
        
        Args:
            symptoms: List of matched symptoms
            
        Returns:
            Severity category: "Low", "Moderate", "High", or "Unknown"
        """
        if not symptoms or not self.severity_dict:
            return "Unknown"
        
        severities = [self.severity_dict.get(s, 0) for s in symptoms]
        
        if not severities or max(severities) == 0:
            return "Unknown"
        
        avg_severity = sum(severities) / len(severities)
        max_severity = max(severities)
        
        # Classification based on average and max
        if max_severity >= 6 or avg_severity >= 5:
            return "High"
        elif max_severity >= 4 or avg_severity >= 3:
            return "Moderate"
        else:
            return "Low"
    
    
    def _create_error_response(self, message: str) -> Dict:
        """Create standardized error response"""
        return {
            "disease": "Error",
            "confidence": 0.0,
            "matched": [],
            "missing": [],
            "description": message,
            "precautions": ["Please consult a healthcare professional"],
            "severity_score": "Unknown",
            "total_user_symptoms": 0,
            "unmatched_user_symptoms": []
        }
    
    
    def _create_no_match_response(self, user_symptoms: List[str]) -> Dict:
        """Create response when no disease matches"""
        return {
            "disease": "Unknown Condition",
            "confidence": 0.0,
            "matched": [],
            "missing": [],
            "description": (
                "Your symptoms don't match our database patterns. "
                "This could mean:\n"
                "• Your symptoms are too general\n"
                "• You may have a rare condition\n"
                "• Symptoms need more specific description\n\n"
                "Please consult a healthcare professional for proper evaluation."
            ),
            "precautions": [
                "Consult a doctor for proper diagnosis",
                "Monitor your symptoms closely",
                "Note any changes or new symptoms",
                "Seek immediate care if symptoms worsen"
            ],
            "severity_score": "Unknown",
            "total_user_symptoms": len(user_symptoms),
            "unmatched_user_symptoms": user_symptoms
        }
    
    
    # -----------------------------
    # UTILITY METHODS
    # -----------------------------
    
    def get_all_diseases(self) -> List[str]:
        """Get list of all diseases in the database"""
        return list(self._disease_cache.keys())
    
    
    def get_disease_info(self, disease: str) -> Optional[Dict]:
        """
        Get detailed information about a specific disease.
        
        Args:
            disease: Disease name
            
        Returns:
            Dictionary with disease information or None if not found
        """
        if disease not in self._disease_cache:
            return None
        
        return {
            "disease": disease,
            "symptoms": self._disease_cache[disease],
            "description": self.desc_dict.get(disease, "No description available"),
            "precautions": self.prec_dict.get(disease, []),
            "symptom_count": len(self._disease_cache[disease])
        }
    
    
    def validate_health(self) -> Dict[str, bool]:
        """
        Validate that all required data is loaded correctly.
        
        Returns:
            Dictionary with validation results
        """
        return {
            "symptom_data_loaded": self.symptom_data is not None,
            "descriptions_loaded": len(self.desc_dict) > 0,
            "precautions_loaded": len(self.prec_dict) > 0,
            "severity_loaded": len(self.severity_dict) > 0,
            "synonyms_loaded": len(self.synonyms) > 0,
            "cache_built": len(self._disease_cache) > 0
        }