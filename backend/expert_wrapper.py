import os
import sys
from io import StringIO
import contextlib
from .medical_expert_system import MedicalExpertSystem

class ExpertWrapper:
    def __init__(self, knowledge_base_path):
        self.knowledge_base_path = os.path.abspath(knowledge_base_path)
        self.expert_system = MedicalExpertSystem(self.knowledge_base_path)
        
    def get_all_symptoms(self):
        """Get all symptoms in display format"""
        return self.expert_system.get_all_symptoms_display()
    
    def get_all_diseases(self):
        """Get all diseases"""
        return sorted(self.expert_system.diseases.keys())
    
    def diagnose(self, symptoms):
        """Perform diagnosis on given symptoms"""
        return self.expert_system.diagnose(symptoms)
    
    def get_disease_info(self, disease_name):
        """Get detailed disease information"""
        return self.expert_system.get_disease_info(disease_name)
    
    def search_symptoms(self, query):
        """Search symptoms matching query"""
        query = query.lower()
        return [s for s in self.expert_system.display_symptoms if query in s.lower()]