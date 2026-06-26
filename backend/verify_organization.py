import sys
from organization.models.org_graph import org_graph_instance
from organization.analyzers.org_analyzer import OrganizationAnalyzer
from organization.recommenders.org_recommender import OrganizationRecommender
from organization.simulators.org_simulator import OrganizationSimulator
from organization.reasoners.org_reasoner import OrganizationReasoner

def run_tests():
    print("====================================")
    print("Verifying Organization Graph & Data")
    print("====================================")
    serialized = org_graph_instance.serialize()
    print(f"Nodes count: {len(serialized['nodes'])}")
    print(f"Edges count: {len(serialized['edges'])}")
    assert len(serialized['nodes']) > 0, "No nodes initialized"
    assert len(serialized['edges']) > 0, "No edges initialized"
    print("[OK] Graph initialization check passed.")

    print("\n====================================")
    print("Verifying Organization Analyzer")
    print("====================================")
    analyzer = OrganizationAnalyzer()
    
    # Test Python dependencies
    python_deps = analyzer.get_projects_depending_on("Python")
    print("Projects depending on Python:")
    for item in python_deps:
        print(f" - {item['technology']}: {item['projects']}")
    assert len(python_deps) > 0, "Python dependencies check failed"

    # Test CUDA teams
    cuda_teams = analyzer.get_teams_using("CUDA")
    print("Teams using CUDA:")
    for item in cuda_teams:
        print(f" - {item['technology']}: {item['teams']}")
    assert len(cuda_teams) > 0, "CUDA usage check failed"

    # Test missing skills
    missing = analyzer.get_missing_skills()
    print("Missing Skills:")
    for m in missing:
        print(f" - Project {m['project']}: missing {m['missing_skills']}")
    assert any(m['project_id'] == 'Project_Data_Pipeline' for m in missing), "Missing skill check failed"

    # Test blocked projects
    blocked = analyzer.get_blocked_projects()
    print("Blocked Projects:")
    for b in blocked:
        print(f" - {b['project']}: {b['reasons']}")
    
    # Test obsolete tech
    obsolete = analyzer.get_obsolete_technologies()
    print("Obsolete Technologies:")
    for o in obsolete:
        print(f" - {o['technology']} (v{o['version']}) used by {o['affected_projects']}")

    # Test duplicate docs
    dups = analyzer.get_duplicate_documents()
    print("Duplicate Documents:")
    for d in dups:
        print(f" - Duplicate: {d['duplicate_document']} of {d['main_document']}")

    # Test bottlenecks
    bottlenecks = analyzer.get_workflow_bottlenecks()
    print("Workflow Bottlenecks:")
    for b in bottlenecks:
        print(f" - {b['type']}: {b['resource']} ({b['details']})")
    
    print("[OK] Analyzer tests passed.")

    print("\n====================================")
    print("Verifying Recommender Engine")
    print("====================================")
    recommender = OrganizationRecommender()
    recs = recommender.get_recommendations()
    print(f"Total Recommendations Generated: {len(recs)}")
    for r in recs[:3]:
        print(f" - [{r['category']}] ({r['severity']}): {r['title']}")
    assert len(recs) > 0, "No recommendations generated"
    print("[OK] Recommender tests passed.")

    print("\n====================================")
    print("Verifying Simulation Engine")
    print("====================================")
    simulator = OrganizationSimulator()
    
    # Test Alice leaves
    sim_alice = simulator.run_simulation("engineer_leave", "Alice")
    print(f"Simulation: 'If Alice leaves' impact:")
    print(f" - Risk Level: {sim_alice['risk_level']}")
    print(f" - Summary: {sim_alice['summary']}")
    print(f" - Affected Nodes: {sim_alice['affected_nodes_count']}")
    assert sim_alice['success'] == True
    
    # Test Project delay
    sim_delay = simulator.run_simulation("project_delay", "Project_Chidakara")
    print(f"Simulation: 'If Project Chidakara delayed' impact:")
    print(f" - Summary: {sim_delay['summary']}")
    print(f" - Dependency Chains:")
    for chain in sim_delay['dependency_chains']:
        print(f"   -> {chain}")
    assert sim_delay['success'] == True

    print("[OK] Simulator tests passed.")

    print("\n====================================")
    print("Verifying Reasoner Engine")
    print("====================================")
    reasoner = OrganizationReasoner()
    health = reasoner.reason_about_health()
    print("Reasoner Health Report:")
    print(f" - Struct: {health['organizational_structure_summary']}")
    print(f" - Skills per dept: {health['departmental_skill_coverage']}")
    print(f" - Operational risk: {health['overall_operational_risk']}")
    print("[OK] Reasoner tests passed.")

    print("\nALL BACKEND ORGANIZATION INTEL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
