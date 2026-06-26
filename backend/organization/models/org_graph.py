from typing import List, Dict, Any, Optional
from graph.memory_graph_store import MemoryGraphStore
from graph.graph_models import Node, Relationship

class OrganizationGraph(MemoryGraphStore):
    """
    Manages the organizational intelligence graph.
    Inherits from MemoryGraphStore to integrate cleanly with the existing Graph API.
    """
    def __init__(self):
        super().__init__()
        self._initialize_mock_data()

    def _initialize_mock_data(self):
        # 1. Define Nodes (Entities)
        # Category: People
        self.add_node("Alice", "Person", {"name": "Alice Smith", "role": "Principal AI Researcher", "val": 25, "status": "Active"})
        self.add_node("Bob", "Person", {"name": "Bob Jones", "role": "Senior Frontend Engineer", "val": 22, "status": "Active"})
        self.add_node("Charlie", "Person", {"name": "Charlie Brown", "role": "DevOps Architect", "val": 20, "status": "Active"})
        self.add_node("Diana", "Person", {"name": "Diana Prince", "role": "Product Manager", "val": 21, "status": "Active"})
        self.add_node("Ethan", "Person", {"name": "Ethan Hunt", "role": "Junior ML Engineer", "val": 15, "status": "Active"})
        self.add_node("Fiona", "Person", {"name": "Fiona Gallagher", "role": "Tech Writer", "val": 16, "status": "Active"})

        # Category: Teams
        self.add_node("AI_Core_Team", "Team", {"name": "AI Core Team", "lead": "Alice", "val": 24})
        self.add_node("Frontend_Team", "Team", {"name": "Frontend Team", "lead": "Bob", "val": 22})
        self.add_node("Platform_Ops_Team", "Team", {"name": "Platform & Ops Team", "lead": "Charlie", "val": 20})

        # Category: Departments
        self.add_node("Engineering_Dept", "Department", {"name": "Engineering Department", "head": "Alice", "val": 28})
        self.add_node("Product_Dept", "Department", {"name": "Product Department", "head": "Diana", "val": 24})

        # Category: Projects
        self.add_node("Project_Chidakara", "Project", {"name": "Project Chidakara", "status": "Active", "priority": "High", "val": 26})
        self.add_node("Project_Web_Console", "Project", {"name": "Project Web Console", "status": "Active", "priority": "Medium", "val": 22})
        self.add_node("Project_Data_Pipeline", "Project", {"name": "Project Data Pipeline", "status": "Blocked", "priority": "High", "val": 20})
        self.add_node("Project_Legacy_Sync", "Project", {"name": "Project Legacy Sync", "status": "Inactive", "priority": "Low", "val": 14})

        # Category: Tasks
        self.add_node("Task_Optimize_CUDA", "Task", {"name": "Optimize CUDA Kernels", "status": "In_Progress", "val": 18})
        self.add_node("Task_Design_Console", "Task", {"name": "Design Platform Dashboard", "status": "Completed", "val": 15})
        self.add_node("Task_Setup_CI_CD", "Task", {"name": "Configure Devops CI/CD", "status": "In_Progress", "val": 16})
        self.add_node("Task_Implement_Go_Scheduler", "Task", {"name": "Implement Go Scheduler", "status": "Blocked", "val": 18}) # Blocked: no Go skills

        # Category: Documents
        self.add_node("Doc_Arch_Spec_v3", "Document", {"name": "Architecture Spec v3", "version": "3.0", "status": "Up_To_Date", "val": 18})
        self.add_node("Doc_UI_Guidelines", "Document", {"name": "UI Brand Guidelines", "version": "1.2", "status": "Up_To_Date", "val": 15})
        self.add_node("Doc_CUDA_11_Setup", "Document", {"name": "CUDA 11.2 Setup Doc", "version": "1.0", "status": "Outdated", "val": 14}) # Outdated
        self.add_node("Doc_UI_Guidelines_Copy", "Document", {"name": "UI Guidelines (Copy)", "version": "1.2", "status": "Duplicate", "val": 12}) # Duplicate of UI Brand Guidelines
        self.add_node("Doc_Security_Policy", "Document", {"name": "Corporate Security Policy 2026", "version": "2.1", "status": "Up_To_Date", "val": 19})

        # Category: Meetings
        self.add_node("Meeting_Daily_Standup", "Meeting", {"name": "Daily Engineering Standup", "frequency": "Daily", "val": 16})
        self.add_node("Meeting_Arch_Review", "Meeting", {"name": "Chidakara Architecture Review", "frequency": "Weekly", "val": 18})

        # Category: Skills
        self.add_node("Skill_CUDA", "Skill", {"name": "CUDA Programming", "val": 22})
        self.add_node("Skill_Python", "Skill", {"name": "Python Language", "val": 20})
        self.add_node("Skill_React", "Skill", {"name": "React Framework", "val": 18})
        self.add_node("Skill_TypeScript", "Skill", {"name": "TypeScript", "val": 18})
        self.add_node("Skill_Go", "Skill", {"name": "Go Language", "val": 20})
        self.add_node("Skill_Docker", "Skill", {"name": "Docker & Containerization", "val": 18})

        # Category: Technologies
        self.add_node("Tech_CUDA_12", "Technology", {"name": "CUDA 12.8", "version": "12.8", "status": "Stable", "val": 20})
        self.add_node("Tech_CUDA_11", "Technology", {"name": "CUDA 11.2", "version": "11.2", "status": "Obsolete", "val": 16}) # Obsolete
        self.add_node("Tech_Python_3", "Technology", {"name": "Python 3.11", "version": "3.11", "status": "Stable", "val": 20})
        self.add_node("Tech_Go_Lang", "Technology", {"name": "Go Language", "version": "1.21", "status": "Stable", "val": 18})
        self.add_node("Tech_React_18", "Technology", {"name": "React 18", "version": "18.2", "status": "Stable", "val": 18})
        self.add_node("Tech_Next_JS", "Technology", {"name": "Next.js 14", "version": "14.1", "status": "Stable", "val": 18})

        # Category: Repositories
        self.add_node("Repo_Chidakara_AI", "Repository", {"name": "chidakara-ai", "status": "Active", "val": 24})
        self.add_node("Repo_Chidakara_Website", "Repository", {"name": "chidakara-website", "status": "Active", "val": 22})
        self.add_node("Repo_Legacy_Sync_Tool", "Repository", {"name": "legacy-sync-tool", "status": "Archived", "val": 14})

        # Category: Policies
        self.add_node("Policy_Remote_Work", "Policy", {"name": "Remote Work Policy", "status": "Active", "val": 16}) # Disconnected Node
        self.add_node("Policy_Open_Source", "Policy", {"name": "Open Source Contribution Policy", "status": "Active", "val": 17})

        # Category: Products
        self.add_node("Prod_Chidakara_OS", "Product", {"name": "Chidakara Enterprise AI OS", "status": "Beta", "val": 26})

        # Category: Customers
        self.add_node("Cust_Acme_Corp", "Customer", {"name": "Acme Corp", "val": 24})
        self.add_node("Cust_Globex", "Customer", {"name": "Globex Corporation", "val": 22})

        # Category: Vendors
        self.add_node("Vend_Nvidia", "Vendor", {"name": "Nvidia Corporation", "val": 20})
        self.add_node("Vend_OpenAI", "Vendor", {"name": "OpenAI LP", "val": 20})


        # 2. Define Edges (Relationships)
        # Person -> Works On -> Project
        self.add_edge("Alice", "Project_Chidakara", "WORKS_ON")
        self.add_edge("Bob", "Project_Web_Console", "WORKS_ON")
        self.add_edge("Charlie", "Project_Data_Pipeline", "WORKS_ON")
        self.add_edge("Ethan", "Project_Chidakara", "WORKS_ON")

        # Person -> Part Of -> Team (Derived relationship)
        self.add_edge("Alice", "AI_Core_Team", "PART_OF")
        self.add_edge("Ethan", "AI_Core_Team", "PART_OF")
        self.add_edge("Bob", "Frontend_Team", "PART_OF")
        self.add_edge("Charlie", "Platform_Ops_Team", "PART_OF")

        # Team -> Belong To -> Department
        self.add_edge("AI_Core_Team", "Engineering_Dept", "BELONG_TO")
        self.add_edge("Frontend_Team", "Engineering_Dept", "BELONG_TO")
        self.add_edge("Platform_Ops_Team", "Engineering_Dept", "BELONG_TO")

        # Person -> Possesses -> Skill
        self.add_edge("Alice", "Skill_CUDA", "POSSESSES")
        self.add_edge("Alice", "Skill_Python", "POSSESSES")
        self.add_edge("Bob", "Skill_React", "POSSESSES")
        self.add_edge("Bob", "Skill_TypeScript", "POSSESSES")
        self.add_edge("Charlie", "Skill_Docker", "POSSESSES")
        self.add_edge("Charlie", "Skill_Python", "POSSESSES")
        self.add_edge("Ethan", "Skill_Python", "POSSESSES")

        # Project -> Uses -> Technology
        self.add_edge("Project_Chidakara", "Tech_CUDA_12", "USES")
        self.add_edge("Project_Chidakara", "Tech_Python_3", "USES")
        self.add_edge("Project_Web_Console", "Tech_React_18", "USES")
        self.add_edge("Project_Web_Console", "Tech_Next_JS", "USES")
        self.add_edge("Project_Data_Pipeline", "Tech_Go_Lang", "USES")
        self.add_edge("Project_Legacy_Sync", "Tech_CUDA_11", "USES") # Obsolete

        # Technology -> Depends On -> Technology
        self.add_edge("Tech_Next_JS", "Tech_React_18", "DEPENDS_ON")
        self.add_edge("Tech_CUDA_12", "Tech_CUDA_11", "DEPENDS_ON") # Upgraded dependency chain

        # Project -> Generates -> Document
        self.add_edge("Project_Chidakara", "Doc_Arch_Spec_v3", "GENERATES")
        self.add_edge("Project_Web_Console", "Doc_UI_Guidelines", "GENERATES")
        self.add_edge("Project_Legacy_Sync", "Doc_CUDA_11_Setup", "GENERATES")

        # Department -> Owns -> Project
        self.add_edge("Engineering_Dept", "Project_Chidakara", "OWNS")
        self.add_edge("Engineering_Dept", "Project_Web_Console", "OWNS")
        self.add_edge("Engineering_Dept", "Project_Data_Pipeline", "OWNS")
        self.add_edge("Product_Dept", "Project_Web_Console", "OWNS")

        # Task -> Assigned To -> Person
        self.add_edge("Task_Optimize_CUDA", "Alice", "ASSIGNED_TO")
        self.add_edge("Task_Design_Console", "Bob", "ASSIGNED_TO")
        self.add_edge("Task_Setup_CI_CD", "Charlie", "ASSIGNED_TO")
        self.add_edge("Task_Implement_Go_Scheduler", "Ethan", "ASSIGNED_TO") # Ethan has no Go skill

        # Task -> Part Of -> Project (Optional Helper)
        self.add_edge("Task_Optimize_CUDA", "Project_Chidakara", "PART_OF")
        self.add_edge("Task_Design_Console", "Project_Web_Console", "PART_OF")
        self.add_edge("Task_Setup_CI_CD", "Project_Data_Pipeline", "PART_OF")
        self.add_edge("Task_Implement_Go_Scheduler", "Project_Data_Pipeline", "PART_OF")

        # Meeting -> Discusses -> Project
        self.add_edge("Meeting_Daily_Standup", "Project_Chidakara", "DISCUSSES")
        self.add_edge("Meeting_Arch_Review", "Project_Chidakara", "DISCUSSES")

        # Document -> References -> Document
        self.add_edge("Doc_Arch_Spec_v3", "Doc_Security_Policy", "REFERENCES")
        self.add_edge("Doc_UI_Guidelines_Copy", "Doc_UI_Guidelines", "REFERENCES") # Duplicate references main

        # Policy -> Applies To -> Department
        self.add_edge("Policy_Open_Source", "Engineering_Dept", "APPLIES_TO")

        # Skill -> Required By -> Project
        self.add_edge("Skill_CUDA", "Project_Chidakara", "REQUIRED_BY")
        self.add_edge("Skill_Python", "Project_Chidakara", "REQUIRED_BY")
        self.add_edge("Skill_React", "Project_Web_Console", "REQUIRED_BY")
        self.add_edge("Skill_TypeScript", "Project_Web_Console", "REQUIRED_BY")
        self.add_edge("Skill_Go", "Project_Data_Pipeline", "REQUIRED_BY")

        # Project -> Part Of -> Product
        self.add_edge("Project_Chidakara", "Prod_Chidakara_OS", "PART_OF")
        self.add_edge("Project_Web_Console", "Prod_Chidakara_OS", "PART_OF")

        # Product -> Sold To -> Customer
        self.add_edge("Prod_Chidakara_OS", "Cust_Acme_Corp", "SOLD_TO")
        self.add_edge("Prod_Chidakara_OS", "Cust_Globex", "SOLD_TO")

        # Vendor -> Supplies -> Technology
        self.add_edge("Vend_Nvidia", "Tech_CUDA_12", "SUPPLIES")
        self.add_edge("Vend_OpenAI", "Tech_Python_3", "SUPPLIES")

# Single global instance of the Org Graph
org_graph_instance = OrganizationGraph()
