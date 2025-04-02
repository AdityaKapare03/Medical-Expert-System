# disease_expert_system.py
import json
import os
from collections import Counter

class MedicalExpertSystem:
    def __init__(self, knowledge_base_path):
        """Initialize the expert system with the knowledge base."""
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.diseases = self.knowledge_base.get("diseases", {})
        self.symptom_severity = self.knowledge_base.get("symptom_severity", {})
        self.all_symptoms = list(self.symptom_severity.keys())
        self.user_friendly_symptoms = {self.format_symptom_for_display(s): s for s in self.all_symptoms}
        self.display_symptoms = list(self.user_friendly_symptoms.keys())
    
    def load_knowledge_base(self, file_path):
        """Load the knowledge base from a JSON file."""
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: Knowledge base file '{file_path}' not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{file_path}'.")
            return {}
    
    def format_symptom_for_display(self, symptom):
        """Convert internal symptom format to user-friendly display format."""
        return symptom.replace('_', ' ').title()
    
    def get_internal_symptom(self, display_symptom):
        """Convert user-friendly symptom back to internal format."""
        return self.user_friendly_symptoms.get(display_symptom)
    
    def get_all_symptoms_display(self):
        """Return a list of all symptoms in user-friendly format."""
        return self.display_symptoms
    
    def diagnose(self, user_symptoms_display):
        """
        Diagnose potential diseases based on user symptoms.
        Takes user-friendly symptom names and converts them to internal format.
        Returns a list of (disease, confidence) tuples sorted by confidence.
        """
        if not user_symptoms_display:
            return []
        user_symptoms = []
        for display_symptom in user_symptoms_display:
            internal_symptom = self.get_internal_symptom(display_symptom)
            if internal_symptom:
                user_symptoms.append(internal_symptom)
        user_symptoms_set = set(user_symptoms)
        disease_scores = []
        for disease_name, disease_info in self.diseases.items():
            symptom_patterns = disease_info.get("symptom_patterns", [])
            best_match_score = 0
            for pattern in symptom_patterns:
                pattern_set = set(pattern)
                matched_symptoms = user_symptoms_set.intersection(pattern_set)
                if matched_symptoms:
                    severity_sum = sum(self.symptom_severity.get(s, 1) for s in matched_symptoms)
                    pattern_coverage = len(matched_symptoms) / len(pattern)
                    user_symptoms_coverage = len(matched_symptoms) / len(user_symptoms_set)
                    score = severity_sum * pattern_coverage * user_symptoms_coverage
                    best_match_score = max(best_match_score, score)
            if best_match_score > 0:
                disease_scores.append((disease_name, best_match_score, disease_info))
        disease_scores.sort(key=lambda x: x[1], reverse=True)
        return disease_scores
    
    def get_disease_info(self, disease_name):
        """Return detailed information about a specific disease."""
        return self.diseases.get(disease_name, {})

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main function to run the expert system."""
    kb_path = "medical_knowledge.json"
    expert_system = MedicalExpertSystem(kb_path)
    if not expert_system.diseases:
        print("Failed to load the knowledge base. Exiting.")
        return
    while True:
        clear_screen()
        print("=" * 60)
        print("MEDICAL DIAGNOSTIC EXPERT SYSTEM")
        print("=" * 60)
        print("\nMAIN MENU:")
        print("1. Diagnose based on symptoms")
        print("2. Browse symptoms")
        print("3. Browse diseases")
        print("4. Exit")
        choice = input("\nEnter your choice (1-4): ")
        if choice == '1':
            diagnose_symptoms(expert_system)
        elif choice == '2':
            browse_symptoms(expert_system)
        elif choice == '3':
            browse_diseases(expert_system)
        elif choice == '4':
            print("\nThank you for using the Medical Diagnostic Expert System. Goodbye!")
            break
        else:
            input("\nInvalid choice. Press Enter to continue...")

def diagnose_symptoms(expert_system):
    """Function to handle the diagnosis process."""
    clear_screen()
    print("=" * 60)
    print("SYMPTOM-BASED DIAGNOSIS")
    print("=" * 60)
    print("\nEnter your symptoms (type 'done' when finished):")
    print("Hint: Type 'list' to see all available symptoms")
    user_symptoms = []
    while True:
        symptom_input = input("> ").strip()
        if symptom_input.lower() == 'done':
            break
        elif symptom_input.lower() == 'list':
            symptoms = expert_system.get_all_symptoms_display()
            for i in range(0, len(symptoms), 3):
                row_symptoms = symptoms[i:i+3]
                print("  ".join(f"{s}" for s in row_symptoms))
            print("\nContinue entering your symptoms:")
        else:
            symptom_input_title = symptom_input.title()
            matching_symptom = None
            if symptom_input_title in expert_system.display_symptoms:
                matching_symptom = symptom_input_title
            else:
                matches = [s for s in expert_system.display_symptoms if symptom_input_title in s]
                if len(matches) == 1:
                    matching_symptom = matches[0]
                elif len(matches) > 1:
                    print(f"Multiple matches found for '{symptom_input}':")
                    for i, match in enumerate(matches[:5], 1):
                        print(f"  {i}. {match}")
                    selection = input("Enter the number of your symptom (or 'none'): ")
                    if selection.isdigit() and 1 <= int(selection) <= len(matches[:5]):
                        matching_symptom = matches[int(selection)-1]
            if matching_symptom:
                if matching_symptom not in user_symptoms:
                    user_symptoms.append(matching_symptom)
                    print(f"Added symptom: {matching_symptom}")
                else:
                    print(f"Symptom '{matching_symptom}' already added.")
            else:
                print(f"Unknown symptom: '{symptom_input}'. Type 'list' to see all symptoms.")
    if not user_symptoms:
        input("\nNo symptoms entered. Press Enter to return to the main menu...")
        return
    print("\nAnalyzing symptoms...")
    diagnoses = expert_system.diagnose(user_symptoms)
    if not diagnoses:
        print("\nNo matching diseases found based on the provided symptoms.")
        input("\nPress Enter to return to the main menu...")
        return
    print("\nPossible diagnoses:")
    print("-" * 60)
    for i, (disease, confidence, info) in enumerate(diagnoses[:5], 1):
        confidence_percent = min(int(confidence * 10), 100)
        print(f"{i}. {disease} (Confidence: {confidence_percent}%)")
    while True:
        selection = input("\nEnter the number for more details (or 'back' to return): ")
        if selection.lower() == 'back':
            break
        try:
            selection_idx = int(selection) - 1
            if 0 <= selection_idx < len(diagnoses[:5]):
                disease_name = diagnoses[selection_idx][0]
                disease_info = diagnoses[selection_idx][2]
                clear_screen()
                print(f"Disease: {disease_name}")
                print("-" * 60)
                print(f"Description: {disease_info.get('description', 'No description available.')}")
                print("\nPrecautions:")
                precautions = disease_info.get('precautions', [])
                if precautions:
                    for i, precaution in enumerate(precautions, 1):
                        print(f"  {i}. {precaution}")
                else:
                    print("  No specific precautions listed.")
                input("\nPress Enter to return to diagnosis results...")
                clear_screen()
                print("Possible diagnoses:")
                print("-" * 60)
                for i, (disease, confidence, info) in enumerate(diagnoses[:5], 1):
                    confidence_percent = min(int(confidence * 10), 100)
                    print(f"{i}. {disease} (Confidence: {confidence_percent}%)")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'back'.")
    input("\nPress Enter to return to the main menu...")

def browse_symptoms(expert_system):
    """Function to browse all symptoms in the system."""
    clear_screen()
    print("=" * 60)
    print("SYMPTOM BROWSER")
    print("=" * 60)
    symptoms_display = expert_system.get_all_symptoms_display()
    symptoms_sorted = sorted(symptoms_display)
    print(f"\nTotal symptoms in database: {len(symptoms_sorted)}")
    print("-" * 60)
    for i, symptom_display in enumerate(symptoms_sorted, 1):
        internal_symptom = expert_system.get_internal_symptom(symptom_display)
        severity = expert_system.symptom_severity.get(internal_symptom, "N/A")
        print(f"{i:3}. {symptom_display} (Severity: {severity})")
        if i % 20 == 0 and i < len(symptoms_sorted):
            input("\nPress Enter to see more symptoms...")
            print()
    input("\nPress Enter to return to the main menu...")

def browse_diseases(expert_system):
    """Function to browse all diseases in the system."""
    clear_screen()
    print("=" * 60)
    print("DISEASE BROWSER")
    print("=" * 60)
    diseases = sorted(expert_system.diseases.keys())
    print(f"\nTotal diseases in database: {len(diseases)}")
    print("-" * 60)
    for i, disease in enumerate(diseases, 1):
        print(f"{i:3}. {disease}")
        if i % 15 == 0 and i < len(diseases):
            input("\nPress Enter to see more diseases...")
            print()
    while True:
        selection = input("\nEnter the number for more details (or 'back' to return): ")
        if selection.lower() == 'back':
            break
        try:
            selection_idx = int(selection) - 1
            if 0 <= selection_idx < len(diseases):
                disease_name = diseases[selection_idx]
                disease_info = expert_system.get_disease_info(disease_name)
                clear_screen()
                print(f"Disease: {disease_name}")
                print("-" * 60)
                print(f"Description: {disease_info.get('description', 'No description available.')}")
                print("\nPrecautions:")
                precautions = disease_info.get('precautions', [])
                if precautions:
                    for i, precaution in enumerate(precautions, 1):
                        print(f"  {i}. {precaution}")
                else:
                    print("  No specific precautions listed.")
                print("\nCommon Symptom Patterns:")
                symptom_patterns = disease_info.get('symptom_patterns', [])
                if symptom_patterns:
                    for i, pattern in enumerate(symptom_patterns[:3], 1):
                        display_pattern = [expert_system.format_symptom_for_display(s) for s in pattern]
                        print(f"  Pattern {i}: {', '.join(display_pattern)}")
                else:
                    print("  No symptom patterns listed.")
                input("\nPress Enter to return to disease list...")
                clear_screen()
                print("DISEASE BROWSER")
                print("-" * 60)
                for i, disease in enumerate(diseases, 1):
                    print(f"{i:3}. {disease}")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'back'.")
    input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()
