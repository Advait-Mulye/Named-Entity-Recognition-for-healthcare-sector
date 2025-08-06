import re
import json
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Entity:
    """Represents a named entity with its properties."""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0

class MedicalNER:
    """Medical Named Entity Recognition system."""
    
    def __init__(self):
        """Initialize the Medical NER system with predefined medical vocabularies."""
        self.entity_types = {
            'DISEASE': self._load_diseases(),
            'MEDICATION': self._load_medications(),
            'SYMPTOM': self._load_symptoms(),
            'BODY_PART': self._load_body_parts(),
            'PROCEDURE': self._load_procedures(),
            'TEST': self._load_tests(),
            'DOSAGE': self._load_dosage_patterns()
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = self._compile_patterns()
        
    def _load_diseases(self) -> Set[str]:
        """Load disease vocabulary."""
        diseases = {
            'diabetes', 'hypertension', 'cancer', 'asthma', 'pneumonia',
            'bronchitis', 'arthritis', 'influenza', 'tuberculosis', 'malaria',
            'covid-19', 'coronavirus', 'migraine', 'depression', 'anxiety',
            'schizophrenia', 'alzheimer', 'parkinson', 'stroke', 'heart attack',
            'myocardial infarction', 'angina', 'epilepsy', 'seizure', 'lupus',
            'hepatitis', 'cirrhosis', 'kidney disease', 'renal failure',
            'liver disease', 'gallstones', 'appendicitis', 'gastritis',
            'ulcer', 'ibs', 'irritable bowel syndrome', 'crohn disease',
            'celiac disease', 'anemia', 'leukemia', 'lymphoma', 'melanoma',
            'osteoporosis', 'fibromyalgia', 'gout', 'thyroid disease',
            'hyperthyroidism', 'hypothyroidism', 'diabetes type 1',
            'diabetes type 2', 'gestational diabetes', 'copd',
            'chronic obstructive pulmonary disease', 'emphysema'
        }
        return diseases
    
    def _load_medications(self) -> Set[str]:
        """Load medication vocabulary."""
        medications = {
            'aspirin', 'ibuprofen', 'acetaminophen', 'paracetamol', 'morphine',
            'codeine', 'tramadol', 'oxycodone', 'fentanyl', 'metformin',
            'insulin', 'lisinopril', 'amlodipine', 'atorvastatin', 'simvastatin',
            'omeprazole', 'pantoprazole', 'albuterol', 'prednisone', 'warfarin',
            'heparin', 'digoxin', 'furosemide', 'hydrochlorothiazide',
            'levothyroxine', 'synthroid', 'gabapentin', 'pregabalin',
            'sertraline', 'fluoxetine', 'citalopram', 'escitalopram',
            'venlafaxine', 'duloxetine', 'risperidone', 'quetiapine',
            'olanzapine', 'haloperidol', 'lorazepam', 'diazepam',
            'alprazolam', 'clonazepam', 'zolpidem', 'eszopiclone',
            'amoxicillin', 'azithromycin', 'ciprofloxacin', 'doxycycline',
            'penicillin', 'vancomycin', 'cephalexin', 'metronidazole'
        }
        return medications
    
    def _load_symptoms(self) -> Set[str]:
        """Load symptom vocabulary."""
        symptoms = {
            'fever', 'headache', 'nausea', 'vomiting', 'diarrhea', 'constipation',
            'cough', 'sore throat', 'runny nose', 'congestion', 'fatigue',
            'weakness', 'dizziness', 'shortness of breath', 'chest pain',
            'abdominal pain', 'back pain', 'joint pain', 'muscle pain',
            'rash', 'itching', 'swelling', 'inflammation', 'bleeding',
            'bruising', 'numbness', 'tingling', 'vision problems',
            'hearing loss', 'tinnitus', 'difficulty swallowing',
            'loss of appetite', 'weight loss', 'weight gain', 'insomnia',
            'excessive sleepiness', 'confusion', 'memory loss', 'seizures',
            'tremors', 'stiffness', 'palpitations', 'irregular heartbeat',
            'high blood pressure', 'low blood pressure', 'difficulty breathing',
            'wheezing', 'snoring', 'night sweats', 'hot flashes',
            'cold intolerance', 'heat intolerance', 'excessive thirst',
            'frequent urination', 'painful urination', 'blood in urine',
            'constipation', 'loose stools', 'heartburn', 'acid reflux'
        }
        return symptoms
    
    def _load_body_parts(self) -> Set[str]:
        """Load body parts vocabulary."""
        body_parts = {
            'head', 'brain', 'skull', 'face', 'eye', 'eyes', 'ear', 'ears',
            'nose', 'mouth', 'teeth', 'tongue', 'throat', 'neck', 'shoulder',
            'shoulders', 'arm', 'arms', 'elbow', 'elbows', 'wrist', 'wrists',
            'hand', 'hands', 'finger', 'fingers', 'thumb', 'chest', 'breast',
            'breasts', 'lung', 'lungs', 'heart', 'back', 'spine', 'abdomen',
            'stomach', 'liver', 'kidney', 'kidneys', 'bladder', 'intestines',
            'colon', 'rectum', 'hip', 'hips', 'leg', 'legs', 'thigh', 'thighs',
            'knee', 'knees', 'ankle', 'ankles', 'foot', 'feet', 'toe', 'toes',
            'skin', 'muscle', 'muscles', 'bone', 'bones', 'joint', 'joints',
            'blood', 'vein', 'veins', 'artery', 'arteries', 'nerve', 'nerves',
            'thyroid', 'pancreas', 'gallbladder', 'appendix', 'spleen',
            'lymph nodes', 'prostate', 'uterus', 'ovaries', 'testicles'
        }
        return body_parts
    
    def _load_procedures(self) -> Set[str]:
        """Load medical procedures vocabulary."""
        procedures = {
            'surgery', 'operation', 'biopsy', 'endoscopy', 'colonoscopy',
            'mammography', 'ultrasound', 'x-ray', 'ct scan', 'mri',
            'pet scan', 'ecg', 'ekg', 'echocardiogram', 'stress test',
            'blood test', 'urine test', 'physical examination', 'checkup',
            'vaccination', 'immunization', 'injection', 'transfusion',
            'dialysis', 'chemotherapy', 'radiation therapy', 'physical therapy',
            'occupational therapy', 'speech therapy', 'psychotherapy',
            'counseling', 'anesthesia', 'intubation', 'catheterization',
            'suturing', 'wound care', 'bandaging', 'cast application',
            'splinting', 'joint replacement', 'bypass surgery',
            'angioplasty', 'stent placement', 'pacemaker implantation'
        }
        return procedures
    
    def _load_tests(self) -> Set[str]:
        """Load medical tests vocabulary."""
        tests = {
            'complete blood count', 'cbc', 'basic metabolic panel', 'bmp',
            'comprehensive metabolic panel', 'cmp', 'lipid panel',
            'liver function tests', 'kidney function tests', 'thyroid function tests',
            'glucose test', 'hemoglobin a1c', 'psa test', 'cholesterol test',
            'triglycerides test', 'blood pressure measurement', 'pulse oximetry',
            'spirometry', 'pulmonary function tests', 'electrocardiogram',
            'holter monitor', 'event monitor', 'treadmill test',
            'nuclear stress test', 'cardiac catheterization', 'angiogram',
            'bone density scan', 'dexa scan', 'skin test', 'allergy test',
            'culture test', 'sensitivity test', 'pathology report',
            'genetic testing', 'tumor markers', 'inflammatory markers'
        }
        return tests
    
    def _load_dosage_patterns(self) -> List[str]:
        """Load dosage pattern regexes."""
        patterns = [
            r'\b\d+\s*mg\b',
            r'\b\d+\s*mcg\b',
            r'\b\d+\s*g\b',
            r'\b\d+\s*ml\b',
            r'\b\d+\s*units?\b',
            r'\b\d+\s*tablets?\b',
            r'\b\d+\s*capsules?\b',
            r'\b\d+\s*times?\s+(?:a\s+)?day\b',
            r'\b(?:once|twice|thrice)\s+(?:a\s+)?day\b',
            r'\bevery\s+\d+\s+hours?\b',
            r'\b\d+\s*drops?\b'
        ]
        return patterns
    
    def _compile_patterns(self) -> Dict[str, List]:
        """Compile regex patterns for efficient matching."""
        compiled = {}
        
        # Compile word-based patterns for exact matches
        for entity_type, words in self.entity_types.items():
            if entity_type != 'DOSAGE':
                # Create regex patterns for each word/phrase
                patterns = []
                for word in words:
                    # Handle multi-word phrases
                    escaped_word = re.escape(word)
                    pattern = r'\b' + escaped_word + r'\b'
                    patterns.append(re.compile(pattern, re.IGNORECASE))
                compiled[entity_type] = patterns
        
        # Compile dosage patterns
        compiled['DOSAGE'] = [re.compile(pattern, re.IGNORECASE) 
                             for pattern in self.entity_types['DOSAGE']]
        
        return compiled
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract all medical entities from the given text."""
        entities = []
        
        # Extract entities for each type
        for entity_type, patterns in self.compiled_patterns.items():
            entities.extend(self._extract_by_type(text, entity_type, patterns))
        
        # Remove duplicates and overlapping entities
        entities = self._remove_overlaps(entities)
        
        # Sort by start position
        entities.sort(key=lambda x: x.start)
        
        return entities
    
    def _extract_by_type(self, text: str, entity_type: str, patterns: List) -> List[Entity]:
        """Extract entities of a specific type."""
        entities = []
        
        for pattern in patterns:
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    label=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0
                )
                entities.append(entity)
        
        return entities
    
    def _remove_overlaps(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, keeping the longest ones."""
        if not entities:
            return entities
        
        # Sort by start position, then by length (descending)
        entities.sort(key=lambda x: (x.start, -(x.end - x.start)))
        
        filtered = []
        for entity in entities:
            # Check if this entity overlaps with any already accepted entity
            overlaps = False
            for accepted in filtered:
                if (entity.start < accepted.end and entity.end > accepted.start):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered.append(entity)
        
        return filtered
    
    def annotate_text(self, text: str) -> str:
        """Annotate text with entity labels."""
        entities = self.extract_entities(text)
        
        if not entities:
            return text
        
        # Sort entities by start position in reverse order
        entities.sort(key=lambda x: x.start, reverse=True)
        
        annotated_text = text
        for entity in entities:
            annotation = f"[{entity.text}|{entity.label}]"
            annotated_text = (annotated_text[:entity.start] + 
                            annotation + 
                            annotated_text[entity.end:])
        
        return annotated_text
    
    def get_entity_summary(self, text: str) -> Dict[str, List[str]]:
        """Get a summary of entities grouped by type."""
        entities = self.extract_entities(text)
        
        summary = defaultdict(list)
        for entity in entities:
            if entity.text not in summary[entity.label]:
                summary[entity.label].append(entity.text)
        
        return dict(summary)

def main():
    """Main function to run the Medical NER system interactively."""
    print("=" * 60)
    print("    Medical Named Entity Recognition System")
    print("=" * 60)
    print("\nThis system can identify the following medical entities:")
    print("• DISEASE - Medical conditions and diseases")
    print("• MEDICATION - Drugs and medications")
    print("• SYMPTOM - Signs and symptoms")
    print("• BODY_PART - Anatomical parts")
    print("• PROCEDURE - Medical procedures")
    print("• TEST - Medical tests and examinations")
    print("• DOSAGE - Medication dosages and frequencies")
    print("\nType 'quit' or 'exit' to stop the program.")
    print("-" * 60)
    
    # Initialize the NER system
    ner = MedicalNER()
    
    while True:
        try:
            # Get user input
            user_input = input("\nEnter medical text to analyze: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Thank you for using Medical NER System!")
                break
            
            if not user_input:
                print("Please enter some text to analyze.")
                continue
            
            print(f"\nAnalyzing: '{user_input}'")
            print("-" * 40)
            
            # Extract entities
            entities = ner.extract_entities(user_input)
            
            if entities:
                print(f"Found {len(entities)} medical entities:")
                print()
                
                for i, entity in enumerate(entities, 1):
                    print(f"{i:2d}. {entity.text:<20} [{entity.label}]")
                
                print(f"\nAnnotated text:")
                print(ner.annotate_text(user_input))
                
                print(f"\nEntity Summary:")
                summary = ner.get_entity_summary(user_input)
                for entity_type, entities_list in summary.items():
                    print(f"  {entity_type}: {', '.join(entities_list)}")
                    
            else:
                print("No medical entities found in the text.")
        
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()